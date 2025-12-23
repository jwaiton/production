import os
import logging
import re
from pathlib import Path

from typing import Dict, List

from omegaconf import DictConfig
from omegaconf.errors import ConfigKeyError

from core.immutables import processing_style
from core.io         import prepend_all, quote_strings


def write_jobs(config_names : List,
               global_vars  : DictConfig) -> None:
    '''
    Writes the job files to the correct location
    '''




def extract_globals(cfg : DictConfig) -> Dict:
    global_vars = {}
    if 'global' in cfg:

        for key, val in cfg['global'].items():
            global_vars[key] = val

        # remove from the main config
        cfg.pop('global', None)

    return global_vars


def alter_config(config_text : str, alterations : DictConfig) -> str:
    '''
    take a python config from IC and alter it to match requirements
    '''
    for key, value in alterations.items():
        # nested dictionaries
        if type(value) is DictConfig:
            config_text = alter_config(config_text, value)
        else:
            try:
                config_text = re.sub(rf"^\s*{key}\s*=\s*.*$",
                                     rf"{key} = {value}",
                                     config_text,
                                     flags = re.MULTILINE)
            except Exception as e:
                logging.error(f"Couldn't alter config for key value pair: {key}, {value}\n {e}")
    return config_text




def write_configs(input_names : List, output_names : List, config_names : [List], config : DictConfig, global_vars : Dict) -> None:
    '''
    write out the config files
    '''
    match global_vars['processing_style']:
        case 'LDC':
            for i in range(global_vars['LDCs']):
                for i_names, o_names, c_names in zip(input_names[i], output_names[i], config_names[i]):
                    conf_dict = {'file_out' : o_names, 'files_in' : i_names}
                    print('conf_dict')
                    print(conf_dict)
                    local_config = alter_config(config, conf_dict)
                    # write it to the file
                    with open(c_names, 'w') as f:
                        f.write(local_config)
        case 'FOLDER':
            print('folders not been set up yet')
        case 'FILE':
            print('files not been set up yet')
        case _:
            print('something else (fuck up)')

    '''
    # for each config name and output_name, write a config
    for o_names, c_names in zip(output_names, config_names):
        conf_dict = {'file_out' : o_names}
        print(config)
        print('='*20)
        local_config = alter_config(config, conf_dict)
        print(local_config)
        exit()
    '''


def collect_input_names(global_vars : Dict,
                        cfg : DictConfig) -> List:
    '''
    using the provided information, ascertains input names
    assuming data is not from the work-chain
    '''

    path = f"{cfg['pre_path']}{cfg['run_number']}/{cfg['post_path']}"


    all_inputs = []

    match global_vars['processing_style']:
        case 'LDC':
            for i in range(global_vars['LDCs']):
                full_path = f"{path}ldc{i+1}/"
                all_inputs.append([f"'{os.path.join(full_path, f)}'" for f in os.listdir(full_path) if f.endswith('.h5')])
                # stupid ' " stuff to retain stringness in configs

        case 'FOLDER':
            print('folders not been set up yet')
        case 'FILE':
            print('files not been set up yet')
        case _:
            print('something else (fuck up)')


    return all_inputs


def extract_output_names(global_vars : Dict,
                         cfg         : DictConfig,
                         input_names : List) -> List:
    '''
    provided with an input file, create the corresponding output file
    this assumes the structure of:

    executable_runnumber_number_whateverelse.h5

    breaks otherwise
    '''

    data_path = f"{global_vars['global_path']}{global_vars['tag']}/data/{cfg['city']}/{cfg['run_number']}/"
    conf_path = f"{global_vars['global_path']}{global_vars['tag']}/configs/{cfg['city']}/{cfg['run_number']}/"

    output_files = []
    config_files = []
    match global_vars['processing_style']:
        case 'LDC':
            for i in range(global_vars['LDCs']):
                LDC_files  = input_names[i]
                file_names = [f.split('/')[-1] for f in LDC_files]
                # generate them based on the number
                numbers    = [f.split('_')[2] for f in file_names]

                output_files.append([f"ldc{i+1}/{cfg['city']}_{cfg['run_number']}_{n}_ldc{i+1}_{global_vars['tag']}.h5" for n in numbers])
                config_files.append([f"ldc{i+1}/{cfg['city']}_{cfg['run_number']}_{n}_ldc{i+1}_{global_vars['tag']}.conf" for n in numbers])
        case 'FOLDER':
            print('folders not been set up yet')
        case 'FILE':
            print('files not been set up yet')
        case _:
            print('something else (fuck up)')

    output_files = prepend_all(output_files, data_path)
    # wrap the output files in '' for formatting
    output_files = quote_strings(output_files)
    config_files = prepend_all(config_files, conf_path)
    return output_files, config_files


def generate_folder_structure(global_vars : Dict,
                              cfg : DictConfig) -> tuple[Path, Path, Path]:
    '''
    generate folder structure based on global_vars and cfg
    '''
    # create config location
    specific_config_path = os.path.join(global_vars['config_path'], cfg['city'])
    specific_config_path = os.path.join(specific_config_path, cfg['run_number'])

    Path(specific_config_path).mkdir(parents = True, exist_ok = True)

    # create data location
    specific_data_path = os.path.join(global_vars['data_path'], cfg['city'])
    specific_data_path = os.path.join(specific_data_path, cfg['run_number'])

    Path(specific_data_path).mkdir(parents = True, exist_ok = True)

    # create jobs location
    specific_jobs_path = os.path.join(global_vars['job_path'], cfg['city'])
    specific_jobs_path = os.path.join(specific_jobs_path, cfg['run_number'])

    Path(specific_jobs_path).mkdir(parents = True, exist_ok = True)

    proc_style = processing_style[global_vars['processing_style']]

    logging.info(f'Generating configs with proc_style: {proc_style}')


    match global_vars['processing_style']:
        case "LDC":
            # generate folders
            for i in range(global_vars['LDCs']):
                Path(f'{specific_config_path}/ldc{i+1}').mkdir(parents = True, exist_ok = True)
                Path(f'{specific_data_path}/ldc{i+1}').mkdir(parents = True, exist_ok = True)
                Path(f'{specific_jobs_path}/ldc{i+1}').mkdir(parents = True, exist_ok = True)

                logging.info(f'Generated config location at {specific_config_path}/ldc{i+1}')
                logging.info(f'Generated data location at {specific_data_path}/ldc{i+1}')
                logging.info(f'Generated jobs location at {specific_jobs_path}/ldc{i+1}')

        case "FOLDER":
            print('folder')
        case "FILE":
            print('file')
        case _:
            print('something else (fuck up)')

    return (specific_config_path, specific_data_path, specific_jobs_path)


def slurm_city_arguments(global_vars : Dict,
                         cfg : DictConfig,
                         conf_length : int,
                         conf_path   : str,
                         job_path    : str,
                         ldc         : int,
                         prod_dir    : str) -> List:
    '''
    returns all required arguments for the slurm city configuration
    '''

    # collect all defaults
    job_name      = f"{global_vars.get('tag', 'tag')}-{cfg.get('city', 'city')}-LDC{ldc}"
    time          = cfg.get('time', '24:00:00')
    cpus_per_task = cfg.get('cpus-per-task', 36)
    mem           = cfg.get('mem', '32G')
    city          = cfg.get('city', 'city')

    slurm_args = [
        "sbatch",
        "--partition=general",
        f"--job-name={job_name}",
        f"--time={time}"
        "--nodes=1",
        "--ntasks=1",
        f"--output={job_path}/{job_name}.log",
        f"--error={job_path}/{job_name}.err",
        f"--cpus-per-task={cpus_per_task}",
        f"--mem={mem}",
        f"--array=0-{conf_length - 1}",
        f"CONFIG_PATH={conf_path},CITY={city},INIT_ENV={global_vars.get('env_script', 'broken')}",
        f"{prod_dir}/templates/job_templates/run_city.slurm",
    ]

    return slurm_args

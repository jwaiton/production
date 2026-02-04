import os
import logging
import re
from pathlib import Path

from typing import Dict, List, Optional
from math import ceil
from omegaconf import DictConfig
from omegaconf.errors import ConfigKeyError

from core.immutables import processing_style
from core.io         import prepend_all, quote_strings





def extract_globals(cfg : DictConfig) -> Dict:
    '''
    Function that extracts global parameters into a
    separate dictionary


    :param cfg: Config extracted from the job file
    :type cfg:  DictConfig


    :return:    Global config dictionary
    :rtype:     Dict[Any, Any]
    '''


    global_vars = {}
    if 'global' in cfg:

        for key, val in cfg['global'].items():
            global_vars[key] = val

        # remove from the main config
        cfg.pop('global', None)

    return global_vars


def alter_config(config_text : str,
                 alterations : DictConfig) -> str:
    '''
    Alter a config (stored as a text string) using a dictionary of alterations

    This extracts whats provided in the job configs and applies them verbatim. For example:

    fixed:
       nhits       : 10
       compression : "'ZLIB4'"
       q_cut       : 50,

    This will be implemented as:
    nhits = 10
    compression = 'ZLIB4'
    cut_dictionary = {
        q_cut = 50,
        other_params = ...
        }


    :param config_text: Text containing the template/base config
    :type config_text: str

    :param alterations: Dictionary containing the parameters to be altered
    :type alterations: DictConfig


    :return: Text containing the altered config
    :rtype: str

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




def write_configs(input_names : List,
                  output_names : List,
                  config_names : List[List],
                  config : str,
                  cfg : DictConfig,
                  global_vars : Dict) -> None:

    '''
    Write configs to their corresponding directories, ready to be used
    by the runner's sub-jobs.

    This function produces configs on a file-by-file
    basis, meaning you have input and output names, then the alterations
    you desire within conf_dict.

    Allows for the three processing styles:
        - LDC    : LDC by LDC config creation at
                   {global_path}/{tag}/data/{city/binary}/{run_number}/LDC{0..N}
        - FOLDER : Not yet implemented
        - FILE   : Same as LDC, but without the LDC component at the end.

    Allows for the processing style to alter based on how the input matches the
    output:
        - match  : match the provided processing style (input matches output)
        - funnel : all inputs into one output, hence 'funnelled'


    :param input_names  : file input names for each runner
    :type  input_names  : List

    :param output_names : file output names for each runner
    :type  output_names : List

    :param config_names : List of all the config names for each runner
    :type  config_names : List[List]

    :param config       : Base config string to be altered for each config
    :type  config       : str

    :param cfg          : Dictionary used for extracting the processing style
    :type  cfg          : DictConfig

    :param global_vars  : Dictionary containing all global variables
    :type  global_vars  : Dict
    '''


    # add a bit in here for funnel that means you select file, do everything once with
    # the list provided
    # overwrite the processing style if needed
    if 'style' in cfg:
        match cfg['style']:
            case 'match':
                proc_style = global_vars['processing_style']
            case 'funnel':
                proc_style = 'FILE'
            case _:
                raise SyntaxError(f"processing style {cfg['style']} not implemented")
    else:
        proc_style = global_vars['processing_style']

    # alter inputs and outputs
    match proc_style:
        case 'LDC':
            for i in range(global_vars['LDCs']):
                for i_names, o_names, c_names in zip(input_names[i], output_names[i], config_names[i]):
                    conf_dict = {'file_out' : o_names, 'files_in' : i_names}
                    if 'MC' in global_vars:
                        if global_vars['MC']:
                            conf_dict['run_number'] = 0
                    print('conf_dict')
                    print(conf_dict)
                    local_config = alter_config(config, conf_dict)
                    # write it to the file
                    with open(c_names, 'w') as f:
                        f.write(local_config)
        case 'FOLDER':
            print('folders not been set up yet')
        case 'FILE':
            # still should be passed through as lists
            for i_names, o_names, c_names in zip(input_names, output_names, config_names):
                conf_dict = {'file_out' : o_names, 'files_in' : i_names}
                print('conf_dict')
                print(conf_dict)
                local_config = alter_config(config, conf_dict)
                # write it to the file
                with open(c_names, 'w') as f:
                    f.write(local_config)

        case _:
            print('something else (fuck up)')


def collect_input_folder(global_vars : Dict,
                         cfg         : DictConfig) -> List:
    '''
    using the provided information, ascertain input name of the folder
    this is used in the 'funnel' case, multiple files compiling into one
    output. See the `topology` binary for an example of how this is implemented.


    :param global_vars : Dictionary containing all global variables
    :type  global_vars : Dict

    :param cfg         : Runner dictionary containing all relevant parameters
    :type  cfg         : DictConfig


    :return            : Input folder path returned as list for compatibility reasons
    :rtype             : List
    '''

    path = f"{cfg['pre_path']}{cfg['run_number']}/{cfg['post_path']}"

    return [f"'{path}'"] # done to ensure its passed through as a string properly


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
                         input_names : List,
                         name        : Optional[str] = None) -> List:
    '''
    provided with an input file, create the corresponding output file
    this assumes the structure of:

    executable_runnumber_number_whateverelse.h5

    breaks otherwise
    '''

    # overwrite the processing style if needed
    if 'style' in cfg:
        match cfg['style']:
            case 'match':
                proc_style = global_vars['processing_style']
            case 'funnel':
                proc_style = 'FILE'
            case _:
                raise SyntaxError(f"processing style {cfg['style']} not implemented")
    else:
        proc_style = global_vars['processing_style']

    # assign name to city if not provided (provided in binary case)
    if name is None:
        name = cfg['city']

    data_path = f"{global_vars['global_path']}{global_vars['tag']}/data/{name}/{cfg['run_number']}/"
    conf_path = f"{global_vars['global_path']}{global_vars['tag']}/configs/{name}/{cfg['run_number']}/"

    output_files = []
    config_files = []
    match proc_style:
        case 'LDC':
            for i in range(global_vars['LDCs']):
                LDC_files  = input_names[i]
                file_names = [f.split('/')[-1] for f in LDC_files]
                # generate them based on the number
                # if the file name contains the tag, you know its been processed and can extract the number intelligently
                if (f"_{cfg['run_number']}_" in file_names[0]) and (f"_{cfg['run_number']}_" in file_names[0]):
                    # remove run numbers to avoid confusion
                    # eg: beersheba_kr_202606_test_001_ldc1_kr
                    #     becomes beersheba_001_ldc1_kr
                    file_names = [x.replace(f"_{cfg['run_number']}_", "_") for x in file_names]
                    numbers    = [f.split('_')[1] for f in file_names]
                else:
                    # if not, default to the stupid, dangerous, silently breaking way
                    numbers    = [f.split('_')[2] for f in file_names]

                output_files.append([f"ldc{i+1}/{name}_{cfg['run_number']}_{n}_ldc{i+1}_{global_vars['tag']}.h5" for n in numbers])
                config_files.append([f"ldc{i+1}/{name}_{cfg['run_number']}_{n}_ldc{i+1}_{global_vars['tag']}.conf" for n in numbers])
        case 'FOLDER':
            print('folders not been set up yet')
        case 'FILE':
            output_files = [f"{name}_{cfg['run_number']}_{global_vars['tag']}.h5"]
            config_files = [f"{name}_{cfg['run_number']}_{global_vars['tag']}.conf"]
        case _:
            print('something else (fuck up)')

    output_files = prepend_all(output_files, data_path)
    # wrap the output files in '' for formatting
    output_files = quote_strings(output_files)
    config_files = prepend_all(config_files, conf_path)
    return output_files, config_files


def generate_folder_structure(global_vars : Dict,
                              cfg : DictConfig,
                              name : Optional[str] = None) -> tuple[Path, Path, Path]:
    '''
    generate folder structure based on global_vars and cfg
    name passed through for binaries to allow for config names independent of city
    '''
    if 'style' in cfg:
        match cfg['style']:
            case 'match':
                proc_style = global_vars['processing_style']
            case 'funnel':
                proc_style = 'FILE'
            case _:
                raise SyntaxError(f"processing style {cfg['style']} not implemented")
    else:
        proc_style = global_vars['processing_style']


    if name is None:
        name = cfg['city']

    # create config location
    specific_config_path = os.path.join(global_vars['config_path'], name)
    specific_config_path = os.path.join(specific_config_path, cfg['run_number'])

    Path(specific_config_path).mkdir(parents = True, exist_ok = True)

    # create data location
    specific_data_path = os.path.join(global_vars['data_path'], name)
    specific_data_path = os.path.join(specific_data_path, cfg['run_number'])

    Path(specific_data_path).mkdir(parents = True, exist_ok = True)

    # create jobs location
    specific_jobs_path = os.path.join(global_vars['job_path'], name)
    specific_jobs_path = os.path.join(specific_jobs_path, cfg['run_number'])

    Path(specific_jobs_path).mkdir(parents = True, exist_ok = True)


    logging.info(f'Generating configs with proc_style: {proc_style}')


    match proc_style:
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
                         prod_dir    : str,
                         chunk_size  : int | None = None) -> List[List[str]]:
    '''
    returns all required arguments for the slurm city configuration
    assuming an LDC on LDC basis
    '''

    # collect all defaults
    job_name      = f"{global_vars.get('tag', 'tag')}-{cfg.get('city', 'city')}-LDC{ldc}"
    time          = cfg.get('time', '24:00:00')
    cpus_per_task = cfg.get('cpus-per-task', 2)
    mem           = cfg.get('mem', '2G')
    city          = cfg.get('city', 'city')

    if chunk_size is not None:
        num_chunks = ceil(conf_length / chunk_size)
    else:
        num_chunks = 1
        chunk_size = 1

    sbatch_cmds = []

    for chunk_id in range(num_chunks):
        start = chunk_id * chunk_size
        end   = min(start + chunk_size - 1, conf_length -1)
        sbatch_cmds.append([
            "sbatch",
            "--partition=general",
            f"--job-name={job_name}_chunk{chunk_id}",
            f"--time={time}",
            "--nodes=1",
            "--ntasks=1",
            f"--output={job_path}/{job_name}_chunk{chunk_id}-%a.log",
            f"--error={job_path}/{job_name}_chunk{chunk_id}-%a.err",
            f"--cpus-per-task={cpus_per_task}",
            f"--mem={mem}",
            f"--array={start}-{end}",
            f"--export=CONFIG_PATH={conf_path},CITY={city},INIT_ENV={global_vars.get('env_script', 'broken')}",
            f"{prod_dir}/templates/job_templates/run_city.slurm",
        ])

    return sbatch_cmds


def slurm_binary_arguments(global_vars : Dict,
                         cfg : DictConfig,
                         conf_length : int,
                         conf_path   : str,
                         job_path    : str,
                         ldc         : int,
                         prod_dir    : str,
                         name        : str,
                         chunk_size  : int | None = None) -> List[List[str]]:
    '''
    returns all required arguments for the slurm binary configuration
    assuming an LDC on LDC basis
    '''

    # collect all defaults
    job_name      = f"{global_vars.get('tag', 'tag')}-{name}-LDC{ldc}"
    time          = cfg.get('time', '24:00:00')
    cpus_per_task = cfg.get('cpus-per-task', 2)
    mem           = cfg.get('mem', '2G')
    binary        = f"{prod_dir}/bin/{name}"


    if chunk_size is not None:
        num_chunks = ceil(conf_length / chunk_size)
    else:
        num_chunks = 1
        chunk_size = 1

    sbatch_cmds = []

    for chunk_id in range(num_chunks):
        start = chunk_id * chunk_size
        end   = min(start + chunk_size - 1, conf_length -1)

        sbatch_cmds.append([
            "sbatch",
            "--partition=general",
            f"--job-name={job_name}_chunk{chunk_id}",
            f"--time={time}",
            "--nodes=1",
            "--ntasks=1",
            f"--output={job_path}/{job_name}_chunk{chunk_id}-%a.log",
            f"--error={job_path}/{job_name}_chunk{chunk_id}-%a.err",
            f"--cpus-per-task={cpus_per_task}",
            f"--mem={mem}",
            f"--array={start}-{end}",
            f"--export=CONFIG_PATH={conf_path},BINARY={binary},INIT_ENV={global_vars.get('env_script', 'broken')}",
            f"{prod_dir}/templates/job_templates/run_binary.slurm",
        ])

    return sbatch_cmds

import os
import sys
import re
import json
import glob
import logging
import time
import subprocess

from typing     import Dict, List

from pathlib    import Path

from omegaconf  import DictConfig
from omegaconf  import OmegaConf
from core.io        import logging.info_cfg
#from core.config_io import generate_configs
from core.config_io import alter_config, generate_folder_structure, collect_input_names, extract_output_names, write_configs, slurm_city_arguments, slurm_binary_arguments, collect_input_folder

from core.immutables import processing_style

# add prod directory to path
PROD_DIR = str(os.environ['PROD_DIR'])
sys.path.append(os.path.expanduser(PROD_DIR))


def run_city_jobs(config_path: str,
                  job_path     : str,
                  global_vars  : Dict,
                  cfg     : DictConfig) -> None:
    '''
    set up job runners:
    - configs already made
    - slurm files need to be generated
    - then ran
    '''
    match global_vars['processing_style']:
        case 'LDC':
            for i in range(global_vars['LDCs']):
                full_path = os.path.join(config_path, f'ldc{i+1}')
                configs = sorted(Path(full_path).glob("*.conf"))
                slurm_batch = slurm_city_arguments(global_vars, cfg, len(configs), full_path, job_path, i+1, PROD_DIR, 100)
                # wait for jobs to be finished
                while get_running_jobs(global_vars.get('cluster_sys')) > global_vars.get('max_num_jobs'):
                    logging.info(f"Currently running jobs: {get_running_jobs(global_vars.get('cluster_sys'))}")
                    time.sleep(60)
                for slurm_args in slurm_batch:
                    time.sleep(60) # add a buffer to let jobs load into the cluster
                    # wait for jobs to be finished
                    while get_running_jobs(global_vars.get('cluster_sys')) > global_vars.get('max_num_jobs'):
                        logging.info(f"Currently running jobs: {get_running_jobs(global_vars.get('cluster_sys'))}")
                        time.sleep(60)
                    logging.info("Submitting:", " ".join(slurm_args))
                    subprocess.run(slurm_args, check=True)


def run_binary_jobs(config_path : str,
                    job_path    : str,
                    global_vars : Dict,
                    cfg         : DictConfig,
                    name        : str) -> None:
    '''
    set up job runners
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


    match proc_style:
        case 'LDC':

            for i in range(global_vars['LDCs']):
                full_path = os.path.join(config_path, f'ldc{i+1}')
                configs = sorted(Path(full_path).glob("*.conf"))
                slurm_batch = slurm_binary_arguments(global_vars, cfg, len(configs), full_path, job_path, i+1, PROD_DIR, name, 100)
                # wait for jobs to be finished
                while get_running_jobs(global_vars.get('cluster_sys')) > global_vars.get('max_num_jobs'):
                    logging.info(f"Currently running jobs: {get_running_jobs(global_vars.get('cluster_sys'))}")
                    time.sleep(60)
                for slurm_args in slurm_batch:
                    time.sleep(60) # add a buffer to let jobs load into the cluster
                    # wait for jobs to be finished
                    while get_running_jobs(global_vars.get('cluster_sys')) > global_vars.get('max_num_jobs'):
                        logging.info(f"Currently running jobs: {get_running_jobs(global_vars.get('cluster_sys'))}")
                        time.sleep(60)
                    logging.info("Submitting:", " ".join(slurm_args))
                    subprocess.run(slurm_args, check=True)
        case 'FILE':

            configs = sorted(Path(config_path).glob("*.conf"))
            slurm_batch = slurm_binary_arguments(global_vars, cfg, len(configs), config_path, job_path, 0, PROD_DIR, name)
            # wait for jobs to be finished
            while get_running_jobs(global_vars.get('cluster_sys')) > global_vars.get('max_num_jobs'):
                logging.info(f"Currently running jobs: {get_running_jobs(global_vars.get('cluster_sys'))}")
                time.sleep(60)
            for slurm_args in slurm_batch:
                time.sleep(60) # add a buffer to let jobs load into the cluster
                # wait for jobs to be finished
                while get_running_jobs(global_vars.get('cluster_sys')) > global_vars.get('max_num_jobs'):
                    logging.info(f"Currently running jobs: {get_running_jobs(global_vars.get('cluster_sys'))}")
                    time.sleep(60)
                logging.info("Submitting:", " ".join(slurm_args))
                subprocess.run(slurm_args, check=True)

def get_running_jobs(system : str) -> int:
    if system == 'SLURM':
        try:
            result = subprocess.run(["squeue", "-u", os.getenv("USER")], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split("\n")
            running_jobs = len(lines) - 1  # Subtract header line
            logging.info(f"Currently running jobs: {running_jobs}")
            return running_jobs
        except subprocess.CalledProcessError as e:
            logging.info(f"Error retrieving running jobs: {e.stderr}")
            return 0
        except FileNotFoundError as e:
            logging.exception('')
            return 0


def process_IC(global_vars : Dict,
               cfg         : DictConfig,
               name        : str) -> None:

    # create directory for storing configs
    config_name = f"{name}-{global_vars['tag']}-{global_vars['timestamp']}"

    # generate_folder_structure
    output_config_path, output_data_path, output_jobs_path = generate_folder_structure(global_vars, cfg)

    # define the generalised config shape here
    config_path = Path(f"{PROD_DIR}/configs/IC_configs/{cfg['city']}.conf")
    logging.info(f'Read/alter config from {config_path}')
    config = config_path.read_text()
    # intially alter to match fixed components
    config = alter_config(config, cfg)

    # collect all input file names
    input_names = collect_input_names(global_vars, cfg)
    output_names, config_names = extract_output_names(global_vars, cfg, input_names)

    write_configs(input_names, output_names, config_names, config, cfg, global_vars)

    run_city_jobs(output_config_path, output_jobs_path, global_vars, cfg)

def process_binary(global_vars : Dict,
                   cfg         : DictConfig,
                   name        : str) -> None:
    '''
    Handles all other file sorts for processing
    all binaries should start with the tag and run, then have all the config parameters
    from within 'fixed' expanded out as keyword arguments
    '''
    # check if its run as a job or not
    if cfg['job'] == False:
        # run locally, find the binary in the bin folder
        binary_path = Path(f"{PROD_DIR}/bin/{name}")
        if not binary_path.exists():
            logging.error(f"Binary '{name}' not found at {binary_path}")
            raise FileNotFoundError(f"Binary '{name}' not found at {binary_path}")


        payload = {
        "fixed": OmegaConf.to_container(cfg['fixed'], resolve = True), # fixes arguments like ${foo}
        "tag": global_vars['tag'],
        "run_number": cfg['run_number'],
        }

        cmd = [
            sys.executable,
            str(binary_path),
            json.dumps(payload),
        ]

        subprocess.run(cmd, check=True)
        # include arguments --> everything from fixed
    else:
        # create directory for storing configs
        config_name = f"{name}-{global_vars['tag']}-{global_vars['timestamp']}"

        # generate_folder_structure
        output_config_path, output_data_path, output_jobs_path = generate_folder_structure(global_vars, cfg, name)

        # read in config and alter it here
        config_path = Path(f"{PROD_DIR}/configs/bin_configs/{name}.conf")
        logging.info(f'Read/alter config from {config_path}')
        config = config_path.read_text()
        # intially alter to match fixed components
        config = alter_config(config, cfg)

        # here we decide on processing style again
        match cfg['style']:
            case 'match':

                # collect input file names here
                input_names = collect_input_names(global_vars, cfg)
                output_names, config_names = extract_output_names(global_vars, cfg, input_names, name)

                write_configs(input_names, output_names, config_names, config, cfg, global_vars)

                run_binary_jobs(output_config_path, output_jobs_path, global_vars, cfg, name)
            case 'funnel':
                # collect input folder here, leave the script to extract each file
                input_folder = collect_input_folder(global_vars, cfg)
                output_names, config_names = extract_output_names(global_vars, cfg, input_folder, name)
                write_configs(input_folder, output_names, config_names, config, cfg, global_vars)

                run_binary_jobs(output_config_path, output_jobs_path, global_vars, cfg, name)


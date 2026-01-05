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
from core.io        import print_cfg
#from core.config_io import generate_configs
from core.config_io import alter_config, generate_folder_structure, collect_input_names, extract_output_names, write_configs, slurm_city_arguments

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
                slurm_args = slurm_city_arguments(global_vars, cfg, len(configs), full_path, job_path, i+1, PROD_DIR)
                # wait for jobs to be finished
                while get_running_jobs(global_vars.get('cluster_sys')) > global_vars.get('max_num_jobs'):
                    print(f"Currently running jobs: {get_running_jobs(global_vars.get('cluster_sys'))}")
                    time.sleep(60)
                print("Submitting:", " ".join(slurm_args))
                subprocess.run(slurm_args, check=True)


def run_binary_jobs(config_path : str,
                    job_path    : str,
                    global_vars : Dict,
                    cfg         : DictConfig) -> None:
    '''
    set up job runners
    '''
    match global_vars['processing_style']:
        case 'LDC':
            for i in range(global_vars['LDCs']):
                full_path = os.path.join(config_path, f'ldc{i+1}')
                configs = sorted(Path(full_path).glob("*.conf"))
                slurm_args = slurm_binary_arguments(global_vars, cfg, len(configs), full_path, job_path, i+1, PROD_DIR)
                # wait for jobs to be finished
                while get_running_jobs(global_vars.get('cluster_sys')) > global_vars.get('max_num_jobs'):
                    print(f"Currently running jobs: {get_running_jobs(global_vars.get('cluster_sys'))}")
                    time.sleep(60)
                print("Submitting:", " ".join(slurm_args))
                subprocess.run(slurm_args, check=True)


def get_running_jobs(system : str) -> int:
    if system == 'SLURM':
        try:
            result = subprocess.run(["squeue", "-u", os.getenv("USER")], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split("\n")
            running_jobs = len(lines) - 1  # Subtract header line
            print(f"Currently running jobs: {running_jobs}")
            return running_jobs
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving running jobs: {e.stderr}")
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

    write_configs(input_names, output_names, config_names, config, global_vars)

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
        config_path = Path(f"{PROD_DIR}/configs/bin/configs{name}.conf")
        logging.info(f'Read/alter config from {config_path}')
        config = config_path.read_text()
        # intially alter to match fixed components
        config = alter_config(config, cfg)

        # collect input file names here
        input_names = collect_input_names(global_vars, cfg)
        output_names, config_names = extract_output_names(global_vars, cfg, input_names, name)

        write_configs(input_names, output_names, config_names, config, global_vars)

        run_binary_jobs(output_config_path, output_jobs_path, global_vars, cfg)

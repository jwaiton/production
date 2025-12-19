import os
import sys
import re
import logging

from typing     import Dict, List

from pathlib    import Path

from omegaconf  import DictConfig

from core.io        import print_cfg
#from core.config_io import generate_configs
from core.config_io import alter_config, generate_folder_structure, collect_input_names, extract_output_names, write_configs

from core.immutables import processing_style

# add prod directory to path
PROD_DIR = str(os.environ['PROD_DIR'])
sys.path.append(os.path.expanduser(PROD_DIR))


def run_city_jobs(config_path: str,
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
                full_path = os.path,join(config_path, f'ldc{i+1}')
                configs = sorted(config_path.glob("*.conf"))
                slurm_args = city_template(global_vars, len(configs))


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


def process_binary(global_vars, config_dict, name):
    print('binary')

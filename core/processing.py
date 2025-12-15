import os
import logging

from typing     import Dict

from pathlib    import Path

from omegaconf  import DictConfig

from core.io        import print_cfg
from core.config_io import generate_configs

from core.immutables import processing_style


def process_IC(global_vars : Dict,
               cfg         : DictConfig,
               name        : str) -> None:

    # create directory for storing configs
    config_name = f"{name}-{global_vars['tag']}-{global_vars['timestamp']}"
    specific_config_path = os.path.join(global_vars['config_path'], )
    Path(specific_config_path).mkdir(parents = True, exist_ok = True)

    proc_style = processing_style[global_vars['processing_style']]

    logging.info(f'Generating configs with proc_style: {proc_style}')

    match proc_style:
        case processing_style.LDC:
            # generate folders
            for i in range(global_vars['LDCs']):
                Path(f'{specific_config_path}/LDC{i}').mkdir(parents = True, exist_ok = True)
                logging.info(f'Generated config location at {specific_config_path}/LDC{i}')
        case processing_style.FOLDER:
            print('folder')
        case processing_style.FILE:
            print('file')
        case _:
            print('something else (fuck up)')



    # extract the base config template
    generate_configs(global_vars,
                     cfg,
                     config_name,
                     proc_style)
    # create jobs to execute these configs


    # run the jobs

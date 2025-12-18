import os
import logging
import re
from pathlib import Path

from typing import Dict

from omegaconf import DictConfig

from core.immutables import processing_style

def extract_globals(cfg : DictConfig) -> Dict:
    global_vars = {}
    if 'global' in cfg:

        for key, val in cfg['global'].items():
            global_vars[key] = val

        # remove from the main config
        cfg.pop('global', None)

    return global_vars


def alter_config(config_text : str, alterations : dict) -> str:
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
                                     rf"{key} = {value},",
                                     config_text,
                                     flags = re.MULTILINE)
            except Exception as e:
                logging.error(f"Couldn't alter config for key value pair: {key}, {value}\n {e}")

    return config_text


def generate_folder_structure(global_vars : Dict,
                              cfg : DictConfig) -> None:

    # extract the specific sweep for this run
    parameter_folder = ''
    if cfg['sweep_params']:
        for param in cfg['sweep_params']:
            parameter_folder += param
            parameter_folder += str(cfg[param])
            parameter_folder += '_'
        # remove trailing _
        parameter_folder = parameter_folder[:-1]

    # create config location
    specific_config_path = os.path.join(global_vars['config_path'], cfg['city'])
    specific_config_path = os.path.join(specific_config_path, cfg['run_number'])
    if parameter_folder != '':
        specific_config_path = os.path.join(specific_config_path, parameter_folder)

    Path(specific_config_path).mkdir(parents = True, exist_ok = True)

    # create data location
    specific_data_path = os.path.join(global_vars['data_path'], cfg['city'])
    specific_data_path = os.path.join(specific_data_path, cfg['run_number'])
    if parameter_folder != '':
        specific_data_path = os.path.join(specific_data_path, parameter_folder)

    Path(specific_data_path).mkdir(parents = True, exist_ok = True)

    proc_style = processing_style[global_vars['processing_style']]

    logging.info(f'Generating configs with proc_style: {proc_style}')


    match global_vars['processing_style']:
        case "LDC":
            # generate folders
            for i in range(global_vars['LDCs']):
                Path(f'{specific_config_path}/ldc{i+1}').mkdir(parents = True, exist_ok = True)
                Path(f'{specific_data_path}/ldc{i+1}').mkdir(parents = True, exist_ok = True)
                logging.info(f'Generated config location at {specific_config_path}/ldc{i+1}')
                # generate all config files based on input files



        case "FOLDER":
            print('folder')
        case "FILE":
            print('file')
        case _:
            print('something else (fuck up)')



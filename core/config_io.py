import logging
import re

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



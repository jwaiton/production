from typing import Dict

from omegaconf import DictConfig

def extract_globals(cfg : DictConfig) -> Dict:
    global_vars = {}
    if 'global' in cfg:
        print('global shit here!')

        for key, val in cfg['global'].items():
            global_vars[key] = val

        # remove from the main config
        cfg.pop('global', None)

    return global_vars

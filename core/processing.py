import os

from typing import Dict
from pathlib import Path

from omegaconf import ConfigDict



def process_IC(global_vars : Dict,
               cfg         : ConfigDict,
               name        : str) -> None:

    # create directory for storing configs
    config_name = f"{name}-{global_vars['timestamp']}"
    specific_config_path = os.path.join(global_vars.config_path, )
    Path(specific_config_path).mkdir(parents = True, exist_ok = True)


    # create configs based on alterations


    # create jobs to execute these configs


    # run the jobs

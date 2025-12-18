import configparser
import logging
import ast

from typing import Dict

from omegaconf import DictConfig

def read_config_file(file_path  :  str) -> dict:
    '''
    Read config file and extract relevant information returned as a dictionary.

    Extracted explicitly from MULE:
    https://github.com/nu-ZOO/MULE/blob/abeab70/packs/core/io.py#L68

    Parameters
    ----------

    file_path (str)  :  Path to config file

    Returns
    -------

    arg_dict (dict)  :  Dictionary of relevant arguments for the pack
    '''
    # setup config parser
    config = configparser.ConfigParser()

    try:
        # read in arguments, require the required ones
        config.read(file_path)
    except TypeError as e:
        logging.error(f"Error reading config file '{file_path}': {e}")
        return None

    arg_dict = {}
    for section in config.sections():
        for key in config[section]:
            # the config should be written in such a way that the python evaluator
            # can determine its type
            #
            # we can setup stricter rules at some other time
            arg_dict[key] = ast.literal_eval(config[section][key])

    return arg_dict

def print_cfg(cfg : DictConfig, indent: int = 0) -> None:
    # set base width of display
    width = 30

    max_key_width = max(len(str(k)) for k in cfg.keys())

    # adding an indent
    space = " " * indent


    print(f'{space}===================')
    for key, value in cfg.items():
        # self nesting
        if (type(value) is DictConfig) or (type(value) is dict):
            print(f'{space}{key:<{max_key_width}}  :')
            print_cfg(value, indent = indent + 4)
        else:
            print(f'{space}{key:<{max_key_width}}  :  {value}')

        # outer layer, add some padding. this is lazy
        if indent == 4:
            print('\n')
    print(f'{space}===================')


def prepend_all(data, prefix):
    if isinstance(data, list):
        return [prepend_all(x, prefix) for x in data]
    else:
        return prefix + data


def quote_strings(data):
    if isinstance(data, list):
        return [quote_strings(x) for x in data]
    elif isinstance(data, str):
        return f"'{data}'"
    else:
        return data # catch for the weird things you shouldnt pass in

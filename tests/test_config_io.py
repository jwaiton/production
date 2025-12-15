import os
import sys

from omegaconf import OmegaConf


# add prod directory to path
PROD_DIR = str(os.environ['PROD_DIR'])
sys.path.append(os.path.expanduser(PROD_DIR))


from core import config_io


def test_global_extraction():

    test_dict = {"k" : "v", "list" : [1, {"a": "1", "b": "2", 3: "c"}]}
    global_params = {'a' : 1, 'b' : 5, 'params' : ['lies', 'deception', 'fury']}
    test_dict['global'] = global_params

    test_config = OmegaConf.create(test_dict)

    global_extracted = config_io.extract_globals(test_config)

    assert global_params == global_extracted


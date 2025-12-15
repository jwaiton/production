import os
import pytest

@pytest.fixture(scope="session")
def PROD_dir():
    return str(os.environ['PROD_DIR'])

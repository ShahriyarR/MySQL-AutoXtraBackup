import pytest
from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer

clb_obj = CloneBuildStartServer()

@pytest.fixture()
def return_clone_obj():
    return clb_obj

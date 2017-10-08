import pytest
from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer
from prepare_env_test_mode.run_benchmark import RunBenchmark

clb_obj = CloneBuildStartServer()

@pytest.fixture()
def return_clone_obj():
    return clb_obj

@pytest.fixture()
def return_basedir():
    basedir = clb_obj.get_basedir()
    return basedir

rb_obj = RunBenchmark()

@pytest.fixture()
def return_run_benchmark_obj():
    return rb_obj


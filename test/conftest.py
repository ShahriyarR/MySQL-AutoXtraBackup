import pytest
from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer
from prepare_env_test_mode.run_benchmark import RunBenchmark
from prepare_env_test_mode.config_generator import ConfigGenerator
from prepare_env_test_mode.take_backup import WrapperForBackupTest
from prepare_env_test_mode.prepare_backup import WrapperForPrepareTest

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

cg_obj = ConfigGenerator()


@pytest.fixture()
def return_config_generator_obj():
    return cg_obj

@pytest.fixture()
def return_take_backup_obj():
    bck_obj = WrapperForBackupTest()
    return bck_obj

@pytest.fixture()
def return_prepare_backup_obj():
    prp_obj = WrapperForPrepareTest()
    return prp_obj
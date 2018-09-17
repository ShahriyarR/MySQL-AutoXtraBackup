import pytest
from prepare_env_test_mode.clone_build_start_server import CloneBuildStartServer
from prepare_env_test_mode.run_benchmark import RunBenchmark
from prepare_env_test_mode.config_generator import ConfigGenerator
from prepare_env_test_mode.runner_test_mode import RunnerTestMode
from master_backup_script.backuper import Backup

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
def return_runner_test_mode_obj_5_6_xb_2_3():
    obj = RunnerTestMode(config="{}/{}".format(clb_obj.testpath, 'xb_2_3_ps_5_6.cnf'))
    return obj

@pytest.fixture()
def return_runner_test_mode_obj_5_6_xb_2_4():
    obj = RunnerTestMode(config="{}/{}".format(clb_obj.testpath, 'xb_2_4_ps_5_6.cnf'))
    return obj

@pytest.fixture()
def return_runner_test_mode_obj_5_7_xb_2_4():
    obj = RunnerTestMode(config="{}/{}".format(clb_obj.testpath, 'xb_2_4_ps_5_7.cnf'))
    return obj
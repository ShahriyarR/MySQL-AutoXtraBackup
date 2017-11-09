import pytest
from prepare_env_test_mode.run_benchmark import RunBenchmark

class TestRunnerTestMode:

    # No matter here which fixture to choose I need an object
    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_6_xb_2_3")
    def test_get_free_tcp_port(self, return_runner_test_mode_obj_5_6_xb_2_3):
        return_runner_test_mode_obj_5_6_xb_2_3.get_free_tcp_port()

    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_6_xb_2_3")
    def test_create_dsns_table(self, return_runner_test_mode_obj_5_6_xb_2_3):
        for basedir in return_runner_test_mode_obj_5_6_xb_2_3.basedirs:
            if '5.6' in basedir:
                mysql_master_client_cmd = RunBenchmark(config=return_runner_test_mode_obj_5_6_xb_2_3.conf).get_mysql_conn(
                    basedir=basedir)
                assert return_runner_test_mode_obj_5_6_xb_2_3.create_dsns_table(mysql_master_client_cmd)

    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_6_xb_2_3")
    def test_populate_dsns_table(self, return_runner_test_mode_obj_5_6_xb_2_3):
        for basedir in return_runner_test_mode_obj_5_6_xb_2_3.basedirs:
            if '5.6' in basedir:
                mysql_master_client_cmd = RunBenchmark(config=return_runner_test_mode_obj_5_6_xb_2_3.conf).get_mysql_conn(
                    basedir=basedir)
                file_name = "cl_node0"
                mysql_slave_client_cmd = RunBenchmark(config=return_runner_test_mode_obj_5_6_xb_2_3.conf).get_mysql_conn(basedir=basedir,
                                                                                       file_name=file_name)
                # Get slave port here
                sql = "{} -e 'select @@port'".format(mysql_slave_client_cmd)
                port = return_runner_test_mode_obj_5_6_xb_2_3.run_sql_command(sql_command=sql)
                #slave_sock = "{}/sock0.sock".format(basedir)
                assert return_runner_test_mode_obj_5_6_xb_2_3.populate_dsns_table(sql_conn=mysql_master_client_cmd, slave_port=port[7:])

    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_6_xb_2_3")
    def test_run_pt_table_checksum(self, return_runner_test_mode_obj_5_6_xb_2_3):
        for basedir in return_runner_test_mode_obj_5_6_xb_2_3.basedirs:
            if '5.6' in basedir:
                # socket = return_run_benchmark_obj.get_sock(basedir=basedir)
                # conn_options = "--user={} --socket={}".format('root', socket)
                assert return_runner_test_mode_obj_5_6_xb_2_3.run_pt_table_checksum(basedir=basedir)

    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_6_xb_2_3")
    def test_run_change_master(self, return_runner_test_mode_obj_5_6_xb_2_3):
        for basedir in return_runner_test_mode_obj_5_6_xb_2_3.basedirs:
            if '5.6' in basedir:
                assert return_runner_test_mode_obj_5_6_xb_2_3.run_change_master(basedir=basedir, file_name='cl_node0')

    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_6_xb_2_3")
    def test_drop_blank_mysql_users(self, return_runner_test_mode_obj_5_6_xb_2_3):
        for basedir in return_runner_test_mode_obj_5_6_xb_2_3.basedirs:
            if '5.6' in basedir:
                mysql_master_client_cmd = RunBenchmark(config=return_runner_test_mode_obj_5_6_xb_2_3.conf).get_mysql_conn(basedir=basedir)
                assert return_runner_test_mode_obj_5_6_xb_2_3.drop_blank_mysql_users(mysql_master_client_cmd)

    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_6_xb_2_3")
    def test_check_slave_status(self, return_runner_test_mode_obj_5_6_xb_2_3):
        for basedir in return_runner_test_mode_obj_5_6_xb_2_3.basedirs:
            if '5.6' in basedir:
                mysql_slave_client_cmd = RunBenchmark(config=return_runner_test_mode_obj_5_6_xb_2_3.conf).get_mysql_conn(basedir=basedir, file_name="cl_node0")
                show_slave_status = "{} -e 'show slave status\G'"
                assert return_runner_test_mode_obj_5_6_xb_2_3.check_slave_status(show_slave_status.format(mysql_slave_client_cmd)) is None


    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_6_xb_2_3")
    def test_wipe_backup_prepare_copyback_5_6_xb_2_3(self, return_runner_test_mode_obj_5_6_xb_2_3):
        for basedir in return_runner_test_mode_obj_5_6_xb_2_3.basedirs:
            if '5.6' in basedir:
                return_runner_test_mode_obj_5_6_xb_2_3.wipe_backup_prepare_copyback(basedir=basedir)

    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_6_xb_2_4")
    def test_wipe_backup_prepare_copyback_5_6_xb_2_4(self, return_runner_test_mode_obj_5_6_xb_2_4):
        for basedir in return_runner_test_mode_obj_5_6_xb_2_4.basedirs:
            if '5.6' in basedir:
                return_runner_test_mode_obj_5_6_xb_2_4.wipe_backup_prepare_copyback(basedir=basedir)

    @pytest.mark.usefixtures("return_runner_test_mode_obj_5_7_xb_2_4")
    def test_wipe_backup_prepare_copyback_5_7_xb_2_4(self, return_runner_test_mode_obj_5_7_xb_2_4):
        for basedir in return_runner_test_mode_obj_5_7_xb_2_4.basedirs:
            if '5.7' in basedir:
                return_runner_test_mode_obj_5_7_xb_2_4.wipe_backup_prepare_copyback(basedir=basedir)

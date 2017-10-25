import pytest

@pytest.mark.usefixtures("return_run_benchmark_obj")
class TestRunBenchmark:
    """
    Test class for run_benchmark.py
    """

    def test_get_sock(self, return_run_benchmark_obj):
        for basedir in return_run_benchmark_obj.basedir:
            assert "sock" in return_run_benchmark_obj.get_sock(basedir=basedir)

    def test_get_mysql_conn(self, return_run_benchmark_obj):
        for basedir in return_run_benchmark_obj.basedir:
            assert "mysql" in return_run_benchmark_obj.get_mysql_conn(basedir=basedir)

    def test_create_db(self, return_run_benchmark_obj):
        for basedir in return_run_benchmark_obj.basedir:
            assert return_run_benchmark_obj.create_db(db_name="test_run_benchmark_db", basedir=basedir) is True

    def test_run_sysbench_prepare(self, return_run_benchmark_obj):
        for basedir in return_run_benchmark_obj.basedir:
            assert return_run_benchmark_obj.run_sysbench_prepare(basedir=basedir) is True

    def test_run_sysbench_run(self, return_run_benchmark_obj):
        for basedir in return_run_benchmark_obj.basedir:
            assert return_run_benchmark_obj.run_sysbench_run(basedir=basedir) is True
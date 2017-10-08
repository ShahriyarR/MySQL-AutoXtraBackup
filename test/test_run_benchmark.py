import pytest

@pytest.mark.usefixtures("return_run_benchmark_obj")
class TestRunBenchmark:
    """
    Test class for run_benchmark.py
    """

    def test_get_sock(self, return_run_benchmark_obj):
        assert "sock" in return_run_benchmark_obj.get_sock()

    def test_get_mysql_conn(self, return_run_benchmark_obj):
        assert "mysql" in return_run_benchmark_obj.get_mysql_conn()

    def test_create_db(self, return_run_benchmark_obj):
        assert return_run_benchmark_obj.create_db("test_run_benchmark_db") == True

    def test_run_sysbench(self, return_run_benchmark_obj):
        assert return_run_benchmark_obj.run_sysbench() == True
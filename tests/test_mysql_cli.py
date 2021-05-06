class TestMySQLCLi:
    def test_create_mysql_client_command(self, return_bck_obj):
        result = '/usr/bin/mysql --defaults-file= -uroot --password=12345 --socket=/var/run/mysqld/mysqld.sock -e "select 1"'
        sql = "select 1"
        assert return_bck_obj.mysql_cli.create_mysql_client_command(sql) == result

    def test_mysql_run_command(self, return_bck_obj):
        sql = "select 1"
        assert return_bck_obj.mysql_cli.mysql_run_command(sql) is True

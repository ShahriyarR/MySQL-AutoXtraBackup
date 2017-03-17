from partial_recovery.partial import PartialRecovery
import pytest

class TestPartialRecovery:
    """Tests for PartialRecovery class and methods"""

    def test_create_mysql_client_command(self):
        """Checking return value type"""
        print("\nIn test_create_mysql_client_command()...")
        return_value = PartialRecovery().create_mysql_client_command("")
        assert type(return_value) == str

    def test_create_mysql_client_command01(self):
        """Checking if TypeError raised"""
        print("\nIn test_create_mysql_client_command01()...")
        with pytest.raises(TypeError):
            PartialRecovery().create_mysql_client_command()

    def test_check_innodb_file_per_table(self):
        """Checking return value type"""
        print("\nIn test_check_innodb_file_per_table()...")
        assert type(PartialRecovery().check_innodb_file_per_table()) == bool

    def test_check_mysql_version(self):
        """Checking return value type"""
        print("\nIn test_check_mysql_version()...")
        assert type(PartialRecovery().check_mysql_version()) == bool

    def test_check_database_exists_on_mysql(self):
        """Checking return value type"""
        print("\nIn test_check_mysql_version()...")
        assert type(PartialRecovery().check_database_exists_on_mysql("")) == bool

    def test_check_database_exists_on_mysql01(self):
        """Checking if TypeError raised"""
        print("\nIn test_check_mysql_version01()...")
        with pytest.raises(TypeError):
            PartialRecovery().check_database_exists_on_mysql()

    def test_check_table_exists_on_mysql(self):
        """Checking return value type"""
        print("\nIn test_check_table_exists_on_mysql()...")
        assert type(PartialRecovery().check_table_exists_on_mysql("","","")) == bool

    def test_check_table_exists_on_mysql01(self):
        """Checking if TypeError raised"""
        print("\nIn test_check_table_exists_on_mysql01()...")
        with pytest.raises(TypeError):
            PartialRecovery().check_table_exists_on_mysql()

    def test_run_mysqlfrm_utility(self):
        """Checking return value for None"""
        print("\nIn test_run_mysqlfrm_utility()...")
        assert PartialRecovery().run_mysqlfrm_utility("") is None

    def test_run_mysqlfrm_utility01(self):
        """Checking return value for None"""
        print("\nIn test_run_mysqlfrm_utility01()...")
        assert PartialRecovery().run_mysqlfrm_utility("/etc/passwd") is None

    def test_get_table_ibd_file(self):
        """Checking if TypeError raised"""
        print("\nIn test_get_table_ibd_file()...")
        with pytest.raises(TypeError):
            PartialRecovery().get_table_ibd_file()

    def test_get_table_ibd_file01(self):
        """Checking return value type"""
        print("\nIn test_get_table_ibd_file01()...")
        assert type(PartialRecovery().get_table_ibd_file("","")) == bool

    def test_lock_table(self):
        """Checking return value type"""
        print("\nIn test_lock_table()...")
        assert type(PartialRecovery().lock_table("","")) == bool

    def test_lock_table01(self):
        """Checking if TypeError raised"""
        print("\nIn test_lock_table01()...")
        with pytest.raises(TypeError):
            PartialRecovery().lock_table()

    def test_alter_tablespace(self):
        """Checking return value type"""
        print("\nIn test_alter_tablespace()...")
        assert type(PartialRecovery().alter_tablespace("","")) == bool

    def test_alter_tablespace01(self):
        """Checking if TypeError raised"""
        print("\nIn test_alter_tablespace01()...")
        with pytest.raises(TypeError):
            PartialRecovery().alter_tablespace()

    def test_copy_ibd_file_back(self):
        """Checking return value type"""
        print("\nIn test_copy_ibd_file_back()...")
        assert type(PartialRecovery().copy_ibd_file_back("","")) == bool

    def test_copy_ibd_file_back01(self):
        """Checking if TypeError raised"""
        print("\nIn test_copy_ibd_file_back01()...")
        with pytest.raises(TypeError):
            PartialRecovery().copy_ibd_file_back()

    def test_give_chown(self):
        """Checking return value type"""
        print("\nIn test_give_chown()...")
        assert type(PartialRecovery().give_chown("")) == bool

    def test_give_chown01(self):
        """Checking if TypeError raised"""
        print("\nIn test_give_chown01()...")
        with pytest.raises(TypeError):
            PartialRecovery().give_chown()

    def test_import_tablespace(self):
        """Checking return value type"""
        print("\nIn test_import_tablespace()...")
        assert type(PartialRecovery().import_tablespace("", "")) == bool

    def test_import_tablespace01(self):
        """Checking if TypeError raised"""
        print("\nIn test_import_tablespace01()...")
        with pytest.raises(TypeError):
            PartialRecovery().import_tablespace()

    def test_unlock_tables(self):
        """Checking return value type"""
        print("\nIn test_unlock_tables()...")
        assert type(PartialRecovery().unlock_tables()) == bool


    # def test_final_actions(self):
    #     print("\nIn test_final_actions()...")
    #     PartialRecovery().final_actions()

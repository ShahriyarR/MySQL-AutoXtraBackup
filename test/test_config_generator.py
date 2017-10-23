import pytest
from general_conf.generalops import GeneralClass

@pytest.mark.usefixtures("return_config_generator_obj")
class TestConfigGenerator:
    #Class for testing config_generator.py

    def test_generate_config_files(self, return_config_generator_obj):
        assert return_config_generator_obj.the_main_generator() is True

    def test_options_combination_generator(self, return_config_generator_obj):
        mysql_options = GeneralClass(config='{}/{}'.format(return_config_generator_obj.testpath, 'xb_2_4_ps_5_6.conf')).mysql_options
        assert len(return_config_generator_obj.options_combination_generator(mysql_options)) > 0
        assert isinstance(return_config_generator_obj.options_combination_generator(mysql_options), list)
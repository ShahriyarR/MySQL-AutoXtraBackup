import pytest


@pytest.mark.usefixtures("return_config_generator_obj")
class TestConfigGenerator:
    #Class for testing config_generator.py

    def test_generate_config_files(self, return_config_generator_obj):
        assert return_config_generator_obj.generate_config_files() is True
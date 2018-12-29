from setuptools import setup
from general_conf import path_config
from general_conf.generate_default_conf import GenerateDefaultConfig

datafiles = [(path_config.config_path, [])]
gen_conf = GenerateDefaultConfig()
gen_conf.generate_config_file()

setup(
    name='mysql-autoxtrabackup',
    version='1.5.4',
    packages=['general_conf', 'backup_prepare', 'partial_recovery', 'master_backup_script', 'prepare_env_test_mode'],
    package_data={
        'prepare_env_test_mode': ['*.sh', '*.sql']
    },
    py_modules=['autoxtrabackup'],
    url='https://github.com/ShahriyarR/MySQL-AutoXtraBackup',
    download_url='https://github.com/ShahriyarR/MySQL-AutoXtraBackup/archive/v1.5.4.zip',
    license='MIT',
    author='Shahriyar Rzayev',
    author_email='rzayev.shahriyar@yandex.com',
    description='Commandline tool written in Python 3 for using Percona XtraBackup',
    install_requires=[
        'click>=3.3',
        'mysql-connector==2.1.4',
        'pid>=2.0',
        'humanfriendly>=2.0',
        'pytest'
    ],
    dependency_links=['https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-2.1.4.tar.gz'],
    entry_points='''
        [console_scripts]
        autoxtrabackup=autoxtrabackup:all_procedure
    ''',
    data_files=datafiles,
)

from setuptools import setup
from general_conf import path_config
from general_conf.generate_default_conf import GenerateDefaultConfig
from os.path import isfile

datafiles = [(path_config.config_path, [])]
gen_conf = GenerateDefaultConfig()
if not isfile(path_config.config_path_file):
    gen_conf.generate_config_file()

setup(
    name='mysql-autoxtrabackup',
    version='2.0',
    packages=['general_conf', 'backup_prepare', 'backup_backup',
              'test', 'process_runner'],
    package_data={
        'test': ['*.sh', '*.py', '*.bats']
    },
    py_modules=['autoxtrabackup'],
    url='https://github.com/ShahriyarR/MySQL-AutoXtraBackup',
    download_url='https://github.com/ShahriyarR/MySQL-AutoXtraBackup/archive/v2.0.zip',
    license='MIT',
    author='Shahriyar Rzayev',
    author_email='rzayev.shahriyar@yandex.com',
    description='Commandline tool written in Python 3 for using Percona XtraBackup',
    install_requires=[
        'click>=3.3',
        'pid>=2.0',
        'humanfriendly>=2.0',
        'pytest'
    ],
    entry_points='''
        [console_scripts]
        autoxtrabackup=autoxtrabackup:all_procedure
    ''',
    data_files=datafiles,
)

from setuptools import setup

setup(
    name='mysql-autoxtrabackup',
    version='1.0',
    packages=['general_conf', 'backup_prepare', 'partial_recovery', 'master_backup_script'],
    py_modules = ['autoxtrabackup'],
    url='https://github.com/ShahriyarR/MySQL-AutoXtraBackup',
    license='',
    author='sh',
    author_email='rzayev,sehriyar@gmail.com',
    description='Python 3 scripts for using Percona Xtrabackup',
    install_requires=[
        'click>=3.3',
        'mysql-connector-python>=2.0.2',
    ],
    entry_points='''
        [console_scripts]
        autoxtrabackup=autoxtrabackup:all_procedure
    ''',
)
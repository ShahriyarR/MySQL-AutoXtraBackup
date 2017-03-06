from setuptools import setup

datafiles = [('//etc', ['general_conf/bck.conf'])]

setup(
    name='mysql-autoxtrabackup',
    version='1.4.7',
    packages=['general_conf', 'backup_prepare', 'partial_recovery', 'master_backup_script'],
    py_modules=['autoxtrabackup'],
    url='https://github.com/ShahriyarR/MySQL-AutoXtraBackup',
    download_url='https://github.com/ShahriyarR/MySQL-AutoXtraBackup/archive/v1.4.7.zip',
    license='MIT',
    author='Shahriyar Rzayev',
    author_email='rzayev.shahriyar@yandex.com',
    description='Commandline tool written in Python 3 for using Percona XtraBackup',
    install_requires=[
        'click>=3.3',
        'mysql-connector>=2.0.2',
        'pid>=2.0',
        'humanfriendly>=2.0'
    ],
    dependency_links=['https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-2.1.3.tar.gz'],
    entry_points='''
        [console_scripts]
        autoxtrabackup=autoxtrabackup:all_procedure
    ''',
    data_files=datafiles,
)

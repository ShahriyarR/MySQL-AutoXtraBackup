Installation
============

System requirements
-------------------

Following packages should be already there:

-  Percona Xtrabackup (>= 2.3.5)
-  Python 3 (>= 3.5)

Installing MySQL-AutoXtraBackup
-------------------------------

Using pip3:

::

    pip3 install mysql-autoxtrabackup

Installing from source with pip:

::

    pip3 install git+https://github.com/ShahriyarR/MySQL-AutoXtraBackup


Installing from source with python (not recommended because uninstalling is hard):

::

    git clone https://github.com/ShahriyarR/MySQL-AutoXtraBackup.git
    cd  to MySQL-AutoXtraBackup
    sudo python3 setup.py install

As Percona XtraBackup requires root privileges in order to backup the MySQL server, it is convenient to install,
autoxtrabackup globally. But, if you think no, then install it to virtualenv and then call as root :)
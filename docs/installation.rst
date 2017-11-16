Installation
============

System requirements
-------------------

Following packages should be already there:

-  Percona Xtrabackup (>= 2.3.5)
-  Python 3 (tested version 3.5.3 on CentOS 7)
-  mysql-utilities (>=1.5.4)

Preparing the system
--------------------

Installing dependencies:

::

    yum install openssl openssl-devel zlib zlib-devel

Installing latest XtraBackup:
For more options please refer to official documentation -> `Installing Percona XtraBackup 2.4 <https://www.percona.com/doc/percona-xtrabackup/2.4/installation.html>`_

::

    yum install http://www.percona.com/downloads/percona-release/redhat/0.1-3/percona-release-0.1-3.noarch.rpm
    yum install percona-xtrabackup
    or
    yum install percona-xtrabackup-24

Installing Python 3 from source:

::

    wget https://www.python.org/ftp/python/3.5.3/Python-3.5.3.tgz
    tar -xf Python-3.5.3.tgz
    cd Python-3.5.3

    -- Open Setup.dist file and search for zlib, uncomment zlib notes:
    * nano Modules/Setup.dist
    # See http://www.gzip.org/zlib/
    zlib zlibmodule.c -I$(prefix)/include -L$(exec_prefix)/lib -lz

    -- Also search for ssl and uncomment ssl section:

    # socket line above, and possibly edit the SSL variable:
    SSL=/usr/local/ssl
    _ssl _ssl.c \
            -DUSE_SSL -I$(SSL)/include -I$(SSL)/include/openssl \
            -L$(SSL)/lib -lssl -lcrypto

    mkdir /opt/Python-3.5.3

    ./configure --prefix=/opt/Python-3.5.3
    make
    make install

Installing mysql-connector-python and mysql-utilities:
(For CentOS 7).
::

    wget https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-2.1.5-1.el7.x86_64.rpm
    yum install mysql-connector-python-2.1.5-1.el7.x86_64.rpm

::

    wget https://dev.mysql.com/get/Downloads/MySQLGUITools/mysql-utilities-1.6.5-1.el7.noarch.rpm
    yum install mysql-utilities-1.6.5-1.el7.noarch.rpm

Installing MySQL-AutoXtraBackup
-------------------------------

Using pip3:

::

    pip3 install mysql-autoxtrabackup

Installing from source:

::

    cd /home git clone https://github.com/ShahriyarR/MySQL-AutoXtraBackup.git
    cd /home/MySQL-AutoXtraBackup/
    sudo python3 setup.py install

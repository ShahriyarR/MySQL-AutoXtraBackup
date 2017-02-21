MySQL-AutoXtrabackup
====================

MySQL AutoXtrabackup commandline tool written in Python 3.
For community from Azerbaijan MySQL User Community: [MySQL Azerbaijan Community](http://mysql.az/).
For any question please ask: [Email](mailto:rzayev.shahriyar@yandex.com)

===========

Demo Usage Video(is subject to change) NOTE: UPDATED!
--------------------------------------

[![autoxtrabackup tool usage demo video](http://img.youtube.com/vi/ODfbz1bRKfY/0.jpg)](https://www.youtube.com/watch?v=ODfbz1bRKfY)


Requirements:
-------------

    * Percona Xtrabackup (>= 2.3.5)
    * Python 3 (tested version 3.5.3 on CentOS 7)
    * Official mysql-connector-python (>= 2.0.2 )
    * mysql-utilities (>=1.5.4)

===========

Preparing System
-----------------

    Installing dependencies:

        yum install openssl openssl-devel zlib zlib-devel
        
    Installing latest XtraBackup:
        
        yum install http://www.percona.com/downloads/percona-release/redhat/0.1-3/percona-release-0.1-3.noarch.rpm
        yum install percona-xtrabackup

    Installing Python 3 from source:

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
        #For CentOS 7.
        wget https://dev.mysql.com/get/Downloads/Connector-Python/mysql-connector-python-2.1.5-1.el7.x86_64.rpm
        yum install mysql-connector-python-2.1.5-1.el7.x86_64.rpm
        
        wget wget https://dev.mysql.com/get/Downloads/MySQLGUITools/mysql-utilities-1.6.5-1.el7.noarch.rpm
        yum install mysql-utilities-1.6.5-1.el7.noarch.rpm
        
    
    Installing MySQL-AutoXtrabackup and dependencies:
        
        cd /home
        git clone https://github.com/ShahriyarR/MySQL-AutoXtraBackup.git
        cd  /home/MySQL-AutoXtraBackup/
        python3 setup.py install
    

        
Project Structure:
------------------
    
    XtraBackup is powerful and open-source hot online backup tool  for MySQL from Percona.
    This script is using XtraBackup for full and incremental backups, also for preparing and recovering taken backups
    Here is project path tree (default location is /home/MySQL-AutoXtraBackup):
        
        * backup_dir 			-- The main folder for storing backups.
        * master_backup_script	-- Full and Incremental backup taker script.
        * backup_prepare		-- Backup prepare and restore script.
        * partial_recovery		-- Partial table recovery script.
		* general_conf			-- All-in-one config file's and config reader class folder.
    	* setup.py				-- Setuptools Setup file.
    	* autoxtrabackup.py		-- Commandline Tool provider script.
    	* /etc/bck.conf         -- Config file will be created from general_conf/bck.conf

============


Available Options:
-----------------
    Usage: autoxtrabackup [OPTIONS]

    Options:
      --prepare                       Prepare/recover backups.
      --backup                        Take full and incremental backups.
      --partial                       Recover specified table (partial recovery).
      --version                       Version information.
      --defaults_file TEXT            Read options from the given file
      -v, --verbose                   Be verbose (print to console)
      -l, --log [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                      Set log level
      --help                          Show this message and exit.


Usage:
-----
        1. Clone repository to local directory. 
        2. Install using setup script.
        3. Edit /etc/bck.conf file reflecting your settings and use.
		
		
		* Please see Demo Usage Video.
		
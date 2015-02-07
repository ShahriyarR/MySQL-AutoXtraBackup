MySQL-backup
============

MySQL Backup and Prepare (including, per database, full, etc.) script written in Python 3.

Original Developers: Shahriyar Rzayev and Jahangir Shabiyev (/master_backup_script/backuper.py).
For community from Azerbaijan MySQL User Community: [MySQL Azerbaijan Community](http://mysql.az/about/).
For any question please ask: [Email](mailto:rzayev.sehriyar@gmail.com)

===========

Requirements:
-------------

    * Percona Xtrabackup (latest version)
    * Python 3 (tested version 3.3.2)
    * Official mysql-connector-python (tested versions 1.1.6, 2.0.2)
    * Python Click package (tested version 3.3)

===========

Preparing System
-----------------

    Installing dependencies:

        * yum install openssl openssl-devel zlib zlib-devel
        
    Installing latest XtraBackup:
        
        * yum install http://www.percona.com/downloads/percona-release/redhat/0.1-3/percona-release-0.1-3.noarch.rpm
        * yum install percona-xtrabackup

    Installing Python 3 from source:

        * wget https://www.dropbox.com/s/ctnzi65be0conqc/Python-3.3.2.tar.bz2?dl=0
        * tar -xvf Python-3.3.2.tar.bz2
        * cd Python-3.3.2
        
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
                
        * ./configure
        * make
        * make install
    
    
    Installing Python 3 packages:
        * pip3 install click
        * pip3 install --allow-external mysql-connector-python mysql-connector-python
    

        
Project Structure:
------------------
    
    XtraBackup is powerfull and open-source hot online backup tool  for MySQL from Percona.
    This script is using XtraBackup for full and incremental backups.
    Here is directory tree (default location is /home/MySQL-AutoXtraBackup):
        
        * backup_dir
        * master_backup_script
        * backup_prepare
        * partial_recovery
    
    backup_dir           -- The main folder for storing backups.
    master_backup_script -- Taking backups from Master server.(Write Server)
    backup_prepare       -- After taking backups you must prepare it for recovery (when needed). This script will do it automatically.

============

Partial Table Recovery:
------------------------
         
         partial_recovery -- Which is using already prepared backup and restore selected one table.
         

Usage:
-----
        Clone repository to /home directory and edit bck.conf files reflecting your settings.

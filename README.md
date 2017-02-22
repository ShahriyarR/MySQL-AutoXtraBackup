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
		

Sample Run results
-----------------

        #Taking very first full backup:
        
        $ sudo autoxtrabackup --backup -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
        2017-02-22 09:09:07 DEBUG    <pid.PidFile object at 0x7f39517c40e8> entering setup
        2017-02-22 09:09:07 DEBUG    <pid.PidFile object at 0x7f39517c40e8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:09:07 DEBUG    <pid.PidFile object at 0x7f39517c40e8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:09:07 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password=msandbox status --host=localhost --port=20192
        mysqladmin: [Warning] Using a password on the command line interface can be insecure.
        2017-02-22 09:09:07 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
        2017-02-22 09:09:07 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysql exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-OK
        2017-02-22 09:09:07 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
        2017-02-22 09:09:07 DEBUG    MySQL configuration file exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+OK
        2017-02-22 09:09:08 DEBUG    Xtrabackup exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-OK
        2017-02-22 09:09:08 DEBUG    Main backup directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK
        2017-02-22 09:09:08 DEBUG    Full Backup directory does not exist.+-+-+-+-+-+-+-+-+-+-+-+-OK
        2017-02-22 09:09:08 DEBUG    Creating full backup directory...+-+-+-+-+-+-+-+-+-++-+-+-+-+OK
        2017-02-22 09:09:08 DEBUG    Created+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
        2017-02-22 09:09:08 DEBUG    Increment directory does not exist.+-+-+-+-+-+-+-+-+-++-+-+-+OK
        2017-02-22 09:09:08 DEBUG    Creating increment backup directory.+-+-+-+-+-+-+-+-+-++-+-+-OK
        2017-02-22 09:09:08 DEBUG    Created
        2017-02-22 09:09:08 DEBUG    Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-OK
        2017-02-22 09:09:08 DEBUG    ###############################################################
        2017-02-22 09:09:08 DEBUG    #You have no backups : Taking very first Full Backup! - - - - #
        2017-02-22 09:09:08 DEBUG    ###############################################################
        2017-02-22 09:09:11 DEBUG    Trying to flush logs
        2017-02-22 09:09:11 DEBUG    Log flushing completed
        2017-02-22 09:09:11 DEBUG    The following backup command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password='msandbox'  --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-22_09-09-11 --backup --host=localhost --port=20192 --compress=quicklz --compress-chunk-size=65536 --compress-threads=4 --encrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --encrypt-threads=4 --encrypt-chunk-size=65536
        2017-02-22 09:09:11 DEBUG    Starting /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup
        2017-02-22 09:09:27 DEBUG    0222 09:09:27 completed OK!
        2017-02-22 09:09:27 DEBUG    <pid.PidFile object at 0x7f39517c40e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:09:27 DEBUG    <pid.PidFile object at 0x7f39517c40e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        
        #Taking first incremental backup:
        
        $ sudo autoxtrabackup --backup -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
        2017-02-22 09:31:44 DEBUG    <pid.PidFile object at 0x7f3e25c330e8> entering setup
        2017-02-22 09:31:44 DEBUG    <pid.PidFile object at 0x7f3e25c330e8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:31:44 DEBUG    <pid.PidFile object at 0x7f3e25c330e8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:31:44 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password=msandbox status --host=localhost --port=20192
        mysqladmin: [Warning] Using a password on the command line interface can be insecure.
        2017-02-22 09:31:44 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
        2017-02-22 09:31:44 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysql exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-OK
        2017-02-22 09:31:44 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
        2017-02-22 09:31:44 DEBUG    MySQL configuration file exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+OK
        2017-02-22 09:31:44 DEBUG    Xtrabackup exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-OK
        2017-02-22 09:31:44 DEBUG    Main backup directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK
        2017-02-22 09:31:44 DEBUG    Full Backup directory exists.+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+OK
        2017-02-22 09:31:44 DEBUG    Increment directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
        2017-02-22 09:31:44 DEBUG    Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-OK
        2017-02-22 09:31:44 DEBUG    ################################################################
        2017-02-22 09:31:44 DEBUG    You have a full backup that is less than 86400 seconds old. - -#
        2017-02-22 09:31:44 DEBUG    We will take an incremental one based on recent Full Backup - -#
        2017-02-22 09:31:44 DEBUG    ################################################################
        2017-02-22 09:31:47 DEBUG    Installed Server is MySQL, will continue as usual.
        2017-02-22 09:31:47 DEBUG    Applying workaround for LP #1444255
        2017-02-22 09:31:47 DEBUG    The following xbcrypt command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xbcrypt -d -k 'VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' -a AES256 -i /home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-22_09-09-11/xtrabackup_checkpoints.xbcrypt -o /home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-22_09-09-11/xtrabackup_checkpoints
        2017-02-22 09:31:47 DEBUG    
        2017-02-22 09:31:47 DEBUG    The following backup command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password='msandbox' --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-22_09-31-47 --incremental-basedir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-22_09-09-11 --backup --host=localhost --port=20192 --compress=quicklz --compress-chunk-size=65536 --compress-threads=4 --encrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --encrypt-threads=4 --encrypt-chunk-size=65536
        2017-02-22 09:32:02 DEBUG    0222 09:32:02 completed OK!
        2017-02-22 09:32:02 DEBUG    <pid.PidFile object at 0x7f3e25c330e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:32:02 DEBUG    <pid.PidFile object at 0x7f3e25c330e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        
        #Taking second incremental backup:
        
        $ sudo autoxtrabackup --backup -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
        2017-02-22 09:32:56 DEBUG    <pid.PidFile object at 0x7f1edc7b90e8> entering setup
        2017-02-22 09:32:56 DEBUG    <pid.PidFile object at 0x7f1edc7b90e8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:32:56 DEBUG    <pid.PidFile object at 0x7f1edc7b90e8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:32:56 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password=msandbox status --host=localhost --port=20192
        mysqladmin: [Warning] Using a password on the command line interface can be insecure.
        2017-02-22 09:32:56 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
        2017-02-22 09:32:56 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysql exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-OK
        2017-02-22 09:32:56 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
        2017-02-22 09:32:56 DEBUG    MySQL configuration file exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+OK
        2017-02-22 09:32:56 DEBUG    Xtrabackup exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-OK
        2017-02-22 09:32:56 DEBUG    Main backup directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK
        2017-02-22 09:32:56 DEBUG    Full Backup directory exists.+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+OK
        2017-02-22 09:32:56 DEBUG    Increment directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
        2017-02-22 09:32:56 DEBUG    Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-OK
        2017-02-22 09:32:56 DEBUG    ################################################################
        2017-02-22 09:32:56 DEBUG    You have a full backup that is less than 86400 seconds old. - -#
        2017-02-22 09:32:56 DEBUG    We will take an incremental one based on recent Full Backup - -#
        2017-02-22 09:32:56 DEBUG    ################################################################
        2017-02-22 09:32:59 DEBUG    Installed Server is MySQL, will continue as usual.
        2017-02-22 09:32:59 DEBUG    Applying workaround for LP #1444255
        2017-02-22 09:32:59 DEBUG    The following xbcrypt command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xbcrypt -d -k 'VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' -a AES256 -i /home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-22_09-31-47/xtrabackup_checkpoints.xbcrypt -o /home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-22_09-31-47/xtrabackup_checkpoints
        2017-02-22 09:32:59 DEBUG    
        2017-02-22 09:32:59 DEBUG    The following backup command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password='msandbox'  --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-22_09-32-59 --incremental-basedir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-22_09-31-47 --backup --host=localhost --port=20192 --compress=quicklz --compress_chunk_size=65536 --encrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --encrypt-threads=4 --encrypt-chunk-size=65536
        2017-02-22 09:33:14 DEBUG    0222 09:33:14 completed OK!
        2017-02-22 09:33:14 DEBUG    <pid.PidFile object at 0x7f1edc7b90e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:33:14 DEBUG    <pid.PidFile object at 0x7f1edc7b90e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        
        
        #Preparing 1 full 2 incremental backups:
        
        $ sudo autoxtrabackup --prepare -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
        2017-02-22 09:34:24 DEBUG    <pid.PidFile object at 0x7f4e4dec40e8> entering setup
        2017-02-22 09:34:24 DEBUG    <pid.PidFile object at 0x7f4e4dec40e8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:34:24 DEBUG    <pid.PidFile object at 0x7f4e4dec40e8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:34:24 DEBUG    Installed Server is MySQL, will continue as usual.
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        
        Preparing full/inc backups!
        What do you want to do?
        1. Prepare Backups and keep for future usage. NOTE('Once Prepared Backups Can not be prepared Again')
        2. Prepare Backups and restore/recover/copy-back immediately
        3. Just copy-back previously prepared backups
        Please Choose one of options and type 1 or 2 or 3: 1
        
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        2017-02-22 09:34:35 DEBUG    ####################################################################################################
        2017-02-22 09:34:35 DEBUG    You have Incremental backups. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#
        2017-02-22 09:34:38 DEBUG    Preparing Full backup 1 time. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#
        Final prepare,will occur after preparing all inc backups - - - - - - - - - - - - - - - - -  - - - -#
        2017-02-22 09:34:38 DEBUG    ####################################################################################################
        2017-02-22 09:34:41 DEBUG    Trying to decrypt backup
        2017-02-22 09:34:41 DEBUG    Running decrypt command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-22_09-09-11 --remove-original
        2017-02-22 09:34:42 DEBUG    0222 09:34:42 completed OK!
        2017-02-22 09:34:42 DEBUG    Decrypted!
        2017-02-22 09:34:42 DEBUG    Trying to decompress backup
        2017-02-22 09:34:42 DEBUG    Running decompress command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decompress=TRUE --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-22_09-09-11 --remove-original
        2017-02-22 09:34:43 DEBUG    0222 09:34:43 completed OK!
        2017-02-22 09:34:43 DEBUG    Decompressed
        2017-02-22 09:34:43 DEBUG    Running prepare command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --prepare --apply-log-only --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-22_09-09-11
        2017-02-22 09:34:45 DEBUG    0222 09:34:45 completed OK!
        2017-02-22 09:34:45 DEBUG    ####################################################################################################
        2017-02-22 09:34:45 DEBUG    Preparing Incs: 
        2017-02-22 09:34:48 DEBUG    Preparing inc backups in sequence. inc backup dir/name is 2017-02-22_09-31-47
        2017-02-22 09:34:48 DEBUG    ####################################################################################################
        2017-02-22 09:34:51 DEBUG    Trying to decrypt backup
        2017-02-22 09:34:51 DEBUG    Running decrypt command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-22_09-31-47 --remove-original
        2017-02-22 09:34:52 DEBUG    0222 09:34:52 completed OK!
        2017-02-22 09:34:52 DEBUG    Decrypted!
        2017-02-22 09:34:52 DEBUG    Trying to decompress backup
        2017-02-22 09:34:52 DEBUG    Running decompress command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decompress=TRUE --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-22_09-31-47 --remove-original
        2017-02-22 09:34:52 DEBUG    0222 09:34:52 completed OK!
        2017-02-22 09:34:52 DEBUG    Decompressed
        2017-02-22 09:34:52 DEBUG    Running prepare command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --prepare --apply-log-only --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-22_09-09-11 --incremental-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-22_09-31-47
        2017-02-22 09:35:02 DEBUG    0222 09:35:02 completed OK!
        2017-02-22 09:35:02 DEBUG    ####################################################################################################
        2017-02-22 09:35:02 DEBUG    Preparing last incremental backup, inc backup dir/name is 2017-02-22_09-32-59
        2017-02-22 09:35:02 DEBUG    ####################################################################################################
        2017-02-22 09:35:05 DEBUG    Trying to decrypt backup
        2017-02-22 09:35:05 DEBUG    Running decrypt command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-22_09-32-59 --remove-original
        2017-02-22 09:35:06 DEBUG    0222 09:35:06 completed OK!
        2017-02-22 09:35:06 DEBUG    Decrypted!
        2017-02-22 09:35:06 DEBUG    Trying to decompress backup
        2017-02-22 09:35:06 DEBUG    Running decompress command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decompress=TRUE --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-22_09-32-59 --remove-original
        2017-02-22 09:35:06 DEBUG    0222 09:35:06 completed OK!
        2017-02-22 09:35:06 DEBUG    Decompressed
        2017-02-22 09:35:06 DEBUG    Running prepare command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --prepare --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-22_09-09-11 --incremental-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-22_09-32-59
        2017-02-22 09:35:19 DEBUG    0222 09:35:19 completed OK!
        2017-02-22 09:35:19 DEBUG    ####################################################################################################
        2017-02-22 09:35:19 DEBUG    The end of the Prepare Stage. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#
        2017-02-22 09:35:19 DEBUG    ####################################################################################################
        2017-02-22 09:35:22 DEBUG    <pid.PidFile object at 0x7f4e4dec40e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:35:22 DEBUG    <pid.PidFile object at 0x7f4e4dec40e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        
        # Partial recovery of table after dropping database:
        
         > drop database dbtest;
         Query OK, 1 row affected (0.24 sec)
         
        [shahriyar.rzaev@qaserver-04 ~]$ sudo autoxtrabackup --partial -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
        2017-02-22 09:55:19 DEBUG    <pid.PidFile object at 0x7f27674da0e8> entering setup
        2017-02-22 09:55:19 DEBUG    <pid.PidFile object at 0x7f27674da0e8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:55:19 DEBUG    <pid.PidFile object at 0x7f27674da0e8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:55:19 DEBUG    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        Type Database name: dbtest
        Type Table name: t1
        2017-02-22 09:55:24 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password=msandbox status --host=localhost --port=20192
        mysqladmin: [Warning] Using a password on the command line interface can be insecure.
        2017-02-22 09:55:24 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
        2017-02-22 09:55:24 DEBUG    Checking if innodb_file_per_table is enabled
        2017-02-22 09:55:24 DEBUG    innodb_file_per_table is enabled!
        2017-02-22 09:55:24 DEBUG    Checking MySQL version
        2017-02-22 09:55:24 DEBUG    MySQL Version is, 5.7.17-11-log
        2017-02-22 09:55:24 DEBUG    You have correct version of MySQL
        2017-02-22 09:55:24 DEBUG    Checking if database exists in MySQL
        2017-02-22 09:55:24 DEBUG    There is no such database!
        2017-02-22 09:55:24 DEBUG    Create Specified Database in MySQL Server, before restoring single table
        We can create it for you do you want? (yes/no): yes
        2017-02-22 09:55:31 DEBUG    Creating specified database
        2017-02-22 09:55:31 DEBUG    dbtest database created
        2017-02-22 09:55:31 DEBUG    Checking if table exists in MySQL Server
        2017-02-22 09:55:31 DEBUG    Table does not exist in MySQL Server.
        2017-02-22 09:55:31 DEBUG    You can not restore table, with not existing tablespace file(.ibd)!
        2017-02-22 09:55:31 DEBUG    We will try to extract table create statement from .frm file, from backup folder
        2017-02-22 09:55:31 DEBUG    Running mysqlfrm tool
        2017-02-22 09:55:31 DEBUG    Success
        2017-02-22 09:55:32 DEBUG    Table Created from .frm file!
        2017-02-22 09:55:32 DEBUG    Applying write lock!
        2017-02-22 09:55:32 DEBUG    Locked
        2017-02-22 09:55:32 DEBUG    Discarding tablespace
        2017-02-22 09:55:32 DEBUG    Tablespace discarded successfully
        2017-02-22 09:55:32 DEBUG    Copying .ibd file back
        2017-02-22 09:55:32 DEBUG    Running chown command!
        2017-02-22 09:55:32 DEBUG    Chown command completed
        2017-02-22 09:55:32 DEBUG    Importing Tablespace!
        2017-02-22 09:55:32 DEBUG    Tablespace imported
        2017-02-22 09:55:32 DEBUG    Unlocking tables!
        2017-02-22 09:55:32 DEBUG    Unlocked!
        2017-02-22 09:55:32 DEBUG    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        2017-02-22 09:55:32 DEBUG    Table Recovered! ...-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        2017-02-22 09:55:32 DEBUG    <pid.PidFile object at 0x7f27674da0e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:55:32 DEBUG    <pid.PidFile object at 0x7f27674da0e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        
        > select * from dbtest.t1;
        +----+
        | id |
        +----+
        |  1 |
        |  1 |
        |  2 |
        |  1 |
        |  2 |
        |  3 |
        +----+
        6 rows in set (0.00 sec)
        
        # Partial recovery after dropping table:
        
        > drop table t1;
        Query OK, 0 rows affected (0.25 sec)
        
        
        $ sudo autoxtrabackup --partial -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
        2017-02-22 10:00:53 DEBUG    <pid.PidFile object at 0x7fdf6276a0e8> entering setup
        2017-02-22 10:00:53 DEBUG    <pid.PidFile object at 0x7fdf6276a0e8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 10:00:53 DEBUG    <pid.PidFile object at 0x7fdf6276a0e8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 10:00:53 DEBUG    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        Type Database name: dbtest
        Type Table name: t1
        2017-02-22 10:00:56 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password=msandbox status --host=localhost --port=20192
        mysqladmin: [Warning] Using a password on the command line interface can be insecure.
        2017-02-22 10:00:56 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
        2017-02-22 10:00:56 DEBUG    Checking if innodb_file_per_table is enabled
        2017-02-22 10:00:56 DEBUG    innodb_file_per_table is enabled!
        2017-02-22 10:00:56 DEBUG    Checking MySQL version
        2017-02-22 10:00:56 DEBUG    MySQL Version is, 5.7.17-11-log
        2017-02-22 10:00:56 DEBUG    You have correct version of MySQL
        2017-02-22 10:00:56 DEBUG    Checking if database exists in MySQL
        2017-02-22 10:00:57 DEBUG    Database exists!
        2017-02-22 10:00:57 DEBUG    Checking if table exists in MySQL Server
        2017-02-22 10:00:57 DEBUG    Table does not exist in MySQL Server.
        2017-02-22 10:00:57 DEBUG    You can not restore table, with not existing tablespace file(.ibd)!
        2017-02-22 10:00:57 DEBUG    We will try to extract table create statement from .frm file, from backup folder
        2017-02-22 10:00:57 DEBUG    Running mysqlfrm tool
        2017-02-22 10:00:57 DEBUG    Success
        2017-02-22 10:00:57 DEBUG    Table Created from .frm file!
        2017-02-22 10:00:57 DEBUG    Applying write lock!
        2017-02-22 10:00:57 DEBUG    Locked
        2017-02-22 10:00:57 DEBUG    Discarding tablespace
        2017-02-22 10:00:57 DEBUG    Tablespace discarded successfully
        2017-02-22 10:00:57 DEBUG    Copying .ibd file back
        2017-02-22 10:00:57 DEBUG    Running chown command!
        2017-02-22 10:00:57 DEBUG    Chown command completed
        2017-02-22 10:00:58 DEBUG    Importing Tablespace!
        2017-02-22 10:00:58 DEBUG    Tablespace imported
        2017-02-22 10:00:58 DEBUG    Unlocking tables!
        2017-02-22 10:00:58 DEBUG    Unlocked!
        2017-02-22 10:00:58 DEBUG    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        2017-02-22 10:00:58 DEBUG    Table Recovered! ...-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        2017-02-22 10:00:58 DEBUG    <pid.PidFile object at 0x7fdf6276a0e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 10:00:58 DEBUG    <pid.PidFile object at 0x7fdf6276a0e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        
        > select * from dbtest.t1;
        +----+
        | id |
        +----+
        |  1 |
        |  1 |
        |  2 |
        |  1 |
        |  2 |
        |  3 |
        +----+
        6 rows in set (0.00 sec)

        
        # Partial recovery after deleting table data:
        
        > delete from t1;
        Query OK, 6 rows affected (0.34 sec)

        
        [shahriyar.rzaev@qaserver-04 ~]$ sudo autoxtrabackup --partial -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
        2017-02-22 09:58:48 DEBUG    <pid.PidFile object at 0x7f0b6a5140e8> entering setup
        2017-02-22 09:58:48 DEBUG    <pid.PidFile object at 0x7f0b6a5140e8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:58:48 DEBUG    <pid.PidFile object at 0x7f0b6a5140e8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:58:48 DEBUG    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        Type Database name: dbtest
        Type Table name: t1
        2017-02-22 09:58:55 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password=msandbox status --host=localhost --port=20192
        mysqladmin: [Warning] Using a password on the command line interface can be insecure.
        2017-02-22 09:58:55 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
        2017-02-22 09:58:55 DEBUG    Checking if innodb_file_per_table is enabled
        2017-02-22 09:58:55 DEBUG    innodb_file_per_table is enabled!
        2017-02-22 09:58:55 DEBUG    Checking MySQL version
        2017-02-22 09:58:55 DEBUG    MySQL Version is, 5.7.17-11-log
        2017-02-22 09:58:55 DEBUG    You have correct version of MySQL
        2017-02-22 09:58:55 DEBUG    Checking if database exists in MySQL
        2017-02-22 09:58:55 DEBUG    Database exists!
        2017-02-22 09:58:55 DEBUG    Checking if table exists in MySQL Server
        2017-02-22 09:58:55 DEBUG    Table exists in MySQL Server.
        2017-02-22 09:58:55 DEBUG    Applying write lock!
        2017-02-22 09:58:55 DEBUG    Locked
        2017-02-22 09:58:55 DEBUG    Discarding tablespace
        2017-02-22 09:58:55 DEBUG    Tablespace discarded successfully
        2017-02-22 09:58:55 DEBUG    Copying .ibd file back
        2017-02-22 09:58:55 DEBUG    Running chown command!
        2017-02-22 09:58:55 DEBUG    Chown command completed
        2017-02-22 09:58:56 DEBUG    Importing Tablespace!
        2017-02-22 09:58:56 DEBUG    Tablespace imported
        2017-02-22 09:58:56 DEBUG    Unlocking tables!
        2017-02-22 09:58:56 DEBUG    Unlocked!
        2017-02-22 09:58:56 DEBUG    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        2017-02-22 09:58:56 DEBUG    Table Recovered! ...-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        2017-02-22 09:58:56 DEBUG    <pid.PidFile object at 0x7f0b6a5140e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-22 09:58:56 DEBUG    <pid.PidFile object at 0x7f0b6a5140e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

        
        > select * from dbtest.t1;
        +----+
        | id |
        +----+
        |  1 |
        |  1 |
        |  2 |
        |  1 |
        |  2 |
        |  3 |
        +----+
        6 rows in set (0.02 sec)

		
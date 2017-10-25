Advanced features
=================

Compressed backups:
-------------------

To enable compression support just uncomment the options under
[Compress] category inside main configuration file:

::

    [Compress]
    #Optional
    #Enable only if you want to use compression.
    compress=quicklz
    compress_chunk_size=65536
    compress_threads=4
    decompress=TRUE
    #Enable if you want to remove .qp files after decompression.(Not available yet, will be released with XB 2.3.7 and 2.4.6)
    #remove_original=FALSE

Example run of compression enabled backup:

::


    $ sudo autoxtrabackup --backup -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
    2017-02-24 18:15:55 DEBUG    <pid.PidFile object at 0x7f44cb96ee08> entering setup
    2017-02-24 18:15:55 DEBUG    <pid.PidFile object at 0x7f44cb96ee08> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 18:15:55 DEBUG    <pid.PidFile object at 0x7f44cb96ee08> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 18:15:55 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password=msandbox status --host=localhost --port=20192
    mysqladmin: [Warning] Using a password on the command line interface can be insecure.
    2017-02-24 18:15:55 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
    2017-02-24 18:15:55 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysql exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-OK
    2017-02-24 18:15:55 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
    2017-02-24 18:15:55 DEBUG    MySQL configuration file exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+OK
    2017-02-24 18:15:55 DEBUG    Xtrabackup exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-OK
    2017-02-24 18:15:55 DEBUG    Main backup directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK
    2017-02-24 18:15:55 DEBUG    Full Backup directory does not exist.+-+-+-+-+-+-+-+-+-+-+-+-OK
    2017-02-24 18:15:55 DEBUG    Creating full backup directory...+-+-+-+-+-+-+-+-+-++-+-+-+-+OK
    2017-02-24 18:15:55 DEBUG    Created+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
    2017-02-24 18:15:55 DEBUG    Increment directory does not exist.+-+-+-+-+-+-+-+-+-++-+-+-+OK
    2017-02-24 18:15:55 DEBUG    Creating increment backup directory.+-+-+-+-+-+-+-+-+-++-+-+-OK
    2017-02-24 18:15:55 DEBUG    Created
    2017-02-24 18:15:55 DEBUG    Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-OK
    2017-02-24 18:15:55 DEBUG    ###############################################################
    2017-02-24 18:15:55 DEBUG    #You have no backups : Taking very first Full Backup! - - - - #
    2017-02-24 18:15:55 DEBUG    ###############################################################
    2017-02-24 18:15:58 DEBUG    Trying to flush logs
    2017-02-24 18:15:59 DEBUG    Log flushing completed
    2017-02-24 18:15:59 DEBUG    The following backup command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password='msandbox'  --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-24_18-15-59 --backup --host=localhost --port=20192 --compress=quicklz --compress-chunk-size=65536 --compress-threads=4
    2017-02-24 18:15:59 DEBUG    Starting /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup
    2017-02-24 18:16:12 DEBUG    0224 18:16:12 completed OK!
    2017-02-24 18:16:12 DEBUG    <pid.PidFile object at 0x7f44cb96ee08> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 18:16:12 DEBUG    <pid.PidFile object at 0x7f44cb96ee08> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

Take a look at backup folder:

::

    [shahriyar.rzaev@qaserver-04 ps_5.7_master]$ sudo ls full/2017-02-24_18-15-59/
    backup-my.cnf.qp  dbtest  ib_buffer_pool.qp  ibdata1.qp  mysql  performance_schema  sys  test  xtrabackup_checkpoints  xtrabackup_info.qp  xtrabackup_logfile.qp

Encrypted backups
-----------------

To enable encryption support uncomment the options under [Encryption]
category:

::

    [Encrypt]
    #Optional
    #Enable only if you want to create encrypted backups
    xbcrypt=/home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xbcrypt
    encrypt=AES256
    # Please note that --encrypt-key and --encrypt-key-file are mutually exclusive
    encrypt_key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K'
    #encrypt_key_file=/path/to/file/with_encrypt_key
    encrypt_threads=4
    encrypt_chunk_size=65536
    decrypt=AES256
    #Enable if you want to remove .qp files after decompression.(Not available yet, will be released with XB 2.3.7 and 2.4.6)
    #remove_original=True

Then just run backup command:

::


    [shahriyar.rzaev@qaserver-04 ~]$ sudo autoxtrabackup --backup -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
    2017-02-24 18:45:53 DEBUG    <pid.PidFile object at 0x7f7d6b511e08> entering setup
    2017-02-24 18:45:53 DEBUG    <pid.PidFile object at 0x7f7d6b511e08> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 18:45:53 DEBUG    <pid.PidFile object at 0x7f7d6b511e08> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 18:45:53 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password=msandbox status --host=localhost --port=20192
    mysqladmin: [Warning] Using a password on the command line interface can be insecure.
    2017-02-24 18:45:53 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
    2017-02-24 18:45:53 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysql exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-OK
    2017-02-24 18:45:53 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
    2017-02-24 18:45:53 DEBUG    MySQL configuration file exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+OK
    2017-02-24 18:45:53 DEBUG    Xtrabackup exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-OK
    2017-02-24 18:45:53 DEBUG    Main backup directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK
    2017-02-24 18:45:53 DEBUG    Full Backup directory does not exist.+-+-+-+-+-+-+-+-+-+-+-+-OK
    2017-02-24 18:45:53 DEBUG    Creating full backup directory...+-+-+-+-+-+-+-+-+-++-+-+-+-+OK
    2017-02-24 18:45:53 DEBUG    Created+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
    2017-02-24 18:45:53 DEBUG    Increment directory does not exist.+-+-+-+-+-+-+-+-+-++-+-+-+OK
    2017-02-24 18:45:53 DEBUG    Creating increment backup directory.+-+-+-+-+-+-+-+-+-++-+-+-OK
    2017-02-24 18:45:53 DEBUG    Created
    2017-02-24 18:45:53 DEBUG    Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-OK
    2017-02-24 18:45:53 DEBUG    ###############################################################
    2017-02-24 18:45:53 DEBUG    #You have no backups : Taking very first Full Backup! - - - - #
    2017-02-24 18:45:53 DEBUG    ###############################################################
    2017-02-24 18:45:56 DEBUG    Trying to flush logs
    2017-02-24 18:45:57 DEBUG    Log flushing completed
    2017-02-24 18:45:57 DEBUG    The following backup command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password='msandbox'  --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-24_18-45-57 --backup --host=localhost --port=20192 --compress=quicklz --compress-chunk-size=65536 --compress-threads=4 --encrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --encrypt-threads=4 --encrypt-chunk-size=65536
    2017-02-24 18:45:57 DEBUG    Starting /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup
    2017-02-24 18:47:09 DEBUG    0224 18:47:09 completed OK!
    2017-02-24 18:47:09 DEBUG    <pid.PidFile object at 0x7f7d6b511e08> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 18:47:09 DEBUG    <pid.PidFile object at 0x7f7d6b511e08> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

Check backup directory:

::


    [shahriyar.rzaev@qaserver-04 ps_5.7_master]$ ls full/2017-02-24_18-45-57/
    backup-my.cnf.qp.xbcrypt  ib_buffer_pool.qp.xbcrypt  mysql               sys   xtrabackup_checkpoints.xbcrypt  xtrabackup_logfile.qp.xbcrypt
    dbtest                    ibdata1.qp.xbcrypt         performance_schema  test  xtrabackup_info.qp.xbcrypt

How about incremental backups? Let's take an incremental backup:

::


    $ sudo autoxtrabackup --backup -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
    2017-02-24 18:58:08 DEBUG    <pid.PidFile object at 0x7f566623ee08> entering setup
    2017-02-24 18:58:08 DEBUG    <pid.PidFile object at 0x7f566623ee08> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 18:58:08 DEBUG    <pid.PidFile object at 0x7f566623ee08> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 18:58:08 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password=msandbox status --host=localhost --port=20192
    mysqladmin: [Warning] Using a password on the command line interface can be insecure.
    2017-02-24 18:58:08 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
    2017-02-24 18:58:08 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysql exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-OK
    2017-02-24 18:58:08 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
    2017-02-24 18:58:08 DEBUG    MySQL configuration file exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+OK
    2017-02-24 18:58:08 DEBUG    Xtrabackup exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-OK
    2017-02-24 18:58:08 DEBUG    Main backup directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK
    2017-02-24 18:58:08 DEBUG    Full Backup directory exists.+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+OK
    2017-02-24 18:58:08 DEBUG    Increment directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
    2017-02-24 18:58:08 DEBUG    Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-OK
    2017-02-24 18:58:08 DEBUG    ################################################################
    2017-02-24 18:58:08 DEBUG    You have a full backup that is less than 86400 seconds old. - -#
    2017-02-24 18:58:08 DEBUG    We will take an incremental one based on recent Full Backup - -#
    2017-02-24 18:58:08 DEBUG    ################################################################
    2017-02-24 18:58:11 DEBUG    Installed Server is MySQL, will continue as usual.
    2017-02-24 18:58:11 DEBUG    Applying workaround for LP #1444255
    2017-02-24 18:58:11 DEBUG    The following xbcrypt command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xbcrypt -d -k 'VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' -a AES256 -i /home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-24_18-45-57/xtrabackup_checkpoints.xbcrypt -o /home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-24_18-45-57/xtrabackup_checkpoints
    2017-02-24 18:58:11 DEBUG
    2017-02-24 18:58:11 DEBUG    The following backup command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password='msandbox' --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-24_18-58-11 --incremental-basedir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-24_18-45-57 --backup --host=localhost --port=20192 --compress=quicklz --compress-chunk-size=65536 --compress-threads=4 --encrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --encrypt-threads=4 --encrypt-chunk-size=65536
    2017-02-24 18:58:27 DEBUG    0224 18:58:27 completed OK!
    2017-02-24 18:58:27 DEBUG    <pid.PidFile object at 0x7f566623ee08> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 18:58:27 DEBUG    <pid.PidFile object at 0x7f566623ee08> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

As you see, the tool first decrypted ``xtrabackup_checkpoints.xbcrypt``
file and then took the incremental backup.

Partial backups
---------------

It is possible to take partial full and incremental backups. The idea is, to take specified table(or database) as full backup,
then to take incremental backups based on this one table.
You can achieve this by enabling ``partial_list`` option from config file:


::

    [Backup]
    #Optional: set pid directory
    pid_dir=/tmp/MySQL-AutoXtraBackup
    #Optional: set warning if pid of backup us running for longer than X
    pid_runtime_warning=2 Hours
    backupdir=/home/backup_dir
    backup_tool=/usr/bin/xtrabackup
    xtra_prepare=--apply-log-only
    #Optional: pass additional options
    #xtra_options=--binlog-info=ON --galera-info
    #Optional: set archive and rotation
    #archive_dir=/home/backup_archives
    #full_backup_interval=1 day
    #max_archive_size=100GiB
    #max_archive_duration=4 Days
    #Optional WARNING(Enable this if you want to take partial backups). Specify database names or table names.
    #partial_list=test.t1 test.t2 dbtest


Sample run of full backup:

::

    $ sudo autoxtrabackup --backup -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
    2017-03-06 10:51:32 DEBUG    <pid.PidFile object at 0x7f129b9a90e8> entering setup
    2017-03-06 10:51:32 DEBUG    <pid.PidFile object at 0x7f129b9a90e8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-03-06 10:51:32 DEBUG    <pid.PidFile object at 0x7f129b9a90e8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-03-06 10:51:32 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password=msandbox status --host=localhost --port=20192
    mysqladmin: [Warning] Using a password on the command line interface can be insecure.
    2017-03-06 10:51:32 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
    2017-03-06 10:51:32 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysql exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-OK
    2017-03-06 10:51:32 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
    2017-03-06 10:51:32 DEBUG    MySQL configuration file exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+OK
    2017-03-06 10:51:32 DEBUG    Xtrabackup exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-OK
    2017-03-06 10:51:32 DEBUG    Main backup directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK
    2017-03-06 10:51:32 DEBUG    Full Backup directory does not exist.+-+-+-+-+-+-+-+-+-+-+-+-OK
    2017-03-06 10:51:32 DEBUG    Creating full backup directory...+-+-+-+-+-+-+-+-+-++-+-+-+-+OK
    2017-03-06 10:51:32 DEBUG    Created+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
    2017-03-06 10:51:32 DEBUG    Increment directory does not exist.+-+-+-+-+-+-+-+-+-++-+-+-+OK
    2017-03-06 10:51:32 DEBUG    Creating increment backup directory.+-+-+-+-+-+-+-+-+-++-+-+-OK
    2017-03-06 10:51:32 DEBUG    Created
    2017-03-06 10:51:32 DEBUG    Archive folder directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK
    2017-03-06 10:51:32 DEBUG    Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-OK
    2017-03-06 10:51:32 DEBUG    ###############################################################
    2017-03-06 10:51:32 DEBUG    #You have no backups : Taking very first Full Backup! - - - - #
    2017-03-06 10:51:32 DEBUG    ###############################################################
    2017-03-06 10:51:35 DEBUG    Trying to flush logs
    2017-03-06 10:51:36 DEBUG    Log flushing completed
    2017-03-06 10:51:36 WARNING  Partial Backup is enabled!
    2017-03-06 10:51:36 DEBUG    The following backup command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password='msandbox'  --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-03-06_10-51-36 --backup --host=localhost --port=20192 --compress=quicklz --compress-chunk-size=65536 --compress-threads=4 --encrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --encrypt-threads=4 --encrypt-chunk-size=65536 --databases="dbtest.t1"
    2017-03-06 10:51:36 DEBUG    Starting /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup
    2017-03-06 10:51:38 DEBUG    0306 10:51:38 completed OK!
    2017-03-06 10:51:38 DEBUG    <pid.PidFile object at 0x7f129b9a90e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-03-06 10:51:38 DEBUG    <pid.PidFile object at 0x7f129b9a90e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

Notice that backup command has changed (see ``--databases`` option):

::

    /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup
    --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password='msandbox'
    --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-03-06_10-51-36 --backup --host=localhost --port=20192 --compress=quicklz
    --compress-chunk-size=65536 --compress-threads=4 --encrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K'
    --encrypt-threads=4 --encrypt-chunk-size=65536
    --databases="dbtest.t1"

In the same way you can take incremental backup of this table:

::

    $ sudo autoxtrabackup --backup -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
    2017-03-06 11:59:59 DEBUG    <pid.PidFile object at 0x7fab09cad0e8> entering setup
    2017-03-06 11:59:59 DEBUG    <pid.PidFile object at 0x7fab09cad0e8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-03-06 11:59:59 DEBUG    <pid.PidFile object at 0x7fab09cad0e8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-03-06 11:59:59 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password=msandbox status --host=localhost --port=20192
    mysqladmin: [Warning] Using a password on the command line interface can be insecure.
    2017-03-06 11:59:59 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
    2017-03-06 11:59:59 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysql exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-OK
    2017-03-06 11:59:59 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
    2017-03-06 11:59:59 DEBUG    MySQL configuration file exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+OK
    2017-03-06 11:59:59 DEBUG    Xtrabackup exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-OK
    2017-03-06 11:59:59 DEBUG    Main backup directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK
    2017-03-06 11:59:59 DEBUG    Full Backup directory exists.+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+OK
    2017-03-06 11:59:59 DEBUG    Increment directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
    2017-03-06 11:59:59 DEBUG    Archive folder directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK
    2017-03-06 11:59:59 DEBUG    Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-OK
    2017-03-06 11:59:59 DEBUG    ################################################################
    2017-03-06 11:59:59 DEBUG    You have a full backup that is less than 86400 seconds old. - -#
    2017-03-06 11:59:59 DEBUG    We will take an incremental one based on recent Full Backup - -#
    2017-03-06 11:59:59 DEBUG    ################################################################
    2017-03-06 12:00:02 DEBUG    Installed Server is MySQL, will continue as usual.
    2017-03-06 12:00:02 DEBUG    Applying workaround for LP #1444255
    2017-03-06 12:00:02 DEBUG    The following xbcrypt command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xbcrypt -d -k 'VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' -a AES256 -i /home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-03-06_10-51-36/xtrabackup_checkpoints.xbcrypt -o /home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-03-06_10-51-36/xtrabackup_checkpoints
    2017-03-06 12:00:02 DEBUG
    2017-03-06 12:00:02 WARNING  Partial Backup is enabled!
    2017-03-06 12:00:02 DEBUG    The following backup command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password='msandbox' --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-03-06_12-00-02 --incremental-basedir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-03-06_10-51-36 --backup --host=localhost --port=20192 --compress=quicklz --compress-chunk-size=65536 --compress-threads=4 --encrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --encrypt-threads=4 --encrypt-chunk-size=65536 --databases="dbtest.t1"
    2017-03-06 12:00:04 DEBUG    0306 12:00:04 completed OK!
    2017-03-06 12:00:04 DEBUG    <pid.PidFile object at 0x7fab09cad0e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-03-06 12:00:04 DEBUG    <pid.PidFile object at 0x7fab09cad0e8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

The prepare process is the same as ordinary prepare, just run autoxtrabackup with ``--prepare`` option, you can even restore this single table using ``--partial`` option.

Decompressing and Decrypting backups
------------------------------------

We took Compressed and Encrypted backups.
It is time to prepare them.
AutoXtraBackup will prepare all backups automatically, by first decrypting then
decompressing step-by-step.

We have 2 incremental backups:

::

    [shahriyar.rzaev@qaserver-04 ps_5.7_master]$ ls full/
    2017-02-24_18-45-57
    [shahriyar.rzaev@qaserver-04 ps_5.7_master]$ ls inc/
    2017-02-24_18-58-11  2017-02-24_19-02-50

Let's prepare them:


::


    $ sudo autoxtrabackup --prepare -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
    2017-02-24 19:07:33 DEBUG    <pid.PidFile object at 0x7faca5716e08> entering setup
    2017-02-24 19:07:33 DEBUG    <pid.PidFile object at 0x7faca5716e08> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 19:07:33 DEBUG    <pid.PidFile object at 0x7faca5716e08> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 19:07:33 DEBUG    Installed Server is MySQL, will continue as usual.
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-

    Preparing full/inc backups!
    What do you want to do?
    1. Prepare Backups and keep for future usage. NOTE('Once Prepared Backups Can not be prepared Again')
    2. Prepare Backups and restore/recover/copy-back immediately
    3. Just copy-back previously prepared backups
    Please Choose one of options and type 1 or 2 or 3: 1

    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
    2017-02-24 19:07:37 DEBUG    ####################################################################################################
    2017-02-24 19:07:37 DEBUG    You have Incremental backups. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#
    2017-02-24 19:07:40 DEBUG    Preparing Full backup 1 time. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#
    Final prepare,will occur after preparing all inc backups - - - - - - - - - - - - - - - - -  - - - -#
    2017-02-24 19:07:40 DEBUG    ####################################################################################################
    2017-02-24 19:07:43 DEBUG    Trying to decrypt backup
    2017-02-24 19:07:43 DEBUG    Running decrypt command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-24_18-45-57
    2017-02-24 19:07:44 DEBUG    0224 19:07:44 completed OK!
    2017-02-24 19:07:44 DEBUG    Decrypted!
    2017-02-24 19:07:44 DEBUG    Trying to decompress backup
    2017-02-24 19:07:44 DEBUG    Running decompress command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decompress=TRUE --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-24_18-45-57
    2017-02-24 19:07:45 DEBUG    0224 19:07:45 completed OK!
    2017-02-24 19:07:45 DEBUG    Decompressed
    2017-02-24 19:07:45 DEBUG    Running prepare command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --prepare --apply-log-only --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-24_18-45-57
    2017-02-24 19:07:47 DEBUG    0224 19:07:47 completed OK!
    2017-02-24 19:07:47 DEBUG    ####################################################################################################
    2017-02-24 19:07:47 DEBUG    Preparing Incs:
    2017-02-24 19:07:50 DEBUG    Preparing inc backups in sequence. inc backup dir/name is 2017-02-24_18-58-11
    2017-02-24 19:07:50 DEBUG    ####################################################################################################
    2017-02-24 19:07:53 DEBUG    Trying to decrypt backup
    2017-02-24 19:07:53 DEBUG    Running decrypt command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-24_18-58-11
    2017-02-24 19:07:53 DEBUG    0224 19:07:53 completed OK!
    2017-02-24 19:07:53 DEBUG    Decrypted!
    2017-02-24 19:07:53 DEBUG    Trying to decompress backup
    2017-02-24 19:07:53 DEBUG    Running decompress command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decompress=TRUE --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-24_18-58-11
    2017-02-24 19:07:54 DEBUG    0224 19:07:54 completed OK!
    2017-02-24 19:07:54 DEBUG    Decompressed
    2017-02-24 19:07:54 DEBUG    Running prepare command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --prepare --apply-log-only --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-24_18-45-57 --incremental-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-24_18-58-11
    2017-02-24 19:08:04 DEBUG    0224 19:08:04 completed OK!
    2017-02-24 19:08:04 DEBUG    ####################################################################################################
    2017-02-24 19:08:04 DEBUG    Preparing last incremental backup, inc backup dir/name is 2017-02-24_19-02-50
    2017-02-24 19:08:04 DEBUG    ####################################################################################################
    2017-02-24 19:08:07 DEBUG    Trying to decrypt backup
    2017-02-24 19:08:07 DEBUG    Running decrypt command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-24_19-02-50
    2017-02-24 19:08:08 DEBUG    0224 19:08:08 completed OK!
    2017-02-24 19:08:08 DEBUG    Decrypted!
    2017-02-24 19:08:08 DEBUG    Trying to decompress backup
    2017-02-24 19:08:08 DEBUG    Running decompress command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decompress=TRUE --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-24_19-02-50
    2017-02-24 19:08:08 DEBUG    0224 19:08:08 completed OK!
    2017-02-24 19:08:08 DEBUG    Decompressed
    2017-02-24 19:08:08 DEBUG    Running prepare command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --prepare --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-24_18-45-57 --incremental-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-24_19-02-50
    2017-02-24 19:08:21 DEBUG    0224 19:08:21 completed OK!
    2017-02-24 19:08:21 DEBUG    ####################################################################################################
    2017-02-24 19:08:21 DEBUG    The end of the Prepare Stage. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#
    2017-02-24 19:08:21 DEBUG    ####################################################################################################
    2017-02-24 19:08:24 DEBUG    <pid.PidFile object at 0x7faca5716e08> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 19:08:24 DEBUG    <pid.PidFile object at 0x7faca5716e08> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

That's it. All backups are first decrypted then decompressed and then
prepared.
You can also optionally enable ``--remove-original`` option to
remove ``.xbcrypt`` and ``.qp`` files from backup directory during prepare
process. Read about this option here -> `--remove-original <https://www.percona.com/doc/percona-xtrabackup/2.4/xtrabackup_bin/xbk_option_reference.html#cmdoption-xtrabackup-remove-original>`_


::

    [Compress]
    #Optional
    #Enable only if you want to use compression.
    compress=quicklz
    compress_chunk_size=65536
    compress_threads=4
    decompress=TRUE
    #Enable if you want to remove .qp files after decompression.
    remove_original=True

    [Encrypt]
    #Optional
    #Enable only if you want to create encrypted backups
    xbcrypt=/home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xbcrypt
    encrypt=AES256
    # Please note that --encrypt-key and --encrypt-key-file are mutually exclusive
    encrypt_key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K'
    #encrypt_key_file=/path/to/file/with_encrypt_key
    encrypt_threads=4
    encrypt_chunk_size=65536
    decrypt=AES256
    #Enable if you want to remove .xbcrypt files after decryption.
    remove_original=True



Restoring single table after drop
---------------------------------

Let's explain a bit, how we can restore single table from full backup?
This is the part of "Transportable Tablespace" concept which you can read more: `Transportable Tablespace <https://dev.mysql.com/doc/refman/5.7/en/tablespace-copying.html>`_

The basic idea is:

-  Discard available tablespace of table
-  Copy the .ibd file from backup to current database directory
-  Import tablespace
-  You have restored the table.

Previously we have mentioned about that, we can restore single table
after deleting data. The situation there, was quite clear because the
table structure was available(i.e table was not dropped).

The problem is getting interesting, if table was dropped or even the
whole database dropped. We should figure out how to find table structure
and create it.

The basic plan for this situation is:

-  Find the dropped table structure(i.e create statement)
-  Create dropped table again
-  Discard tablespace of newly created table
-  Copy the .ibd file from backup to current database directory
-  Import tablespace
-  You have restored the table.

I found a way,by using ``mysqlfrm`` tool for extracting create statement
from table's .frm file, which is stored in backup directory. So this is
also automated. Let's see it in action. We have a dbtest database and t1 table:

    ::

        > show tables from dbtest;
        +------------------+
        | Tables_in_dbtest |
        +------------------+
        | t1               |
        +------------------+
        1 row in set (0.02 sec)

Dropping the database:

    ::

        > drop database dbtest;
        Query OK, 1 row affected (1.08 sec)


Trying to restore t1 table: It will figure out that specified database is missing and will prompt to create it.

    ::


        $ sudo autoxtrabackup --partial -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
        2017-02-24 19:31:57 DEBUG    <pid.PidFile object at 0x7f7332952e08> entering setup
        2017-02-24 19:31:57 DEBUG    <pid.PidFile object at 0x7f7332952e08> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-24 19:31:57 DEBUG    <pid.PidFile object at 0x7f7332952e08> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-24 19:31:57 DEBUG    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        Type Database name: dbtest
        Type Table name: t1
        2017-02-24 19:32:02 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password=msandbox status --host=localhost --port=20192
        mysqladmin: [Warning] Using a password on the command line interface can be insecure.
        2017-02-24 19:32:02 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
        2017-02-24 19:32:02 DEBUG    Checking if innodb_file_per_table is enabled
        2017-02-24 19:32:02 DEBUG    innodb_file_per_table is enabled!
        2017-02-24 19:32:02 DEBUG    Checking MySQL version
        2017-02-24 19:32:03 DEBUG    MySQL Version is, 5.7.17-11-log
        2017-02-24 19:32:03 DEBUG    You have correct version of MySQL
        2017-02-24 19:32:03 DEBUG    Checking if database exists in MySQL
        2017-02-24 19:32:03 DEBUG    There is no such database!
        2017-02-24 19:32:03 DEBUG    Create Specified Database in MySQL Server, before restoring single table
        We can create it for you do you want? (yes/no): yes
        2017-02-24 19:33:09 DEBUG    Creating specified database
        2017-02-24 19:33:09 DEBUG    dbtest database created
        2017-02-24 19:33:09 DEBUG    Checking if table exists in MySQL Server
        2017-02-24 19:33:09 DEBUG    Table does not exist in MySQL Server.
        2017-02-24 19:33:09 DEBUG    You can not restore table, with not existing tablespace file(.ibd)!
        2017-02-24 19:33:09 DEBUG    We will try to extract table create statement from .frm file, from backup folder
        2017-02-24 19:33:09 DEBUG    Running mysqlfrm tool
        2017-02-24 19:33:10 DEBUG    Success
        2017-02-24 19:33:11 DEBUG    Table Created from .frm file!
        2017-02-24 19:33:11 DEBUG    Applying write lock!
        2017-02-24 19:33:11 DEBUG    Locked
        2017-02-24 19:33:11 DEBUG    Discarding tablespace
        2017-02-24 19:33:11 DEBUG    Tablespace discarded successfully
        2017-02-24 19:33:11 DEBUG    Copying .ibd file back
        2017-02-24 19:33:11 DEBUG    Running chown command!
        2017-02-24 19:33:11 DEBUG    Chown command completed
        2017-02-24 19:33:11 DEBUG    Importing Tablespace!
        2017-02-24 19:33:11 DEBUG    Tablespace imported
        2017-02-24 19:33:11 DEBUG    Unlocking tables!
        2017-02-24 19:33:11 DEBUG    Unlocked!
        2017-02-24 19:33:11 DEBUG    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        2017-02-24 19:33:11 DEBUG    Table Recovered! ...-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        2017-02-24 19:33:11 DEBUG    <pid.PidFile object at 0x7f7332952e08> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-02-24 19:33:11 DEBUG    <pid.PidFile object at 0x7f7332952e08> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

As you noticed, the ``mysqlfrm`` tool did the job and table is restored after drop:

    ::

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




Streaming backups - for now only for TEST purposes
--------------------------------------------------

With recent XtraBackup release, you can decrypt your streamed + encrypted backups on the fly.
Say, you took full backup as:

    ::

        xtrabackup --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_percona-server-5_7_17/master/my.sandbox.cnf
        --user=msandbox --password='msandbox'  --target-dir=/home/shahriyar.rzaev/backup_dir/ps_5.7_master/full/2017-04-24_14-43-50
        --backup --host=127.0.0.1 --port=20192 --compress=quicklz --compress-chunk-size=65536 --compress-threads=4
        --encrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --encrypt-threads=4
        --encrypt-chunk-size=65536 --binlog-info=AUTO --stream="xbstream" >
        /home/shahriyar.rzaev/backup_dir/ps_5.7_master/full/2017-04-24_14-43-50/full_backup.stream


As you noticed, there will be ``full_backup.stream`` file  inside full backup directory.
If you are going to take incremental backup based on full backup you can extract and decrypt streamed backup directly using ``xbstream``:

    ::

        xbstream -x --parallel=100 --decrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K'
        --encrypt-threads=4 <
        /home/shahriyar.rzaev/backup_dir/ps_5.7_master/full/2017-04-24_14-43-50/full_backup.stream -C /home/shahriyar.rzaev/backup_dir/ps_5.7_master/full/2017-04-24_14-43-50

        xtrabackup --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_percona-server-5_7_17/master/my.sandbox.cnf
        --user=msandbox --password='msandbox' --target-dir=/home/shahriyar.rzaev/backup_dir/ps_5.7_master/inc/2017-04-24_14-44-02
        --incremental-basedir=/home/shahriyar.rzaev/backup_dir/ps_5.7_master/full/2017-04-24_14-43-50 --backup --host=127.0.0.1
        --port=20192 --compress=quicklz --compress-chunk-size=65536 --compress-threads=4 --encrypt=AES256
        --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --encrypt-threads=4 --encrypt-chunk-size=65536 --binlog-info=AUTO
        --stream="xbstream" > /home/shahriyar.rzaev/backup_dir/ps_5.7_master/inc/2017-04-24_14-44-02/inc_backup.stream

So based on this, the incremental backup should be treated same way during prepare or for the second incremental backup etc.
Congratulations, autoxtrabackup will do it for you


autoxtrabackup with --dry_run option
------------------------------------

For testing purposes or just to show what is going on, with autoxtrabackup backup and prepare steps.
You can append ``--dry_run`` option, to show commands but not to run them.
Taking 1 full and 1 incremental backup:

    ::


        $ autoxtrabackup --backup --dry_run -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master.conf
        2017-04-24 15:00:30 DEBUG    <pid.PidFile object at 0x7fa9bcdb3ea8> entering setup
        2017-04-24 15:00:30 DEBUG    <pid.PidFile object at 0x7fa9bcdb3ea8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-04-24 15:00:30 DEBUG    <pid.PidFile object at 0x7fa9bcdb3ea8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-04-24 15:00:30 WARNING  Dry run enabled!
        2017-04-24 15:00:30 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/percona-server/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_percona-server-5_7_17/master/my.sandbox.cnf --user=msandbox --password=msandbox status --host=127.0.0.1 --port=20192
        mysqladmin: [Warning] Using a password on the command line interface can be insecure.
        2017-04-24 15:00:30 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
        2017-04-24 15:00:30 DEBUG    /home/shahriyar.rzaev/percona-server/5.7.17/bin/mysql exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-OK
        2017-04-24 15:00:30 DEBUG    /home/shahriyar.rzaev/percona-server/5.7.17/bin/mysqladmin exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
        2017-04-24 15:00:30 DEBUG    MySQL configuration file exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+OK
        2017-04-24 15:00:30 DEBUG    Xtrabackup exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-OK
        2017-04-24 15:00:30 DEBUG    Main backup directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK
        2017-04-24 15:00:30 DEBUG    Full Backup directory does not exist.+-+-+-+-+-+-+-+-+-+-+-+-OK
        2017-04-24 15:00:30 DEBUG    Creating full backup directory...+-+-+-+-+-+-+-+-+-++-+-+-+-+OK
        2017-04-24 15:00:30 DEBUG    Created+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
        2017-04-24 15:00:30 DEBUG    Increment directory does not exist.+-+-+-+-+-+-+-+-+-++-+-+-+OK
        2017-04-24 15:00:30 DEBUG    Creating increment backup directory.+-+-+-+-+-+-+-+-+-++-+-+-OK
        2017-04-24 15:00:30 DEBUG    Created
        2017-04-24 15:00:30 DEBUG    Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-OK
        2017-04-24 15:00:30 DEBUG    ###############################################################
        2017-04-24 15:00:30 DEBUG    #You have no backups : Taking very first Full Backup! - - - - #
        2017-04-24 15:00:30 DEBUG    ###############################################################
        2017-04-24 15:00:33 DEBUG    Trying to flush logs
        2017-04-24 15:00:33 DEBUG    Log flushing completed
        2017-04-24 15:00:33 WARNING  Streaming is enabled!
        2017-04-24 15:00:33 DEBUG    The following backup command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_percona-server-5_7_17/master/my.sandbox.cnf --user=msandbox --password='msandbox'  --target-dir=/home/shahriyar.rzaev/backup_dir/ps_5.7_master/full/2017-04-24_15-00-33 --backup --host=127.0.0.1 --port=20192 --compress=quicklz --compress-chunk-size=65536 --compress-threads=4 --encrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --encrypt-threads=4 --encrypt-chunk-size=65536 --binlog-info=AUTO --stream="xbstream" > /home/shahriyar.rzaev/backup_dir/ps_5.7_master/full/2017-04-24_15-00-33/full_backup.stream
        2017-04-24 15:00:33 DEBUG    <pid.PidFile object at 0x7fa9bcdb3ea8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-04-24 15:00:33 DEBUG    <pid.PidFile object at 0x7fa9bcdb3ea8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid


        $ autoxtrabackup --backup --dry_run -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master.conf
        2017-04-24 15:00:38 DEBUG    <pid.PidFile object at 0x7f5d73316ea8> entering setup
        2017-04-24 15:00:38 DEBUG    <pid.PidFile object at 0x7f5d73316ea8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-04-24 15:00:38 DEBUG    <pid.PidFile object at 0x7f5d73316ea8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-04-24 15:00:38 WARNING  Dry run enabled!
        2017-04-24 15:00:38 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/percona-server/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_percona-server-5_7_17/master/my.sandbox.cnf --user=msandbox --password=msandbox status --host=127.0.0.1 --port=20192
        mysqladmin: [Warning] Using a password on the command line interface can be insecure.
        2017-04-24 15:00:38 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
        2017-04-24 15:00:38 DEBUG    /home/shahriyar.rzaev/percona-server/5.7.17/bin/mysql exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-OK
        2017-04-24 15:00:38 DEBUG    /home/shahriyar.rzaev/percona-server/5.7.17/bin/mysqladmin exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
        2017-04-24 15:00:38 DEBUG    MySQL configuration file exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+OK
        2017-04-24 15:00:38 DEBUG    Xtrabackup exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-OK
        2017-04-24 15:00:38 DEBUG    Main backup directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK
        2017-04-24 15:00:38 DEBUG    Full Backup directory exists.+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+OK
        2017-04-24 15:00:38 DEBUG    Increment directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
        2017-04-24 15:00:38 DEBUG    Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-OK
        2017-04-24 15:00:38 DEBUG    ################################################################
        2017-04-24 15:00:38 DEBUG    You have a full backup that is less than 86400 seconds old. - -#
        2017-04-24 15:00:38 DEBUG    We will take an incremental one based on recent Full Backup - -#
        2017-04-24 15:00:38 DEBUG    ################################################################
        2017-04-24 15:00:41 DEBUG    Installed Server is MySQL, will continue as usual.
        2017-04-24 15:00:41 DEBUG    Using xbstream to extract and decrypt from full_backup.stream!
        2017-04-24 15:00:41 DEBUG    The following xbstream command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xbstream -x --parallel=100 --decrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --encrypt-threads=4 < /home/shahriyar.rzaev/backup_dir/ps_5.7_master/full/2017-04-24_15-00-33/full_backup.stream -C /home/shahriyar.rzaev/backup_dir/ps_5.7_master/full/2017-04-24_15-00-33
        2017-04-24 15:00:41 WARNING  Streaming is enabled!
        2017-04-24 15:00:41 DEBUG    The following backup command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_percona-server-5_7_17/master/my.sandbox.cnf --user=msandbox --password='msandbox' --target-dir=/home/shahriyar.rzaev/backup_dir/ps_5.7_master/inc/2017-04-24_15-00-41 --incremental-basedir=/home/shahriyar.rzaev/backup_dir/ps_5.7_master/full/2017-04-24_15-00-33 --backup --host=127.0.0.1 --port=20192 --compress=quicklz --compress-chunk-size=65536 --compress-threads=4 --encrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --encrypt-threads=4 --encrypt-chunk-size=65536 --binlog-info=AUTO --stream="xbstream" > /home/shahriyar.rzaev/backup_dir/ps_5.7_master/inc/2017-04-24_15-00-41/inc_backup.stream
        2017-04-24 15:00:41 DEBUG    <pid.PidFile object at 0x7f5d73316ea8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-04-24 15:00:41 DEBUG    <pid.PidFile object at 0x7f5d73316ea8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

Preparing backups:

    ::


        $ autoxtrabackup --prepare --dry_run -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master.conf
        2017-04-24 15:04:04 DEBUG    <pid.PidFile object at 0x7f357389aea8> entering setup
        2017-04-24 15:04:04 DEBUG    <pid.PidFile object at 0x7f357389aea8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-04-24 15:04:04 DEBUG    <pid.PidFile object at 0x7f357389aea8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-04-24 15:04:04 WARNING  Dry run enabled!
        2017-04-24 15:04:04 WARNING  Do not recover/copy-back in this mode!
        2017-04-24 15:04:04 DEBUG    Installed Server is MySQL, will continue as usual.
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-

        Preparing full/inc backups!
        What do you want to do?
        1. Prepare Backups and keep for future usage. NOTE('Once Prepared Backups Can not be prepared Again')
        2. Prepare Backups and restore/recover/copy-back immediately
        3. Just copy-back previously prepared backups
        Please Choose one of options and type 1 or 2 or 3: 1

        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
        2017-04-24 15:04:08 DEBUG    ####################################################################################################
        2017-04-24 15:04:08 DEBUG    You have Incremental backups. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#
        2017-04-24 15:04:11 DEBUG    Preparing Full backup 1 time. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#
        Final prepare,will occur after preparing all inc backups - - - - - - - - - - - - - - - - -  - - - -#
        2017-04-24 15:04:11 DEBUG    ####################################################################################################
        2017-04-24 15:04:14 DEBUG    Trying to decrypt backup
        2017-04-24 15:04:14 DEBUG    Running decrypt command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --target-dir=/home/shahriyar.rzaev/backup_dir/ps_5.7_master/full/2017-04-24_15-00-33 --remove-original
        2017-04-24 15:04:14 DEBUG    Trying to decompress backup
        2017-04-24 15:04:14 DEBUG    Running decompress command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decompress=TRUE --target-dir=/home/shahriyar.rzaev/backup_dir/ps_5.7_master/full/2017-04-24_15-00-33 --remove-original
        2017-04-24 15:04:14 DEBUG    Running prepare command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --prepare --apply-log-only --target-dir=/home/shahriyar.rzaev/backup_dir/ps_5.7_master/full/2017-04-24_15-00-33 --binlog-info=AUTO
        2017-04-24 15:04:14 DEBUG    ####################################################################################################
        2017-04-24 15:04:14 DEBUG    Preparing Incs:
        2017-04-24 15:04:17 DEBUG    ####################################################################################################
        2017-04-24 15:04:17 DEBUG    Preparing last incremental backup, inc backup dir/name is 2017-04-24_15-00-41
        2017-04-24 15:04:17 DEBUG    ####################################################################################################
        2017-04-24 15:04:20 DEBUG    Using xbstream to extract from full_backup.stream!
        2017-04-24 15:04:20 DEBUG    The following xbstream command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xbstream -x --parallel=100 < /home/shahriyar.rzaev/backup_dir/ps_5.7_master/inc/2017-04-24_15-00-41/inc_backup.stream -C /home/shahriyar.rzaev/backup_dir/ps_5.7_master/inc/2017-04-24_15-00-41
        2017-04-24 15:04:20 DEBUG    Trying to decrypt backup
        2017-04-24 15:04:20 DEBUG    Running decrypt command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decrypt=AES256 --encrypt-key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K' --target-dir=/home/shahriyar.rzaev/backup_dir/ps_5.7_master/inc/2017-04-24_15-00-41 --remove-original
        2017-04-24 15:04:20 DEBUG    Trying to decompress backup
        2017-04-24 15:04:20 DEBUG    Running decompress command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --decompress=TRUE --target-dir=/home/shahriyar.rzaev/backup_dir/ps_5.7_master/inc/2017-04-24_15-00-41 --remove-original
        2017-04-24 15:04:20 DEBUG    Running prepare command -> /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --prepare --target-dir=/home/shahriyar.rzaev/backup_dir/ps_5.7_master/full/2017-04-24_15-00-33 --incremental-dir=/home/shahriyar.rzaev/backup_dir/ps_5.7_master/inc/2017-04-24_15-00-41 --binlog-info=AUTO
        2017-04-24 15:04:20 DEBUG    ####################################################################################################
        2017-04-24 15:04:20 DEBUG    The end of the Prepare Stage. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -#
        2017-04-24 15:04:20 DEBUG    ####################################################################################################
        2017-04-24 15:04:23 DEBUG    <pid.PidFile object at 0x7f357389aea8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-04-24 15:04:23 DEBUG    <pid.PidFile object at 0x7f357389aea8> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
Basic features
==============

Backup
------

Yes you are right, this tool is for taking backups.
It should take care for automating this process for you.
You can specify the backup directory in config file (default /etc/bck.conf) under [Backup] category.
For me there is another config file prepared here -> ``/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf``

::

    [Backup]
    #Optional: set pid directory
    pid_dir=/tmp/MySQL-AutoXtraBackup
    tmpdir=/home/shahriyar.rzaev/XB_TEST/mysql_datadirs
    #Optional: set warning if pid of backup us running for longer than X
    pid_runtime_warning=2 Hours
    backupdir=/home/shahriyar.rzaev/XB_TEST/backup_dir
    backup_tool=/usr/bin/xtrabackup
    #Optional: specify different path/version of xtrabackup here for prepare
    #prepare_tool=
    xtra_prepare=--apply-log-only
    #Optional: pass additional options for backup stage
    #xtra_backup=--compact
    #Optional: pass additional options for prepare stage
    #xtra_prepare_options=--rebuild-indexes
    #Optional: pass general additional options; it will go to both for backup and prepare
    #xtra_options=--binlog-info=ON --galera-info
    #Optional: set archive and rotation
    #archive_dir=/home/shahriyar.rzaev/XB_TEST/backup_archives
    #full_backup_interval=1 day
    #max_archive_size=100GiB
    #max_archive_duration=4 Days
    #Optional WARNING(Enable this if you want to take partial backups). Specify database names or table names.
    #partial_list=test.t1 test.t2 dbtest

The command for backup:

::

    $ sudo autoxtrabackup --backup -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf

The result of first run:

::

    $ sudo autoxtrabackup --backup -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
    2017-11-02 22:47:23 DEBUG    <pid.PidFile object at 0x7fb405d41d68> entering setup
    2017-11-02 22:47:23 DEBUG    <pid.PidFile object at 0x7fb405d41d68> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-11-02 22:47:23 DEBUG    <pid.PidFile object at 0x7fb405d41d68> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-11-02 22:47:23 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/XB_TEST/server_dir/PS231017-percona-server-5.7.19-17-linux-x86_64-debug/bin/mysqladmin --defaults-file= --user=root --password= status --socket=/home/shahriyar.rzaev/XB_TEST/server_dir/PS231017-percona-server-5.7.19-17-linux-x86_64-debug/socket.sock
    mysqladmin: [Warning] Using a password on the command line interface can be insecure.
    2017-11-02 22:47:23 DEBUG    OK: Server is Up and running
    2017-11-02 22:47:23 DEBUG    OK: /home/shahriyar.rzaev/XB_TEST/server_dir/PS231017-percona-server-5.7.19-17-linux-x86_64-debug/bin/mysql exists
    2017-11-02 22:47:23 DEBUG    OK: /home/shahriyar.rzaev/XB_TEST/server_dir/PS231017-percona-server-5.7.19-17-linux-x86_64-debug/bin/mysqladmin exists
    2017-11-02 22:47:23 DEBUG    Skipping my.cnf check, because it is not specified
    2017-11-02 22:47:23 DEBUG    OK: XtraBackup exists
    2017-11-02 22:47:23 DEBUG    Main backup directory does not exist
    2017-11-02 22:47:23 DEBUG    Creating Main Backup folder...
    2017-11-02 22:47:23 DEBUG    OK: Created
    2017-11-02 22:47:23 DEBUG    Full Backup directory does not exist
    2017-11-02 22:47:23 DEBUG    Creating full backup directory...
    2017-11-02 22:47:23 DEBUG    OK: Created
    2017-11-02 22:47:23 DEBUG    Increment directory does not exist
    2017-11-02 22:47:23 DEBUG    Creating increment backup directory...
    2017-11-02 22:47:23 DEBUG    OK: Created
    2017-11-02 22:47:23 DEBUG    OK: Check status
    2017-11-02 22:47:23 DEBUG    - - - - You have no backups : Taking very first Full Backup! - - - -
    2017-11-02 22:47:26 DEBUG    Trying to flush logs
    2017-11-02 22:47:27 DEBUG    OK: Log flushing completed


You will have 2 separate folders inside backup directory:

::

    [shahriyar.rzaev@qaserver-04 ps_5.7_master]$ ls
    full  inc

We took full backup and it should be under ``full`` directory:

::

    [shahriyar.rzaev@qaserver-04 ps_5.7_master]$ ls full
    2017-02-24_14-49-10

Just run same command for taking incremental backup:

::

    $ sudo autoxtrabackup --backup -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
    2017-02-24 15:10:17 DEBUG    <pid.PidFile object at 0x7ff210900e08> entering setup
    2017-02-24 15:10:17 DEBUG    <pid.PidFile object at 0x7ff210900e08> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 15:10:17 DEBUG    <pid.PidFile object at 0x7ff210900e08> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 15:10:17 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password=msandbox status --host=localhost --port=20192
    mysqladmin: [Warning] Using a password on the command line interface can be insecure.
    2017-02-24 15:10:17 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
    2017-02-24 15:10:17 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysql exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-++-OK
    2017-02-24 15:10:17 DEBUG    /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
    2017-02-24 15:10:17 DEBUG    MySQL configuration file exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+OK
    2017-02-24 15:10:17 DEBUG    Xtrabackup exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-OK
    2017-02-24 15:10:17 DEBUG    Main backup directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-OK
    2017-02-24 15:10:17 DEBUG    Full Backup directory exists.+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+OK
    2017-02-24 15:10:17 DEBUG    Increment directory exists+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-OK
    2017-02-24 15:10:17 DEBUG    Check status: STATUS+-+-+-+-+-+-+-+-+-++-+-+-+-+-+-+-+-+-+-+-OK
    2017-02-24 15:10:17 DEBUG    ################################################################
    2017-02-24 15:10:17 DEBUG    You have a full backup that is less than 86400 seconds old. - -#
    2017-02-24 15:10:17 DEBUG    We will take an incremental one based on recent Full Backup - -#
    2017-02-24 15:10:17 DEBUG    ################################################################
    2017-02-24 15:10:20 DEBUG    Installed Server is MySQL, will continue as usual.
    2017-02-24 15:10:20 DEBUG    The following backup command will be executed /home/shahriyar.rzaev/Percona_Xtrabackups/xb_2.4/usr/local/xtrabackup/bin/xtrabackup --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password='msandbox' --target-dir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//inc/2017-02-24_15-10-20 --incremental-basedir=/home/shahriyar.rzaev/backup_dirs/ps_5.7_master//full/2017-02-24_14-49-10 --backup --host=localhost --port=20192
    2017-02-24 15:10:32 DEBUG    0224 15:10:32 completed OK!
    2017-02-24 15:10:32 DEBUG    <pid.PidFile object at 0x7ff210900e08> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 15:10:32 DEBUG    <pid.PidFile object at 0x7ff210900e08> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

Again run same command for taking second incremental backup:

::

    $ sudo autoxtrabackup --backup -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
    2017-11-02 22:49:37 DEBUG    <pid.PidFile object at 0x7ff4e39560e8> entering setup
    2017-11-02 22:49:37 DEBUG    <pid.PidFile object at 0x7ff4e39560e8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-11-02 22:49:37 DEBUG    <pid.PidFile object at 0x7ff4e39560e8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-11-02 22:49:37 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/XB_TEST/server_dir/PS231017-percona-server-5.7.19-17-linux-x86_64-debug/bin/mysqladmin --defaults-file= --user=root --password= status --socket=/home/shahriyar.rzaev/XB_TEST/server_dir/PS231017-percona-server-5.7.19-17-linux-x86_64-debug/socket.sock
    mysqladmin: [Warning] Using a password on the command line interface can be insecure.
    2017-11-02 22:49:37 DEBUG    OK: Server is Up and running
    2017-11-02 22:49:37 DEBUG    OK: /home/shahriyar.rzaev/XB_TEST/server_dir/PS231017-percona-server-5.7.19-17-linux-x86_64-debug/bin/mysql exists
    2017-11-02 22:49:37 DEBUG    OK: /home/shahriyar.rzaev/XB_TEST/server_dir/PS231017-percona-server-5.7.19-17-linux-x86_64-debug/bin/mysqladmin exists
    2017-11-02 22:49:37 DEBUG    Skipping my.cnf check, because it is not specified
    2017-11-02 22:49:37 DEBUG    OK: XtraBackup exists
    2017-11-02 22:49:37 DEBUG    OK: Main backup directory exists
    2017-11-02 22:49:37 DEBUG    OK: Full Backup directory exists
    2017-11-02 22:49:37 DEBUG    OK: Increment directory exists
    2017-11-02 22:49:37 DEBUG    OK: Check status
    2017-11-02 22:49:37 DEBUG    - - - - You have a full backup that is less than 86400 seconds old. - - - -
    2017-11-02 22:49:37 DEBUG    - - - - We will take an incremental one based on recent Full Backup - - - -

The incremental backups will be stored under ``inc`` directory:

::

    [shahriyar.rzaev@qaserver-04 ps_5.7_master]$ ls  inc/
    2017-02-24_15-10-20  2017-02-24_15-11-30

You can proceed to take incremental backups in the same manner.





Prepare
-------
For preparing backups just use --prepare option. For our case we have a
full and 2 incremental backups. All backups will be prepared
automatically.

You are going to have 3 options to choose:

1. Only prepare backups.
2. Prepare backups and restore immediately
3. Restore from already prepared backup.

For now let's choose 1:

::

    $ sudo autoxtrabackup --prepare -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
    2017-11-02 22:51:57 DEBUG    <pid.PidFile object at 0x7f035a8ed0e8> entering setup
    2017-11-02 22:51:57 DEBUG    <pid.PidFile object at 0x7f035a8ed0e8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-11-02 22:51:57 DEBUG    <pid.PidFile object at 0x7f035a8ed0e8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    Preparing full/inc backups!
    What do you want to do?
    1. Prepare Backups and keep for future usage. NOTE('Once Prepared Backups Can not be prepared Again')
    2. Prepare Backups and restore/recover/copy-back immediately
    3. Just copy-back previously prepared backups
    Please Choose one of options and type 1 or 2 or 3: 1
    1

    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    2017-11-02 22:52:22 DEBUG    - - - - You have Incremental backups. - - - -
    2017-11-02 22:52:25 DEBUG    - - - - Preparing Full backup for incrementals - - - -
    2017-11-02 22:52:25 DEBUG    - - - - Final prepare,will occur after preparing all inc backups - - - -
    2017-11-02 22:52:28 DEBUG    Trying to decrypt backup
    2017-11-02 22:52:28 DEBUG    Running decrypt command -> /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --decrypt=AES256 --encrypt-key=VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/full/2017-11-02_22-47-27 --remove-original
    2017-11-02 22:52:29 DEBUG    1102 22:52:29 completed OK!
    2017-11-02 22:52:29 DEBUG    OK: Decrypted!
    2017-11-02 22:52:29 DEBUG    Trying to decompress backup
    2017-11-02 22:52:29 DEBUG    Running decompress command -> /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --decompress=TRUE --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/full/2017-11-02_22-47-27 --remove-original
    2017-11-02 22:52:29 DEBUG    1102 22:52:29 completed OK!
    2017-11-02 22:52:29 DEBUG    OK: Decompressed

    That's it. Your backup is ready to restore/recovery.



Restore single table
--------------------

If you have deleted table data and you have full server backup. You can
restore single table as displayed here:

::


    > select * from t1;
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
    6 rows in set (0.01 sec)

    > delete from t1;
    Query OK, 6 rows affected (0.12 sec)


Restoring single table, ``--partial`` must be used for this:

::


    $ sudo autoxtrabackup --partial -v -l DEBUG --defaults_file=/home/shahriyar.rzaev/AutoXtrabackup_Configs/ps_5.7_master_bck.conf
    2017-02-24 15:45:01 DEBUG    <pid.PidFile object at 0x7f3349583e08> entering setup
    2017-02-24 15:45:01 DEBUG    <pid.PidFile object at 0x7f3349583e08> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 15:45:01 DEBUG    <pid.PidFile object at 0x7f3349583e08> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 15:45:01 DEBUG    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
    Type Database name: dbtest
    Type Table name: t1
    2017-02-24 15:45:05 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/Percona_Servers/5.7.17/bin/mysqladmin --defaults-file=/home/shahriyar.rzaev/sandboxes/rsandbox_Percona-Server-5_7_17/master/my.sandbox.cnf --user=jeffrey --password=msandbox status --host=localhost --port=20192
    mysqladmin: [Warning] Using a password on the command line interface can be insecure.
    2017-02-24 15:45:05 DEBUG    Server is Up and running+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+OK
    2017-02-24 15:45:05 DEBUG    Checking if innodb_file_per_table is enabled
    2017-02-24 15:45:05 DEBUG    innodb_file_per_table is enabled!
    2017-02-24 15:45:05 DEBUG    Checking MySQL version
    2017-02-24 15:45:05 DEBUG    MySQL Version is, 5.7.17-11-log
    2017-02-24 15:45:05 DEBUG    You have correct version of MySQL
    2017-02-24 15:45:05 DEBUG    Checking if database exists in MySQL
    2017-02-24 15:45:05 DEBUG    Database exists!
    2017-02-24 15:45:05 DEBUG    Checking if table exists in MySQL Server
    2017-02-24 15:45:05 DEBUG    Table exists in MySQL Server.
    2017-02-24 15:45:05 DEBUG    Applying write lock!
    2017-02-24 15:45:05 DEBUG    Locked
    2017-02-24 15:45:05 DEBUG    Discarding tablespace
    2017-02-24 15:45:05 DEBUG    Tablespace discarded successfully
    2017-02-24 15:45:05 DEBUG    Copying .ibd file back
    2017-02-24 15:45:05 DEBUG    Running chown command!
    2017-02-24 15:45:05 DEBUG    Chown command completed
    2017-02-24 15:45:05 DEBUG    Importing Tablespace!
    2017-02-24 15:45:05 DEBUG    Tablespace imported
    2017-02-24 15:45:05 DEBUG    Unlocking tables!
    2017-02-24 15:45:05 DEBUG    Unlocked!
    2017-02-24 15:45:05 DEBUG    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
    2017-02-24 15:45:05 DEBUG    Table Recovered! ...-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    2017-02-24 15:45:05 DEBUG    <pid.PidFile object at 0x7f3349583e08> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-02-24 15:45:05 DEBUG    <pid.PidFile object at 0x7f3349583e08> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

Congratulations you have restored table:

::

    > select * from t1;
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

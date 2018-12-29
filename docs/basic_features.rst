Basic features
==============

Backup
------

Yes you are right, this tool is for taking backups.
It should take care for automating this process for you.
You can specify the backup directory in config file (default /etc/bck.conf) under [Backup] category.
So you have prepared your config and now you are ready for start.

The command for taking full backup with DEBUG enabled, i.e first run of the tool.

::

    $ sudo autoxtrabackup -v -lf /home/shahriyar.rzaev/autoxtrabackup_2_4_5_7.log \
    -l DEBUG --defaults-file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.conf --backup

    2017-11-16 19:37:52 DEBUG    <pid.PidFile object at 0x7fdb6f78b048> entering setup
    2017-11-16 19:37:52 DEBUG    <pid.PidFile object at 0x7fdb6f78b048> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-11-16 19:37:52 DEBUG    <pid.PidFile object at 0x7fdb6f78b048> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-11-16 19:37:52 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/bin/mysqladmin --defaults-file= --user=root --password= status --socket=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/socket.sock
    mysqladmin: [Warning] Using a password on the command line interface can be insecure.
    2017-11-16 19:37:52 DEBUG    OK: Server is Up and running
    2017-11-16 19:37:52 DEBUG    OK: /home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/bin/mysql exists
    2017-11-16 19:37:52 DEBUG    OK: /home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/bin/mysqladmin exists
    2017-11-16 19:37:52 DEBUG    Skipping my.cnf check, because it is not specified
    2017-11-16 19:37:52 DEBUG    OK: XtraBackup exists
    2017-11-16 19:37:52 DEBUG    Main backup directory does not exist
    2017-11-16 19:37:52 DEBUG    Creating Main Backup folder...
    2017-11-16 19:37:52 DEBUG    OK: Created
    2017-11-16 19:37:52 DEBUG    Full Backup directory does not exist
    2017-11-16 19:37:52 DEBUG    Creating full backup directory...
    2017-11-16 19:37:52 DEBUG    OK: Created
    2017-11-16 19:37:52 DEBUG    Increment directory does not exist
    2017-11-16 19:37:52 DEBUG    Creating increment backup directory...
    2017-11-16 19:37:52 DEBUG    OK: Created
    2017-11-16 19:37:52 DEBUG    OK: Check status
    2017-11-16 19:37:52 DEBUG    - - - - You have no backups : Taking very first Full Backup! - - - -
    2017-11-16 19:37:52 DEBUG    Trying to flush logs
    2017-11-16 19:37:52 DEBUG    OK: Log flushing completed
    2017-11-16 19:37:52 WARNING  Streaming is enabled!
    2017-11-16 19:37:52 DEBUG    The following backup command will be executed /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --defaults-file= --user=root --password=''  --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/full/2017-11-16_19-37-52 --backup --socket=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/socket.sock --compress=quicklz --compress-chunk-size=65536 --compress-threads=4 --encrypt=AES256 --encrypt-key=VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K --encrypt-threads=4 --encrypt-chunk-size=65536 --slave-info --no-version-check --core-file --parallel=1 --throttle=40 --keyring-file-data=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/mysql-keyring/keyring --stream="xbstream" > /home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/full/2017-11-16_19-37-52/full_backup.stream

The result of second run; it will take an incremental backup.

::

    $ sudo autoxtrabackup -v -lf /home/shahriyar.rzaev/autoxtrabackup_2_4_5_7.log \
    -l DEBUG --defaults-file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.conf --backup
    2017-11-16 19:43:07 DEBUG    <pid.PidFile object at 0x7fb688315048> entering setup
    2017-11-16 19:43:07 DEBUG    <pid.PidFile object at 0x7fb688315048> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-11-16 19:43:07 DEBUG    <pid.PidFile object at 0x7fb688315048> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-11-16 19:43:07 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/bin/mysqladmin --defaults-file= --user=root --password= status --socket=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/socket.sock
    mysqladmin: [Warning] Using a password on the command line interface can be insecure.
    2017-11-16 19:43:07 DEBUG    OK: Server is Up and running
    2017-11-16 19:43:07 DEBUG    OK: /home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/bin/mysql exists
    2017-11-16 19:43:07 DEBUG    OK: /home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/bin/mysqladmin exists
    2017-11-16 19:43:07 DEBUG    Skipping my.cnf check, because it is not specified
    2017-11-16 19:43:07 DEBUG    OK: XtraBackup exists
    2017-11-16 19:43:07 DEBUG    OK: Main backup directory exists
    2017-11-16 19:43:07 DEBUG    OK: Full Backup directory exists
    2017-11-16 19:43:07 DEBUG    OK: Increment directory exists
    2017-11-16 19:43:07 DEBUG    OK: Check status
    2017-11-16 19:43:07 DEBUG    - - - - You have a full backup that is less than 86400 seconds old. - - - -
    2017-11-16 19:43:07 DEBUG    - - - - We will take an incremental one based on recent Full Backup - - - -
    2017-11-16 19:43:10 DEBUG    Using xbstream to extract and decrypt from full_backup.stream!
    2017-11-16 19:43:10 DEBUG    The following xbstream command will be executed /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xbstream -x --parallel=100 --decrypt=AES256 --encrypt-key=VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K --encrypt-threads=4 < /home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/full/2017-11-16_19-37-52/full_backup.stream -C /home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/full/2017-11-16_19-37-52
    2017-11-16 19:43:10 DEBUG    OK: XBSTREAM command succeeded.
    2017-11-16 19:43:10 WARNING  Streaming is enabled!
    2017-11-16 19:43:10 DEBUG    The following backup command will be executed /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --defaults-file= --user=root --password='' --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_19-43-10 --incremental-basedir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/full/2017-11-16_19-37-52 --backup --socket=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/socket.sock --compress=quicklz --compress-chunk-size=65536 --compress-threads=4 --encrypt=AES256 --encrypt-key=VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K --encrypt-threads=4 --encrypt-chunk-size=65536 --slave-info --no-version-check --core-file --parallel=1 --throttle=40 --keyring-file-data=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/mysql-keyring/keyring --stream="xbstream" > /home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_19-43-10/inc_backup.stream



You will have 2 separate folders inside backup directory:

::

    [vagrant@localhost backup_dir]$ ls
    ps_5_7_x_2_4
    [vagrant@localhost backup_dir]$ cd ps_5_7_x_2_4/
    [vagrant@localhost ps_5_7_x_2_4]$ ls
    full  inc


We took full backup and it should be under the ``full`` directory:

::

    [vagrant@localhost ps_5_7_x_2_4]$ ls full/
    2017-11-16_19-37-52

Incremental backups are inside ``inc`` directory:

::

    [vagrant@localhost ps_5_7_x_2_4]$ ls inc/
    2017-11-16_19-43-10

If you want more incremental backups just run the same command again and again.


Prepare
-------
For preparing backups just use --prepare option. For our case we have a
full and 2 incremental backups:

::

    [vagrant@localhost ps_5_7_x_2_4]$ ls full/
    2017-11-16_19-37-52
    [vagrant@localhost ps_5_7_x_2_4]$ ls inc/
    2017-11-16_19-43-10  2017-11-16_19-48-23

All backups will be prepared
automatically.

You are going to have 3 options to choose:

1. Only prepare backups.
2. Prepare backups and restore immediately.
3. Restore from already prepared backup.

For now let's choose 1:

::

    $ autoxtrabackup -v -lf /home/shahriyar.rzaev/autoxtrabackup_2_4_5_7.log \
    -l DEBUG --defaults-file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.conf --prepare
    2017-11-16 19:50:33 DEBUG    <pid.PidFile object at 0x7fea1d28c048> entering setup
    2017-11-16 19:50:33 DEBUG    <pid.PidFile object at 0x7fea1d28c048> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-11-16 19:50:33 DEBUG    <pid.PidFile object at 0x7fea1d28c048> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    Preparing full/inc backups!
    What do you want to do?
    1. Prepare Backups and keep for future usage. NOTE('Once Prepared Backups Can not be prepared Again')
    2. Prepare Backups and restore/recover/copy-back immediately
    3. Just copy-back previously prepared backups
    Please Choose one of options and type 1 or 2 or 3: 1


That's it. Your backup is ready to restore/recovery.



Restore single table
--------------------

If you have deleted table data and you have already prepared full server backup.
You can restore single table as displayed here:

::

    > show create table t1\G
    *************************** 1. row ***************************
           Table: t1
    Create Table: CREATE TABLE t1 (
      id int(11) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    1 row in set (0.01 sec)

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


Restoring single table, the ``--partial`` option must be used for this:

::


    $ sudo autoxtrabackup -v -lf /home/shahriyar.rzaev/autoxtrabackup_2_4_5_7.log \
    -l DEBUG --defaults-file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.conf --partial
    2017-11-16 19:56:32 DEBUG    <pid.PidFile object at 0x7f39212e4048> entering setup
    2017-11-16 19:56:32 DEBUG    <pid.PidFile object at 0x7f39212e4048> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-11-16 19:56:32 DEBUG    <pid.PidFile object at 0x7f39212e4048> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    Type Database name: test
    Type Table name: t1
    2017-11-16 19:56:56 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/bin/mysqladmin --defaults-file= --user=root --password= status --socket=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/socket.sock
    mysqladmin: [Warning] Using a password on the command line interface can be insecure.
    2017-11-16 19:56:56 DEBUG    OK: Server is Up and running
    2017-11-16 19:56:56 DEBUG    Checking if innodb_file_per_table is enabled
    2017-11-16 19:56:56 DEBUG    OK: innodb_file_per_table is enabled!
    2017-11-16 19:56:56 DEBUG    Checking MySQL version
    2017-11-16 19:56:56 DEBUG    You have correct version of MySQL
    2017-11-16 19:56:56 DEBUG    Checking if database exists in MySQL
    2017-11-16 19:56:56 DEBUG    Database exists!
    2017-11-16 19:56:56 DEBUG    Checking if table exists in MySQL Server
    2017-11-16 19:56:57 DEBUG    Table exists in MySQL Server.
    2017-11-16 19:56:57 DEBUG    Applying write lock!
    2017-11-16 19:56:57 DEBUG    OK: Table is locked
    2017-11-16 19:56:57 DEBUG    Discarding tablespace
    2017-11-16 19:56:57 DEBUG    OK: Tablespace discarded successfully
    2017-11-16 19:56:57 DEBUG    OK: Copying .ibd file back
    2017-11-16 19:56:57 DEBUG    Running chown command!
    2017-11-16 19:56:57 DEBUG    OK: Chown command completed
    2017-11-16 19:56:57 DEBUG    Importing Tablespace!
    2017-11-16 19:56:57 DEBUG    OK: Tablespace imported
    2017-11-16 19:56:57 DEBUG    Unlocking tables!
    2017-11-16 19:56:57 DEBUG    OK: Unlocked!
    2017-11-16 19:56:57 DEBUG    OK: Table Recovered! ...
    2017-11-16 19:56:57 DEBUG    <pid.PidFile object at 0x7f39212e4048> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-11-16 19:56:57 DEBUG    <pid.PidFile object at 0x7f39212e4048> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

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

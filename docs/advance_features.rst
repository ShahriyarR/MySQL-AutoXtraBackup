Advanced features
=================

Compressed backups:
-------------------

To enable compression support just uncomment the options under
[Compress] category inside main cnfiguration file:

.. code-block:: shell

    [Compress]
    #Optional
    #Enable only if you want to use compression.
    compress=quicklz
    compress_chunk_size=65536
    compress_threads=4
    decompress=TRUE
    #Enable if you want to remove .qp files after decompression.(Available from PXB 2.3.7 and 2.4.6)
    remove_original=FALSE


Encrypted backups
-----------------

To enable encryption support uncomment the options under [Encryption]
category:

::

    [Encrypt]
    #optional
    #enable only if you want to create encrypted backups
    xbcrypt = /usr/bin/xbcrypt
    encrypt = AES256
    #please note that --encrypt-key and --encrypt-key-file are mutually exclusive
    encrypt_key = VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K
    #encrypt_key_file = /path/to/file/with_encrypt_key
    encrypt_threads = 4
    encrypt_chunk_size = 65536
    decrypt = AES256
    #enable if you want to remove .qp files after decompression.(Available from PXB 2.3.7 and 2.4.6)
    remove_original = FALSE


Partial backups
---------------

It is possible to take partial full and incremental backups. The idea is, to take specified table(or database) as full backup,
then to take incremental backups based on this one table.
You can achieve this by enabling ``partial_list`` option from cnfig file:


::

    [Backup]
    #optional: set pid directory
    pid_dir = /tmp/MySQL-AutoXtraBackup
    tmp_dir = /home/shako/XB_TEST/mysql_datadirs
    #optional: set warning if pid of backup us running for longer than x
    pid_runtime_warning = 2 Hours
    backup_dir = /home/shako/XB_TEST/backup_dir
    backup_tool = /usr/bin/xtrabackup
    #optional: specify different path/version of xtrabackup here for prepare
    #prepare_tool =
    xtra_prepare = --apply-log-only
    #optional: pass additional options for backup stage
    #xtra_backup = --compact
    #optional: pass additional options for prepare stage
    #xtra_prepare_options = --rebuild-indexes
    #optional: pass general additional options; it will go to both for backup and prepare
    #xtra_options = --binlog-info=ON --galera-info
    #optional: set archive and rotation
    #archive_dir = /home/shako/XB_TEST/backup_archives
    #prepare_archive = 1
    #move_archive = 0
    #full_backup_interval = 1 day
    #archive_max_size = 100GiB
    #archive_max_duration = 4 Days
    #optional: warning(enable this if you want to take partial backups). specify database names or table names.
    #partial_list = test.t1 test.t2 dbtest


Run it and notice that backup command has changed (see ``--databases`` option for xtrabackup command):

In the same way you can take incremental backup of specified tables.

The prepare process is the same as ordinary prepare, just run autoxtrabackup with ``--prepare`` option, you can even restore this single table using ``--partial`` option.

Decompressing and Decrypting backups
------------------------------------

We took Compressed and Encrypted backups.
It is time to prepare them.
autoxtrabackup will prepare all backups automatically, by first decrypting then
decompressing step-by-step.
All backups first will be decrypted then decompressed and then
prepared.
You can also optionally enable ``--remove-original`` option to
remove ``.xbcrypt`` and ``.qp`` files from backup directory during prepare
process. Read about this option here -> `--remove-original <https://www.percona.com/doc/percona-xtrabackup/2.4/xtrabackup_bin/xbk_option_reference.html#cmdoption-xtrabackup-remove-original>`_

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

Dropping the database:

::

        > drop database test;
        Query OK, 1 row affected (1.08 sec)


Trying to restore t1 table: It will figure out that specified database is missing and will prompt to create it.

::


        $ autoxtrabackup -v -lf /home/shahriyar.rzaev/autoxtrabackup_2_3_5_6.log \
        -l DEBUG --defaults-file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.cnf --partial
        2017-11-16 20:38:16 DEBUG    <pid.PidFile object at 0x7f4f1ac6a048> entering setup
        2017-11-16 20:38:16 DEBUG    <pid.PidFile object at 0x7f4f1ac6a048> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-11-16 20:38:16 DEBUG    <pid.PidFile object at 0x7f4f1ac6a048> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        Type Database name: test
        Type Table name: t1
        2017-11-16 20:38:19 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/bin/mysqladmin --defaults-file= --user=root --password= status --socket=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/socket.sock
        mysqladmin: [Warning] Using a password on the command line interface can be insecure.
        2017-11-16 20:38:19 DEBUG    OK: Server is Up and running
        2017-11-16 20:38:19 DEBUG    Checking if innodb_file_per_table is enabled
        2017-11-16 20:38:19 DEBUG    OK: innodb_file_per_table is enabled!
        2017-11-16 20:38:19 DEBUG    Checking MySQL version
        2017-11-16 20:38:19 DEBUG    You have correct version of MySQL
        2017-11-16 20:38:19 DEBUG    Checking if database exists in MySQL
        2017-11-16 20:38:19 DEBUG    There is no such database!
        2017-11-16 20:38:19 DEBUG    Create Specified Database in MySQL Server, before restoring single table
        We can create it for you do you want? (yes/no): yes
        2017-11-16 20:38:26 DEBUG    Creating specified database
        2017-11-16 20:38:26 DEBUG    OK: test database created
        2017-11-16 20:38:26 DEBUG    Checking if table exists in MySQL Server
        2017-11-16 20:38:26 DEBUG    Table does not exist in MySQL Server.
        2017-11-16 20:38:26 DEBUG    You can not restore table, with not existing tablespace file(.ibd)!
        2017-11-16 20:38:26 DEBUG    We will try to extract table create statement from .frm file, from backup folder
        2017-11-16 20:38:26 DEBUG    Running mysqlfrm tool
        2017-11-16 20:38:26 DEBUG    OK: Success to run mysqlfrm
        2017-11-16 20:38:26 DEBUG    Table Created from .frm file!
        2017-11-16 20:38:26 DEBUG    Applying write lock!
        2017-11-16 20:38:26 DEBUG    OK: Table is locked
        2017-11-16 20:38:26 DEBUG    Discarding tablespace
        2017-11-16 20:38:26 DEBUG    OK: Tablespace discarded successfully
        2017-11-16 20:38:26 DEBUG    OK: Copying .ibd file back
        2017-11-16 20:38:26 DEBUG    Running chown command!
        2017-11-16 20:38:26 DEBUG    OK: Chown command completed
        2017-11-16 20:38:26 DEBUG    Importing Tablespace!
        2017-11-16 20:38:26 DEBUG    OK: Tablespace imported
        2017-11-16 20:38:26 DEBUG    Unlocking tables!
        2017-11-16 20:38:26 DEBUG    OK: Unlocked!
        2017-11-16 20:38:26 DEBUG    OK: Table Recovered! ...
        2017-11-16 20:38:26 DEBUG    <pid.PidFile object at 0x7f4f1ac6a048> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-11-16 20:38:26 DEBUG    <pid.PidFile object at 0x7f4f1ac6a048> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

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


autoxtrabackup with --dry_run option
------------------------------------

For testing purposes or just to show what is going on, with autoxtrabackup backup and prepare steps.
You can append ``--dry_run`` option, to show commands but not to run them.
Taking backup:

::


        $ autoxtrabackup -v -lf /home/shahriyar.rzaev/autoxtrabackup_2_3_5_6.log -l DEBUG --defaults-file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.cnf --backup --dry_run
        2017-11-16 20:40:47 DEBUG    <pid.PidFile object at 0x7f0cf71a4048> entering setup
        2017-11-16 20:40:47 DEBUG    <pid.PidFile object at 0x7f0cf71a4048> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-11-16 20:40:47 DEBUG    <pid.PidFile object at 0x7f0cf71a4048> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-11-16 20:40:47 WARNING  Dry run enabled!
        2017-11-16 20:40:47 DEBUG    Running mysqladmin command -> /home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/bin/mysqladmin --defaults-file= --user=root --password= status --socket=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/socket.sock
        mysqladmin: [Warning] Using a password on the command line interface can be insecure.
        2017-11-16 20:40:47 DEBUG    OK: Server is Up and running
        2017-11-16 20:40:47 DEBUG    OK: /home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/bin/mysql exists
        2017-11-16 20:40:47 DEBUG    OK: /home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/bin/mysqladmin exists
        2017-11-16 20:40:47 DEBUG    Skipping my.cnf check, because it is not specified
        2017-11-16 20:40:47 DEBUG    OK: XtraBackup exists
        2017-11-16 20:40:47 DEBUG    OK: Main backup directory exists
        2017-11-16 20:40:47 DEBUG    OK: Full Backup directory exists
        2017-11-16 20:40:47 DEBUG    OK: Increment directory exists
        2017-11-16 20:40:47 DEBUG    OK: Check status
        2017-11-16 20:40:47 DEBUG    - - - - You have a full backup that is less than 86400 seconds old. - - - -
        2017-11-16 20:40:47 DEBUG    - - - - We will take an incremental one based on recent Full Backup - - - -
        2017-11-16 20:40:50 DEBUG    Using xbstream to extract and decrypt from inc_backup.stream!
        2017-11-16 20:40:50 DEBUG    The following xbstream command will be executed /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xbstream -x --parallel=100 --decrypt=AES256 --encrypt-key=VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K --encrypt-threads=4 < /home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-13-39/inc_backup.stream -C /home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-13-39
        2017-11-16 20:40:50 WARNING  Streaming is enabled!
        2017-11-16 20:40:50 DEBUG    The following backup command will be executed /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --defaults-file= --user=root --password=''  --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-40-50 --incremental-basedir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-13-39 --backup --socket=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/socket.sock --compress=quicklz --compress_chunk_size=65536 --encrypt=AES256 --encrypt-key=VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K --encrypt-threads=4 --encrypt-chunk-size=65536 --slave-info --no-version-check --core-file --parallel=1 --throttle=40 --keyring-file-data=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/mysql-keyring/keyring --stream="xbstream" > /home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-40-50/inc_backup.stream
        2017-11-16 20:40:50 DEBUG    <pid.PidFile object at 0x7f0cf71a4048> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-11-16 20:40:50 DEBUG    <pid.PidFile object at 0x7f0cf71a4048> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

Preparing backups:

::


        $ autoxtrabackup -v -lf /home/shahriyar.rzaev/autoxtrabackup_2_3_5_6.log -l DEBUG --defaults-file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.cnf --prepare --dry_run
        2017-11-16 20:41:49 DEBUG    <pid.PidFile object at 0x7fac08f9e048> entering setup
        2017-11-16 20:41:49 DEBUG    <pid.PidFile object at 0x7fac08f9e048> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-11-16 20:41:49 DEBUG    <pid.PidFile object at 0x7fac08f9e048> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-11-16 20:41:49 WARNING  Dry run enabled!
        2017-11-16 20:41:49 WARNING  Do not recover/copy-back in this mode!
        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        Preparing full/inc backups!
        What do you want to do?
        1. Prepare Backups and keep for future usage. NOTE('Once Prepared Backups Can not be prepared Again')
        2. Prepare Backups and restore/recover/copy-back immediately
        3. Just copy-back previously prepared backups
        Please Choose one of options and type 1 or 2 or 3: 1

        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        2017-11-16 20:41:53 DEBUG    - - - - You have Incremental backups. - - - -
        2017-11-16 20:41:53 DEBUG    - - - - Preparing Full backup for incrementals - - - -
        2017-11-16 20:41:53 DEBUG    - - - - Final prepare,will occur after preparing all inc backups - - - -
        2017-11-16 20:41:56 DEBUG    Trying to decrypt backup
        2017-11-16 20:41:56 DEBUG    Running decrypt command -> /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --decrypt=AES256 --encrypt-key=VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/full/2017-11-16_20-10-53 --remove-original
        2017-11-16 20:41:56 DEBUG    Trying to decompress backup
        2017-11-16 20:41:56 DEBUG    Running decompress command -> /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --decompress=TRUE --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/full/2017-11-16_20-10-53 --remove-original
        2017-11-16 20:41:56 DEBUG    Running prepare command -> /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --prepare --apply-log-only --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/full/2017-11-16_20-10-53 --slave-info --no-version-check --core-file --parallel=1 --throttle=40 --keyring-file-data=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/mysql-keyring/keyring
        2017-11-16 20:41:56 DEBUG    Preparing Incs:
        2017-11-16 20:41:56 DEBUG    Preparing inc backups in sequence. inc backup dir/name is 2017-11-16_20-12-23
        2017-11-16 20:41:56 DEBUG    Trying to decrypt backup
        2017-11-16 20:41:56 DEBUG    Running decrypt command -> /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --decrypt=AES256 --encrypt-key=VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-12-23 --remove-original
        2017-11-16 20:41:56 DEBUG    Trying to decompress backup
        2017-11-16 20:41:56 DEBUG    Running decompress command -> /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --decompress=TRUE --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-12-23 --remove-original
        2017-11-16 20:41:56 DEBUG    Running prepare command -> /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --prepare --apply-log-only --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/full/2017-11-16_20-10-53 --incremental-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-12-23 --slave-info --no-version-check --core-file --parallel=1 --throttle=40 --keyring-file-data=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/mysql-keyring/keyring
        2017-11-16 20:41:56 DEBUG    Preparing inc backups in sequence. inc backup dir/name is 2017-11-16_20-13-39
        2017-11-16 20:41:56 DEBUG    Trying to decrypt backup
        2017-11-16 20:41:56 DEBUG    Running decrypt command -> /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --decrypt=AES256 --encrypt-key=VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-13-39 --remove-original
        2017-11-16 20:41:56 DEBUG    Trying to decompress backup
        2017-11-16 20:41:56 DEBUG    Running decompress command -> /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --decompress=TRUE --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-13-39 --remove-original
        2017-11-16 20:41:56 DEBUG    Running prepare command -> /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --prepare --apply-log-only --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/full/2017-11-16_20-10-53 --incremental-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-13-39 --slave-info --no-version-check --core-file --parallel=1 --throttle=40 --keyring-file-data=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/mysql-keyring/keyring
        2017-11-16 20:41:56 DEBUG    Preparing last incremental backup, inc backup dir/name is 2017-11-16_20-40-50
        2017-11-16 20:41:56 DEBUG    Using xbstream to extract from inc_backup.stream!
        2017-11-16 20:41:56 DEBUG    The following xbstream command will be executed /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xbstream -x --parallel=100 < /home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-40-50/inc_backup.stream -C /home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-40-50
        2017-11-16 20:41:56 DEBUG    Trying to decrypt backup
        2017-11-16 20:41:56 DEBUG    Running decrypt command -> /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --decrypt=AES256 --encrypt-key=VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-40-50 --remove-original
        2017-11-16 20:41:56 DEBUG    Trying to decompress backup
        2017-11-16 20:41:56 DEBUG    Running decompress command -> /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --decompress=TRUE --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-40-50 --remove-original
        2017-11-16 20:41:56 DEBUG    Running prepare command -> /home/shahriyar.rzaev/XB_TEST/server_dir/target/percona-xtrabackup-2.4.x-debug/bin/xtrabackup --prepare --target-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/full/2017-11-16_20-10-53 --incremental-dir=/home/shahriyar.rzaev/XB_TEST/backup_dir/ps_5_7_x_2_4/inc/2017-11-16_20-40-50 --slave-info --no-version-check --core-file --parallel=1 --throttle=40 --keyring-file-data=/home/shahriyar.rzaev/XB_TEST/server_dir/PS131117-percona-server-5.7.19-17-linux-x86_64/mysql-keyring/keyring
        2017-11-16 20:41:56 DEBUG    - - - - The end of the Prepare Stage. - - - -
        2017-11-16 20:41:56 DEBUG    <pid.PidFile object at 0x7fac08f9e048> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
        2017-11-16 20:41:56 DEBUG    <pid.PidFile object at 0x7fac08f9e048> closing pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid

The end.

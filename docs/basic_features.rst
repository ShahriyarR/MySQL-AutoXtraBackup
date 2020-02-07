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

    $ sudo autoxtrabackup -v -lf /home/shako/.autoxtrabackup/autoxtrabackup.log \
    -l DEBUG --defaults-file=/home/shako/.autoxtrabackup/autoxtrabackup.cnf --backup

    2019-01-20 13:52:07 DEBUG    [__init__.py:71] <pid.PidFile object at 0x7f7cd6ebe7c8> entering setup
    2019-01-20 13:52:07 DEBUG    [__init__.py:161] <pid.PidFile object at 0x7f7cd6ebe7c8> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2019-01-20 13:52:07 DEBUG    [__init__.py:148] <pid.PidFile object at 0x7f7cd6ebe7c8> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2019-01-20 13:52:07 DEBUG    [check_env.py:49] Running mysqladmin command -> /usr/bin/mysqladmin --defaults-file= --user=root --password='*' status --host=127.0.0.1 --port=3306
    2019-01-20 13:52:07 DEBUG    [check_env.py:54] OK: Server is Up and running
    2019-01-20 13:52:07 DEBUG    [check_env.py:81] OK: /usr/bin/mysql exists
    2019-01-20 13:52:07 DEBUG    [check_env.py:93] OK: /usr/bin/mysqladmin exists
    2019-01-20 13:52:07 DEBUG    [check_env.py:66] Skipping my.cnf check, because it is not specified
    2019-01-20 13:52:07 DEBUG    [check_env.py:105] OK: XtraBackup exists
    2019-01-20 13:52:07 DEBUG    [check_env.py:121] Main backup directory does not exist
    2019-01-20 13:52:07 DEBUG    [check_env.py:122] Creating Main Backup folder...
    2019-01-20 13:52:07 DEBUG    [check_env.py:125] OK: Created
    2019-01-20 13:52:07 DEBUG    [check_env.py:165] Full Backup directory does not exist
    2019-01-20 13:52:07 DEBUG    [check_env.py:166] Creating full backup directory...
    2019-01-20 13:52:07 DEBUG    [check_env.py:169] OK: Created
    2019-01-20 13:52:07 DEBUG    [check_env.py:185] Increment directory does not exist
    2019-01-20 13:52:07 DEBUG    [check_env.py:186] Creating increment backup directory...
    2019-01-20 13:52:07 DEBUG    [check_env.py:189] OK: Created
    2019-01-20 13:52:07 DEBUG    [check_env.py:215] OK: Check status
    2019-01-20 13:52:07 DEBUG    [backuper.py:694] - - - - You have no backups : Taking very first Full Backup! - - - -

The result of second run; it will take an incremental backup.

::

    $ sudo autoxtrabackup -v -lf /home/shako/.autoxtrabackup/autoxtrabackup.log \
    -l DEBUG --defaults-file=/home/shako/.autoxtrabackup/autoxtrabackup.cnf --backup

    2019-01-20 13:53:56 DEBUG    [__init__.py:71] <pid.PidFile object at 0x7f021c775868> entering setup
    2019-01-20 13:53:56 DEBUG    [__init__.py:161] <pid.PidFile object at 0x7f021c775868> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2019-01-20 13:53:56 DEBUG    [__init__.py:148] <pid.PidFile object at 0x7f021c775868> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2019-01-20 13:53:56 DEBUG    [check_env.py:49] Running mysqladmin command -> /usr/bin/mysqladmin --defaults-file= --user=root --password='*' status --host=127.0.0.1 --port=3306
    2019-01-20 13:53:56 DEBUG    [check_env.py:54] OK: Server is Up and running
    2019-01-20 13:53:56 DEBUG    [check_env.py:81] OK: /usr/bin/mysql exists
    2019-01-20 13:53:56 DEBUG    [check_env.py:93] OK: /usr/bin/mysqladmin exists
    2019-01-20 13:53:56 DEBUG    [check_env.py:66] Skipping my.cnf check, because it is not specified
    2019-01-20 13:53:56 DEBUG    [check_env.py:105] OK: XtraBackup exists
    2019-01-20 13:53:56 DEBUG    [check_env.py:118] OK: Main backup directory exists
    2019-01-20 13:53:56 DEBUG    [check_env.py:162] OK: Full Backup directory exists
    2019-01-20 13:53:56 DEBUG    [check_env.py:182] OK: Increment directory exists
    2019-01-20 13:53:56 DEBUG    [check_env.py:215] OK: Check status
    2019-01-20 13:53:56 DEBUG    [backuper.py:744] - - - - You have a full backup that is less than 86400 seconds old. - - - -
    2019-01-20 13:53:56 DEBUG    [backuper.py:745] - - - - We will take an incremental one based on recent Full Backup - - - -



You will have 2 separate folders inside backup directory:

::

    (.venv) shako@shako-localhost:~/XB_TEST$ cd backup_dir/
    (.venv) shako@shako-localhost:~/XB_TEST/backup_dir$ ls
    full  inc



We took full backup and it should be under the ``full`` directory:

::

    (.venv) shako@shako-localhost:~/XB_TEST/backup_dir$ ls full/
    2019-01-20_13-52-07


Incremental backups are inside ``inc`` directory:

::

    (.venv) shako@shako-localhost:~/XB_TEST/backup_dir$ ls inc/
    2019-01-20_13-53-59

If you want more incremental backups just run the same command again and again.


Prepare
-------
For preparing backups just use --prepare option. For our case we have a
full and 2 incremental backups:

::

    (.venv) shako@shako-localhost:~/XB_TEST/backup_dir$ ls full/
    2019-01-20_13-52-07
    (.venv) shako@shako-localhost:~/XB_TEST/backup_dir$ ls inc/
    2019-01-20_13-53-59  2019-01-20_13-56-42


All backups will be prepared
automatically.

You are going to have 3 options to choose:

1. Only prepare backups.
2. Prepare backups and restore immediately.
3. Restore from already prepared backup.

For now let's choose 1:

::

    $ sudo /home/shako/REPOS/MySQL-AutoXtraBackup/.venv/bin/autoxtrabackup --prepare -v -l DEBUG
    2019-01-20 14:02:57 DEBUG    [__init__.py:71] <pid.PidFile object at 0x7f91306ce868> entering setup
    2019-01-20 14:02:57 DEBUG    [__init__.py:161] <pid.PidFile object at 0x7f91306ce868> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2019-01-20 14:02:57 DEBUG    [__init__.py:148] <pid.PidFile object at 0x7f91306ce868> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
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

    mysql> show create table t1\G
    *************************** 1. row ***************************
           Table: t1
    Create Table: CREATE TABLE t1 (
      id int(11) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    1 row in set (0.01 sec)

    mysql> select * from t1;
    +----+
    | id |
    +----+
    |  1 |
    |  2 |
    |  3 |
    |  4 |
    |  5 |
    +----+
    5 rows in set (0.00 sec)

    mysql> delete from t1;
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

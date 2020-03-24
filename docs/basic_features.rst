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


The result of second run; it will take an incremental backup.

::

    $ sudo autoxtrabackup -v -lf /home/shako/.autoxtrabackup/autoxtrabackup.log \
    -l DEBUG --defaults-file=/home/shako/.autoxtrabackup/autoxtrabackup.cnf --backup




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

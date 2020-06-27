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

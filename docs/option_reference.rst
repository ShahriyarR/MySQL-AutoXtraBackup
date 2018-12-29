Option Reference
=================

The command line options to use:

.. code-block:: shell

    $ autoxtrabackup --help
    Usage: autoxtrabackup [OPTIONS]

    Options:
      --dry-run                       Enable the dry run.
      --prepare                       Prepare/recover backups.
      --backup                        Take full and incremental backups.
      --partial                       Recover specified table (partial recovery).
      --version                       Version information.
      --defaults-file TEXT            Read options from the given file  [default: /
                                      home/shako/.autoxtrabackup/autoxtrabackup.cn
                                      f]
      --tag TEXT                      Pass the tag string for each backup
      --show-tags                     Show backup tags and exit
      -v, --verbose                   Be verbose (print to console)
      -lf, --log-file TEXT            Set log file  [default: /home/shako/.autoxtr
                                      abackup/autoxtrabackup.log]
      -l, --log, --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                      Set log level  [default: DEBUG]
      --log-file-max-bytes INTEGER    Set log file max size in bytes  [default:
                                      1073741824]
      --log-file-backup-count INTEGER
                                      Set log file backup count  [default: 7]
      --keyring-vault INTEGER         Enable this when you pass keyring_vault
                                      options in default mysqld options in
                                      config[Only for using with --test-mode]
                                      [default: 0]
      --test-mode                     Enable test mode. Must be used with
                                      --defaults-file and only for TESTs for
                                      XtraBackup
      --help                          Print help message and exit.



dry-run
-------

--dry-run
Use this option to enable dry running. If you enable this, actual commands will not be executed but, will only be shown.
It is useful, when you want to see what is going to happen, if you run the actual process.

prepare
-------

--prepare
This option is for prepare and copy-back(recover) the backup.


backup
------

--backup
This option for taking backups. If it is first run, it will take full backup.
If you want incremental backups, just run same command as much as you want take incremental backups.

partial
-------

This option will let you recover only desired tables. The version of MySQL must be > 5.6.
It is using transportable tablespace concept.

version
-------

--version
Prints version information.

defaults-file
-------------

--defaults-file
The main config file to path to ``autoxtrabackup``. The default one is ``~/.autoxtrabackup/autoxtrabackup.cnf``.
In default config, the compression, encryption and streaming backups are disabled by defualt.

tag
----
--tag
This option enables creation of tags for backups.
The backup_tags.txt file will be created and stored inside backup directory.

show-tags
---------
It will show the backup tags and exit.

verbose, v
----------

--verbose, -v
This option enables to print to console the logging messages.

log-file, lf
------------

-lf, --log-file
Pass, the path for log file, for autoxtrabackup. Default is ``~/.autoxtrabackup/autoxtrabackup.log``

log-file-backup_count
---------------------

--log_file_backup_count
Set log file backup count. Default is 7

log-file-max-bytes
------------------

--log_file_max_bytes
Set log file max size in bytes. Default: 1073741824 bytes.

log, log-level
--------------

-l, --log, --log-level

Set the log level for tool. Can be DEBUG, INFO, WARNING, ERROR or CRITICAL. Default is DEBUG.

test-mode
---------

--test-mode
This option enables Test Mode and must be used with --defaults-file option.
Will not be available in default configuration file.
WARNING: It is not for daily usage. It is only and only for testing XtraBackup.

keyring-vault
-------------

--keyring_vault
Enable this when you pass keyring_vault options in default mysqld options in
config[Only for using with --test_mode] [default: 0]
This is for keyring_vault plugin testing.

help
----

--help
As name indicates.


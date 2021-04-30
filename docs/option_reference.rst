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
                                      Set log level  [default: INFO]
      --log-file-max-bytes INTEGER    Set log file max size in bytes  [default:
                                      1073741824]
      --log-file-backup-count INTEGER
                                      Set log file backup count  [default: 7]
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


help
----

--help
As name indicates.


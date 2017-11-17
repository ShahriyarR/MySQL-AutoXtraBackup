Option Reference
=================

The command line options to use:

.. code-block:: shell


    $ sudo autoxtrabackup
    Usage: autoxtrabackup [OPTIONS]

    Options:
      --dry_run                       Enable the dry run.
      --prepare                       Prepare/recover backups.
      --backup                        Take full and incremental backups.
      --partial                       Recover specified table (partial recovery).
      --version                       Version information.
      --defaults_file TEXT            Read options from the given file  [default:
                                      /etc/bck.conf]
      --tag TEXT                      Pass the tag string for each backup
      --show_tags                     Show backup tags and exit
      -v, --verbose                   Be verbose (print to console)
      -lf, --log_file TEXT            Set log file  [default:
                                      /var/log/autoxtrabackup.log]
      -l, --log [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                      Set log level  [default: WARNING]
      --test_mode                     Enable test mode.Must be used with
                                      --defaults_file and only for TESTs for
                                      XtraBackup
      --help                          Print help message and exit.


dry_run
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

defaults_file
-------------

--defaults_file
The main config file to path to ``autoxtrabackup``. The default one is ``/etc/bck.conf``.
In default config, the compression, encryption and streaming backups are disabled by defualt.

tag
----
--tag
This option enables creation of tags for backups.
The backup_tags.txt file will be created and stored inside backup directory.

show_tags
---------
It will show the backup tags and exit.

verbose, v
----------

--verbose, -v
This option enables to print to console the logging messages.

log_file, lf
------------

-lf, --log_file
Pass, the path for log file, for autoxtrabackup. Default is ``/var/log/autoxtrabackup.log``

log
----

-l, --log

Set the log level for tool.

test_mode
---------

--test_mode
This option enables Test Mode and must be used with --defaults_file option.
WARNING: It is not for daily usage. It is only and only for testing XtraBackup.


help
----

--help
As name indicates.


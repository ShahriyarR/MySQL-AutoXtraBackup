Basic Overview
==============

Project Structure
-----------------

XtraBackup is a powerful open-source hot online backup tool for MySQL
from Percona. This script is using XtraBackup for full and incremental
backups, also for preparing backups, as well as to restore. Here is project path tree:

::

    * master_backup_script  -- Full and Incremental backup taker script.
    * backup_prepare        -- Backup prepare and restore script.
    * partial_recovery      -- Partial table recovery script.
    * general_conf          -- All-in-one config file's and config reader class folder.
    * prepare_env_test_mode -- The directory for --test_mode actions.
    * test                  -- The directory for test things.
    * setup.py              -- Setuptools Setup file.
    * autoxtrabackup.py     -- Commandline Tool provider script.
    * VagrantFile           -- The Vagrant thing for starting using this tool[will be useful to contributors].
    * ~/.autoxtrabackup/autoxtrabackup.cnf        -- Config file will be created from general_conf/autoxtrabackup.cnf


Available Options
-----------------

.. code-block:: shell

    $ autoxtrabackup --help
    Usage: autoxtrabackup [OPTIONS]

    Options:
      --dry_run                       Enable the dry run.
      --prepare                       Prepare/recover backups.
      --backup                        Take full and incremental backups.
      --partial                       Recover specified table (partial recovery).
      --version                       Version information.
      --defaults_file TEXT            Read options from the given file  [default:
                                    ~/.autoxtrabackup/autoxtrabackup.cnf]
      --tag TEXT                      Pass the tag string for each backup
      --show_tags                     Show backup tags and exit
      -v, --verbose                   Be verbose (print to console)
      -lf, --log_file TEXT            Set log file  [default: ~/.autoxtrabackup/autoxtrabackup.log]
      -l, --log [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                      Set log level  [default: WARNING]
      --log_file_max_bytes INTEGER    Set log file max size in bytes  [default:
                                      1073741824]
      --log_file_backup_count INTEGER
                                      Set log file backup count  [default: 7]
      --keyring_vault INTEGER         Enable this when you pass keyring_vault
                                      options in default mysqld options in
                                      config[Only for using with --test_mode]
                                      [default: 0]
      --test_mode                     Enable test mode. Must be used with
                                      --defaults_file and only for TESTs for
                                      XtraBackup
      --help                          Print help message and exit.





Usage
-----

::

    1. Install it.
    2. Edit /etc/bck.conf file to reflect your environment or create your own config.
    3. Pass this config file to autoxtrabackup with --defaults_file and begin to backup/prepare/restore.




Logging
--------

The logging mechanism is using Python3 logging.
It lets to log directly to console and also to file.

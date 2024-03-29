Basic Overview
==============

Project Structure
-----------------

XtraBackup is a powerful open-source hot online backup tool for MySQL
from Percona. This script is using XtraBackup for full and incremental
backups, also for preparing backups, as well as to restore. Here is project path tree:

::

    * mysql_autoxtrabackup                       -- source directory
    * mysql_autoxtrabackup/backup_backup         -- Full and Incremental backup taker script.
    * mysql_autoxtrabackup/backup_prepare        -- Backup prepare and restore script.
    * mysql_autoxtrabackup/general_conf          -- All-in-one config file's and config reader class folder.
    * mysql_autoxtrabackup/process_runner        -- The directory for process runner script.
    * mysql_autoxtrabackup/autoxtrabackup.py     -- Commandline Tool provider script.
    * mysql_autoxtrabackup/api                   -- The API server written in FastAPI.
    * tests                                      -- The directory for test things.
    * ~/.autoxtrabackup/autoxtrabackup.cnf       -- Config file will be created during setup.


Available Options
-----------------

.. code-block:: shell

    $ autoxtrabackup --help
    Usage: autoxtrabackup [OPTIONS]

    Options:
      --dry-run                       Enable the dry run.
      --prepare                       Prepare/recover backups.
      --run-server                    Start the FastAPI app for serving API
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






Usage
-----

::

    1. Install it.
    2. Edit ~/.autoxtrabackup/autoxtrabackup.cnf(default config) file to reflect your environment or create your own config.
    3. Pass config file to autoxtrabackup with --defaults_file option(if you are not using default config) and begin to backup/prepare/restore.




Logging
--------

The logging mechanism is using Python3 logging.
It lets to log directly to console and also to file.

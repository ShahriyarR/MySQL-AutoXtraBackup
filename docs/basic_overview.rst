Basic Overview
==============

Project Structure
-----------------

XtraBackup is a powerful open-source hot online backup tool for MySQL
from Percona. This script is using XtraBackup for full and incremental
backups, also for preparing backups, as well as to restore. Here is project path tree:

::

    * backup_dir            -- The main folder for storing backups (optional)
    * master_backup_script  -- Full and Incremental backup taker script.
    * backup_prepare        -- Backup prepare and restore script.
    * partial_recovery      -- Partial table recovery script.
    * general_conf          -- All-in-one config file's and config reader class folder.
    * setup.py              -- Setuptools Setup file.
    * autoxtrabackup.py     -- Commandline Tool provider script.
    * VagrantFile           -- The Vagrant thing for starting using this tool[will be useful to contributors]
    * /etc/bck.conf         -- Config file will be created from general_conf/bck.conf


Available Options
-----------------

::


    $ autoxtrabackup --help
    Usage: autoxtrabackup [OPTIONS]

    Options:
        --dry_run                       Enable the dry run.
        --prepare                       Prepare/recover backups.
        --backup                        Take full and incremental backups.
        --partial                       Recover specified table (partial recovery).
        --version                       Version information.
        --defaults_file TEXT            Read options from the given file
        -v, --verbose                   Be verbose (print to console)
        -l, --log [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                          Set log level
        --test_mode                     Enable test mode.Must be used with
                                          --defaults_file and only for TESTs for
                                          XtraBackup
        --help                          Show this message and exit.





Usage
-----

::

    1. Install it
    2. Edit /etc/bck.conf file to reflect your environment or create your own config and pass it to script as --defaults_file

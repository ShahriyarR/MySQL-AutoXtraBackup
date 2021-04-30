The structure of configuration file
===================================

Defaults file explained
-----------------------

There are some changes related to default config file.
First and foremost it is renamed and now located in home of user in .autoxtrabackup folder.
Keep in mind that config file is going to be dynamically generated during setup process.
The default config will be located ~/.autoxtrabackup/autoxtrabackup.cnf.
The available options are divided into optional and primary options.
Options are quite self-explanatory.
I have tried to make them similar to existing options in XtraBackup and MySQL.
You can use another configuration file using ``--defaults_file`` option.

Let's clarify the config file structure a bit.

[MySQL]
--------

The [MySQL] category is for specifying information about MySQL instance.

::

    [MySQL]
    mysql=/usr/bin/mysql
    mycnf=/etc/my.cnf
    mysqladmin=/usr/bin/mysqladmin
    mysql_user=root
    mysql_password=12345
    ## Set either mysql_socket only, OR host + port. If both are set mysql_socket is used
    #mysql_socket=/var/lib/mysql/mysql.sock
    mysql_host=127.0.0.1
    mysql_port=3306
    datadir=/var/lib/mysql


[Logging]
---------

Options for logging mechanism of tool.(added in 1.5.4 version)

::

    [Logging]
    #[debug,info,warning,error,critical]
    log = DEBUG
    log_file_max_bytes = 1073741824
    log_file_backup_count = 7

[Backup]
--------

The [Backup] category is for specifying information about backup/prepare process itself.

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

+----------------------+----------+-----------------------------------------------------------------------------+
| **Key**              | Required | **Description**                                                             |
+----------------------+----------+-----------------------------------------------------------------------------+
| pid_dir              | no       | Directory where the PID file will be created in                             |
+----------------------+----------+-----------------------------------------------------------------------------+
| tmp_dir               | yes     | Used for moving current running mysql-datadir to when copying-back          |
|                      |          | (restoring) an archive                                                      |
+----------------------+----------+-----------------------------------------------------------------------------+
| backup_dir            | yes     | Directory will be used for storing the backups. Subdirs ./full and ./inc    |
|                      |          | will be created                                                             |
+----------------------+----------+-----------------------------------------------------------------------------+
| backup_tool          | yes      | Full path to Percona xtrabackup executable used when making backup          |
+----------------------+----------+-----------------------------------------------------------------------------+
| prepare_tool         | no       | Full path to Percona xtrabackup executable used when preparing (restoring)  |
+----------------------+----------+-----------------------------------------------------------------------------+
| xtra_prepare         | yes      | Options passed to xtrabackup when preparing.                                |
|                      |          | '--apply-log-only' is essential to allow further incremental                |
|                      |          | backups to be made. See[1]                                                  |
+----------------------+----------+-----------------------------------------------------------------------------+
| xtra_backup          | no       | pass additional options for backup stage                                    |
+----------------------+----------+-----------------------------------------------------------------------------+
| xtra_prepare_options | no       | pass additional options for prepare stage                                   |
+----------------------+----------+-----------------------------------------------------------------------------+
| xtra_options         | no       | pass general additional options; it will go to both for backup and prepare  |
+----------------------+----------+-----------------------------------------------------------------------------+
| archive_dir          | no       | Directory for storing archives (tar.gz or otherwise). Cannot be inside the  |
|                      |          | 'backupdir' above                                                           |
+----------------------+----------+-----------------------------------------------------------------------------+
| prepare_archive      | no       | Prepare backups before archiving them.                                      |
+----------------------+----------+-----------------------------------------------------------------------------+
| move_archive         | no       | When rotating backups to archive move instead of compressing with tar.gz    |
+----------------------+----------+-----------------------------------------------------------------------------+
| full_backup_interval | no       | Maximum interval after which a new full backup will be made                 |
+----------------------+----------+-----------------------------------------------------------------------------+
| archive_max_size     | no       | Delete archived backups after X GiB                                         |
+----------------------+----------+-----------------------------------------------------------------------------+
| archive_max_duration | no       | Delete archived backups after X Days                                        |
+----------------------+----------+-----------------------------------------------------------------------------+
| partial_list         | no       | Specify database names or table names.                                      |
|                      |          | **WARNING**: Enable this if you want to take partial backups                |
+----------------------+----------+-----------------------------------------------------------------------------+

[Compress]
----------

The [Compress] category is for enabling backup compression.

The options will be passed to XtraBackup.

::

    [Compress]
    #optional
    #enable only if you want to use compression.
    compress = quicklz
    compress_chunk_size = 65536
    compress_threads = 4
    decompress = TRUE
    #enable if you want to remove .qp files after decompression.(Available from PXB 2.3.7 and 2.4.6)
    remove_original = FALSE

[Encrypt]
---------

The [Encrypt] category is for enabling backup encryption.

The options will be passed to XtraBackup.

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

[Xbstream]
----------

The [Xbstream] category is for enabling backup streaming.

The options will be passed to XtraBackup.

::

    [Xbstream]
    #experimental
    #enable this, if you want to stream your backups
    xbstream = /usr/bin/xbstream
    stream = xbstream
    xbstream_options = -x --parallel=100
    xbs_decrypt = 1
    # warn, enable this, if you want to stream your backups to remote host
    #remote_stream = ssh xxx.xxx.xxx.xxx


Deprecated feature, will be removed in next releases[Do not use]

::

    #Optional remote syncing
    #[Remote]
    #remote_conn=root@xxx.xxx.xxx.xxx
    #remote_dir=/home/sh/Documents

[Commands]
----------

The [Commands] category is for specifying some options for copy-back/restore actions.

::

    [Commands]
    start_mysql_command=service mysql start
    stop_mysql_command=service mysql stop
    #Change user:group respectively
    chown_command=chown -R mysql:mysql


[1]: https://www.percona.com/doc/percona-xtrabackup/LATEST/xtrabackup_bin/incremental_backups.html#preparing-the-incremental-backups


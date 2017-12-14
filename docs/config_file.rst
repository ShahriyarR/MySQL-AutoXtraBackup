The structure of configuration file
===================================

Defaults file explained
-----------------------

The default config file is located /etc/bck.conf.
The available options are divided into optional and primary options.
Options are quite self-explanatory.
I have tried to make them similar to existing options in XtraBackup and MySQL.
You can use another configuration file using ``--defaults_file`` option.

Let's clarify the config file structure a bit.
The [MySQL] category is for specifying information about MySQL instance.

::

    [MySQL]
    mysql=/usr/bin/mysql
    mycnf=/etc/my.cnf
    mysqladmin=/usr/bin/mysqladmin
    mysql_user=root
    mysql_password=12345
    #Set either mysql_socket or host and post. If both are set socket is used
    #mysql_socket=/var/lib/mysql/mysql.sock
    mysql_host=127.0.0.1
    mysql_port=3306
    datadir=/var/lib/mysql


The [Backup] category is for specifying information about backup/prepare process itself.

::

    [Backup]
    #Optional: set pid directory
    pid_dir=/tmp/MySQL-AutoXtraBackup
    tmpdir=/home/shahriyar.rzaev/XB_TEST/mysql_datadirs
    #Optional: set warning if pid of backup us running for longer than X
    pid_runtime_warning=2 Hours
    backupdir=/home/shahriyar.rzaev/XB_TEST/backup_dir
    backup_tool=/usr/bin/xtrabackup
    #Optional: specify different path/version of xtrabackup here for prepare
    #prepare_tool=
    xtra_prepare=--apply-log-only
    #Optional: pass additional options for backup stage
    #xtra_backup=--compact
    #Optional: pass additional options for prepare stage
    #xtra_prepare_options=--rebuild-indexes
    #Optional: pass general additional options; it will go to both for backup and prepare
    #xtra_options=--binlog-info=ON --galera-info
    xtra_options=--no-version-check
    #Optional: set archive and rotation
    #archive_dir=/home/shahriyar.rzaev/XB_TEST/backup_archives
    #full_backup_interval=1 day
    #max_archive_size=100GiB
    #max_archive_duration=4 Days
    #Optional WARNING(Enable this if you want to take partial backups). Specify database names or table names.
    #partial_list=test.t1 test.t2 dbtest


The [Compress] category is for enabling backup compression.
The options will be passed to XtraBackup.

::

    [Compress]
    #Optional
    #Enable only if you want to use compression.
    #compress=quicklz
    #compress_chunk_size=65536
    #compress_threads=4
    #decompress=TRUE
    #Enable if you want to remove .qp files after decompression.(Not available yet, will be released with XB 2.3.7 and 2.4.6)
    #remove_original=FALSE

The [Encrypt] category is for enabling backup encryption.
The options will be passed to XtraBackup.

::

    [Encrypt]
    #Optional
    #Enable only if you want to create encrypted backups
    #xbcrypt=/usr/bin/xbcrypt
    #encrypt=AES256
    # Please note that --encrypt-key and --encrypt-key-file are mutually exclusive
    #encrypt_key='VVTBwgM4UhwkTTV98fhuj+D1zyWoA89K'
    #encrypt_key_file=/path/to/file/with_encrypt_key
    #encrypt_threads=4
    #encrypt_chunk_size=65536
    #decrypt=AES256
    #Enable if you want to remove .qp files after decompression.(Not available yet, will be released with XB 2.3.7 and 2.4.6)
    #remove_original=FALSE

The [Xbstream] category is for enabling backup streaming.
The options will be passed to XtraBackup.

::

    [Xbstream]
    #EXPERIMENTAL
    # Enable this, if you want to stream your backups
    #xbstream=/usr/bin/xbstream
    #stream=xbstream
    #Optional
    #Please enable this and disable all other options here, for tar streaming
    #stream=tar
    #xbstream_options=-x --parallel=100
    #xbs_decrypt=1
    # WARN, enable this, if you want to stream your backups to remote host
    #remote_stream=ssh xxx.xxx.xxx.xxx


Deprecated feature, will be removed in next releases

::

    #Optional remote syncing
    #[Remote]
    #remote_conn=root@xxx.xxx.xxx.xxx
    #remote_dir=/home/sh/Documents

The [Commands] category is for specifying some options for copy-back/restore actions.

::

    [Commands]
    start_mysql_command=service mysql start
    stop_mysql_command=service mysql stop
    #Change user:group respectively
    chown_command=chown -R mysql:mysql

The [TestConf] category is part of XtraBackup testing procedures and is not for daily usage.
So just ignore this, it is actually for myself :)

::

    # Do not touch; this is for --test_mode, which is testing for XtraBackup itself.
    [TestConf]
    ps_branches=5.5 5.6 5.7
    pxb_branches=2.3 2.4
    gitcmd=--recursive --depth=1 https://github.com/percona/percona-server.git
    pxb_gitcmd=https://github.com/percona/percona-xtrabackup.git
    testpath=/home/shahriyar.rzaev/XB_TEST/server_dir
    incremental_count=3
    #make_slaves=1
    xb_configs=xb_2_4_ps_5_6.conf xb_2_4_ps_5_7.conf xb_2_3_ps_5_6.conf xb_2_3_ps_5_5.conf xb_2_4_ps_5_5.conf
    default_mysql_options=--log-bin=mysql-bin,--log-slave-updates,--server-id={},--gtid-mode=ON,--enforce-gtid-consistency,--binlog-format=row
    mysql_options=--innodb_buffer_pool_size=1G 2G 3G,--innodb_log_file_size=1G 2G 3G,--innodb_page_size=4K 8K 16K 32K 64K

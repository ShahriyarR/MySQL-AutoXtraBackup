Advance features
=================

Compressed backups
------------------

To enable compression support just uncomment the options under
[Compress] category inside main configuration file:

::

    [Compress]
    #Optional
    #Enable only if you want to use compression.
    compress=quicklz
    compress_chunk_size=65536
    compress_threads=4
    decompress=TRUE
    #Enable if you want to remove .qp files after decompression.(Available from PXB 2.3.7 and 2.4.6)
    remove_original=FALSE


Encrypted backups
-----------------

To enable encryption support uncomment the options under [Encryption]
category:

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


Partial backups
---------------

It is possible to take partial full and incremental backups. The idea is, to take specified table(or database) as full backup,
then to take incremental backups based on this one table.
You can achieve this by enabling ``partial_list`` option from config file:


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


Run it and notice that backup command has changed (see ``--databases`` option for xtrabackup command):

In the same way you can take incremental backup of specified tables.

The prepare process is the same as ordinary prepare, just run autoxtrabackup with ``--prepare`` option.

Decompressing and Decrypting backups
------------------------------------

We took Compressed and Encrypted backups.
It is time to prepare them.
autoxtrabackup will prepare all backups automatically, by first decrypting then
decompressing step-by-step.
All backups first will be decrypted then decompressed and then
prepared.
You can also optionally enable ``--remove-original`` option to
remove ``.xbcrypt`` and ``.qp`` files from backup directory during prepare
process.
Read about this option here -> `--remove-original <https://www.percona.com/doc/percona-xtrabackup/2.4/xtrabackup_bin/xbk_option_reference.html#cmdoption-xtrabackup-remove-original>`_

autoxtrabackup with --dry_run option
------------------------------------

For testing purposes or just to show what is going on, with autoxtrabackup backup and prepare steps.
You can append ``--dry_run`` option, to show commands but not to run them.
Taking backup:

::


        $ autoxtrabackup -v -lf /home/shahriyar.rzaev/autoxtrabackup_2_3_5_6.log -l DEBUG \
        --defaults-file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.cnf --backup --dry_run


Preparing backups:

::


        $ autoxtrabackup -v -lf /home/shahriyar.rzaev/autoxtrabackup_2_3_5_6.log -l DEBUG \
        --defaults-file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.cnf --prepare --dry_run


The end.

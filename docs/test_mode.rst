Using --test_mode
================

I have added --test_mode option for testing XtraBackup itself.

> This is not for general usage. Use it for testing PXB.

What is going to be happened with --test_mode?
The flow is as described:

* Clone percona-qa repo
* Clone Percona Server 5.6 and 5.7 from github.
* Build PS servers in debug mode.
* Get 2.3 and 2.4 versions of XtraBackup.
* Generate autoxtrabackup .conf files for each versions PS and XtraBackup:

  xb_2_3_ps_5_5.cnf

  xb_2_3_ps_5_6.cnf

  xb_2_4_ps_5_5.cnf

  xb_2_4_ps_5_6.cnf

  xb_2_4_ps_5_7.cnf


* Pass different combination of options to PS(MySQL) start command; Initialize PS servers each time with different options.
  These options are going to be passed in single thread manner. You will see the messages about cycle0, cycle1 - each those cycles are going to be the unique combination of passed options.
* Run sysbench against each started PS server - this will prepare the tables which are needed to run tests(update, alters on them).
* Took backup in cycles for each started PS - cycle0 will run all sort of backup and prepare stages and then it will start from scratch for cycle1 and so on.
* If make_slaves option is defined in config file, then it will create slave1 server from this backup(i.e copy-back to another directory and start slave from it).
* Then take backup from this new slave1, prepare and copy-back to new slave2 directory for starting new slave2.
* Run pt-table-checksum on master to check backup consistency between all nodes.

> Those all actions mentione above will happen for each cycle

Now let's talk a bit more here.

Preparing test environment
--------------------------

For simplicity I have created ``prepare_env.bats`` file for preparing test environment in fully automated manner.
You need BATS_. for this.

.. _BATS: https://github.com/sstephenson/bats

Prior actions can be taken we should setup all necessary things. Please note that I have tested those things only under Centos 7 and Ubuntu Bionic.
The setup process is using default config file ~/.autoxtrabackup/autoxrtabackup.cnf. By default --test_mode settings are disabled in it. So please enable them and update respectively:

# Do not touch; this is for --test_mode, which is testing for XtraBackup itself.

::

    [TestConf]
    ps_branches = 5.5 5.6 5.7
    pxb_branches = 2.3 2.4
    gitcmd = --recursive --depth=1 https://github.com/percona/percona-server.git
    pxb_gitcmd = https://github.com/percona/percona-xtrabackup.git
    testpath = /home/shahriyar.rzaev/XB_TEST/server_dir
    incremental_count = 3
    xb_configs = xb_2_4_ps_5_6.conf xb_2_4_ps_5_7.conf xb_2_3_ps_5_6.conf xb_2_3_ps_5_5.conf xb_2_4_ps_5_5.conf
    make_slaves = 1
    default_mysql_options = --early-plugin-load=keyring_file.so,--keyring_file_data={}/mysql-keyring/keyring,--log-bin=mysql-bin,--log-slave-updates,--server-id={},--gtid-mode=ON,--enforce-gtid-consistency,--binlog-format=row,--encrypt_binlog=ON,--master_verify_checksum=ON,--binlog_checksum=CRC32,--innodb_encrypt_tables=ON,--innodb_encrypt_online_alter_logs=ON,--innodb_temp_tablespace_encrypt=ON
    mysql_options = --innodb_buffer_pool_size=1G 2G 3G,--innodb_log_file_size=1G 2G 3G,--innodb_page_size=4K 8K 16K 32K

I think the options are quite clear.
The only thing is specify testpath under [TestConf] - in which path the test environment should be constructed, created.

**Running whole environment setup**

The thing you need is to run:

``bats prepare_env.bats``

That's it, it will do the all job.

**Running specific bats files**

I have prepared separate bats files to run specific things:

* ``test_clone_percona_qa.bats`` -> will clone percona-qa repo.
* ``test_clone_ps_server_from_conf.bats`` -> will clone PS servers based on specified branches.
* ``test_clone_pxb.bats`` -> will clone specified PXB based on specified branches.
* ``test_build_pxb.bats`` -> will build cloned PXBs and create separate binary archives for each branch.
* ``test_build_server.bats`` -> will build PS servers.
* ``test_prepare_startup.bats`` -> will run startup.sh from percona-qa inside PS basedirs.
* ``test_prepare_start_dynamic.bats`` -> will create start_dynamic scripts inside PS basedirs, which is going to be used in slave setup etc.
* ``test_start_server.bats`` -> will start PS servers with default values(executing start script inside basedirs).
* ``test_extract_xb_archive.bats`` -> will extracting PXB binary archives to the target folder inside testpath(which is grabbed from config file).
* ``test_generate_config_files.bats`` -> will generate specific config files based on PXB and PS versions.

After running this you will likely have something like in your test path:


.. code-block:: shell

    $ ls
    percona-qa                                PS250418-5.7.21-21-linux-x86_64-debug                           PS-5.5-trunk_dbg  PXB-2.3             xb_2_4_ps_5_5.cnf
    percona-xtrabackup-2.3.x-debug.tar.gz     PS250418-percona-server-5.5.59-38.11-linux-x86_64-debug.tar.gz  PS-5.6-trunk      PXB-2.4             xb_2_4_ps_5_6.cnf
    percona-xtrabackup-2.4.x-debug.tar.gz     PS250418-percona-server-5.6.39-83.1-linux-x86_64-debug.tar.gz   PS-5.6-trunk_dbg  target              xb_2_4_ps_5_7.cnf
    PS250418-5.5.59-38.11-linux-x86_64-debug  PS250418-percona-server-5.7.21-21-linux-x86_64-debug.tar.gz     PS-5.7-trunk      xb_2_3_ps_5_5.cnf
    PS250418-5.6.39-83.1-linux-x86_64-debug   PS-5.5-trunk                                                    PS-5.7-trunk_dbg  xb_2_3_ps_5_6.cnf                                                 target

So you have everything you need to run combination of tests for XtraBackup. Even configs are generated for you.


Running test mode
-----------------

For this, just run autoxtrabackup with respective config file which was generated automatically:

.. code-block:: shell

    autoxtrabackup -lf /home/shahriyar.rzaev/XB_TEST/autoxtrabackup.log \
    --defaults_file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.cnf -v -l DEBUG --test_mode

This will start autoxtrabackup in test mode and will run full cycle based on combinations of mysql options passed to PS.
To be clear, for eg, we have 50 different combinations of starting PS, then we will have 50 cycles of backup/restore process.


Where I can add more mysql options?
-----------------------------------

In generated configs you can add more PS(mysql) startup/initialization options.
For test mode [TestConf] category is relevant. Let's go through options

::

    # Do not touch; this is for --test_mode, which is testing for XtraBackup itself.
    [TestConf]
    ps_branches = 5.5 5.6 5.7
    pxb_branches = 2.3 2.4
    gitcmd = --recursive --depth=1 https://github.com/percona/percona-server.git
    pxb_gitcmd = https://github.com/percona/percona-xtrabackup.git
    testpath = /home/shahriyar.rzaev/XB_TEST/server_dir
    incremental_count = 3
    xb_configs = xb_2_4_ps_5_6.conf xb_2_4_ps_5_7.conf xb_2_3_ps_5_6.conf xb_2_3_ps_5_5.conf xb_2_4_ps_5_5.conf
    make_slaves = 1
    default_mysql_options = --early-plugin-load=keyring_file.so,--keyring_file_data={}/mysql-keyring/keyring,--log-bin=mysql-bin,--log-slave-updates,--server-id={},--gtid-mode=ON,--enforce-gtid-consistency,--binlog-format=row,--encrypt_binlog=ON,--master_verify_checksum=ON,--binlog_checksum=CRC32,--innodb_encrypt_tables=ON,--innodb_encrypt_online_alter_logs=ON,--innodb_temp_tablespace_encrypt=ON
    mysql_options = --innodb_buffer_pool_size=1G 2G 3G,--innodb_log_file_size=1G 2G 3G,--innodb_page_size=4K 8K 16K 32K

The important thing to remember here if you wanto to pass default options to mysqld startup then please add them to:

``default_mysql_options`` default mysql options to pass to PS start script.

If you want to create option combinations then use:

``mysql_options`` option combinations are for passing mysql startup/initialization options to PS start script.

Internally, based on mysql options, the combination of those options will be created.
For eg, --innodb_buffer_pool_size=1G 2G 3G there is 3 possible value for --innodb_buffer_pool_size
and they will be passed separately as unique option combination.
So just add more options to ``mysql_options`` if you want more.


Important things to remember
-----------------------------

This is tested only with Percona Servers, but can be expanded.
Also --test_mode option is mutually exclusive with other options such as --backup and --prepare.
So basically do not touch this, if you are not testing XtraBackup.
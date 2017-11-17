Using --test_mode
================

I have added --test_mode option for testing XtraBackup itself.

> This is not for general usage.

Here is the brief flow for this:

* Clone percona-qa repo
* Clone Percona Server 5.6 and 5.7 from github.
* Build PS servers in debug mode.
* Get 2.3 and 2.4 versions of XtraBackup
* Generate autoxtrabackup .conf files for each version PS and XtraBackup
* Pass different combination of options to PS start command; Initialize PS servers each time with different options.
* Run sysbench against each started PS server
* Took backup in cycles for each started PS + prepare
* If make_slaves is defined then create slave1 server from this backup(i.e copy-back to another directory and start slave from it)
* Then take backup, prepare and copy-back from this new slave1 and create slave2
* Run pt-table-checksum on master to check backup consistency

Now let's talk a bit more here.

Preparing test environment
--------------------------

For simplicity I have created ``prepare_env.bats`` file for preparing test environment in fully automated manner.
You need BATS_. for this.

.. _BATS: https://github.com/sstephenson/bats

After running this you will likely have something like in your test path:


.. code-block:: shell

    [shahriyar.rzaev@qaserver-02 ~]$ cd XB_TEST/
    [shahriyar.rzaev@qaserver-02 XB_TEST]$ ls
    server_dir
    [shahriyar.rzaev@qaserver-02 XB_TEST]$ ls server_dir/
    percona-qa                                              PS231017-percona-server-5.6.37-82.2-linux-x86_64-debug.tar.gz  PS-5.6-trunk_dbg  xb_2_3_ps_5_6.conf
    percona-xtrabackup-2.3.x-debug.tar.gz                   PS231017-percona-server-5.7.19-17-linux-x86_64-debug           PS-5.7-trunk      xb_2_4_ps_5_6.conf
    percona-xtrabackup-2.4.x-debug.tar.gz                   PS231017-percona-server-5.7.19-17-linux-x86_64-debug.tar.gz    PS-5.7-trunk_dbg  xb_2_4_ps_5_7.conf
    PS231017-percona-server-5.6.37-82.2-linux-x86_64-debug  PS-5.6-trunk                                                   target

So you have everything you need to run combination of tests for XtraBackup. Even configs are generated for you.


Running test mode
-----------------

For this, just run autoxtrabackup with respective config file:

.. code-block:: shell

    autoxtrabackup -v -l DEBUG --test_mode \
    --defaults_file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.conf

This will start autoxtrabackup in test mode and will run full cycle based on combinations of mysql options passed to PS.
To be clear, for eg, we have 50 different combinations of starting PS, then we will have 50 cycles of backup/restore process.


Where I can add more mysql options?
-----------------------------------

In generated configs you can add more PS(mysql) startup/initialization options.
For test mode [TestConf] category is relevant. Let's go through options

::

    # Do not touch; this is for --test_mode, which is testing for XtraBackup itself.
    [TestConf]
    ps_branches=5.6 5.7
    gitcmd=--recursive --depth=1 https://github.com/percona/percona-server.git
    testpath=/home/shahriyar.rzaev/XB_TEST/server_dir
    incremental_count=3
    #make_slaves=1
    xb_configs=xb_2_4_ps_5_6.conf xb_2_4_ps_5_7.conf xb_2_3_ps_5_6.conf
    default_mysql_options=--log-bin=mysql-bin,--log-slave-updates,--server-id={},--gtid-mode=ON,--enforce-gtid-consistency,--binlog-format=row
    mysql_options=--innodb_buffer_pool_size=1G 2G 3G,--innodb_log_file_size=1G 2G 3G,--innodb_page_size=4K 8K 16K 32K 64K

``ps_branches`` is for specifying PS branches in github.

``gitcmd`` is for passing git command for git clone.

``testpath`` is for passing the path for test mode.

``incremental_count`` specify how many incremental backups the tool should take.

``make_slaves`` specify if you want to create slave servers.

``xb_configs`` is for passing config files to be generated.

``default_mysql_options`` default mysql options to pass to PS start script.

``mysql_options`` option combinations are for passing mysql startup/initialization options to PS start script.

Internally, based on mysql options, the combination of those options will be created.
So just add more options to ``mysql_options`` if you want more.


Important things to remember
-----------------------------

This is tested only with Percona Servers, but can be expanded.
Also --test_mode option is mutually exclusive with other options such as --backup and --prepare.
So basically do not touch this, if you are not testing XtraBackup.
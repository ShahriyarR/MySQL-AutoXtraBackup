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
* Took backup in cycles for each started PS + prepare + restore.

Now let's talk a bit more here.

Preparing test environment
--------------------------

For simplicity I have created ``prepare_env.bats`` file for preparing test environment in fully automated manner.
You need _BATS: https://github.com/sstephenson/bats for this.

After running this you will likely have something like in your test path:


::

        [shahriyar.rzaev@qaserver-02 ~]$ cd XB_TEST/
        [shahriyar.rzaev@qaserver-02 XB_TEST]$ ls
        server_dir
        [shahriyar.rzaev@qaserver-02 XB_TEST]$ ls server_dir/
        percona-qa                                              PS231017-percona-server-5.6.37-82.2-linux-x86_64-debug.tar.gz  PS-5.6-trunk_dbg  xb_2_3_ps_5_6.conf
        percona-xtrabackup-2.3.x-debug.tar.gz                   PS231017-percona-server-5.7.19-17-linux-x86_64-debug           PS-5.7-trunk      xb_2_4_ps_5_6.conf
        percona-xtrabackup-2.4.x-debug.tar.gz                   PS231017-percona-server-5.7.19-17-linux-x86_64-debug.tar.gz    PS-5.7-trunk_dbg  xb_2_4_ps_5_7.conf
        PS231017-percona-server-5.6.37-82.2-linux-x86_64-debug  PS-5.6-trunk                                                   target

So you have everything you need to run combination of tests for XtraBackup. Even ``xb_2_3_ps_5_6.conf`` configs are generated here.


Running test mode
-----------------

For this, just run autoxtrabackup with respective config file:

::

    autoxtrabackup -v -l DEBUG --test_mode --defaults_file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.conf

This will start autoxtrabackup in test mode and will run full cycle based on combinations of mysql options passed to PS.
To be clear, for eg, we have 50 different combinations of starting PS, then we will have 50 cycles of backup/restore process.


Where I can add more mysql options?
-----------------------------------

In generated configs you can add more PS(mysql) startup/initialization options:

::

    [TestConf]
    ps_branches = 5.6 5.7
    gitcmd = --recursive --depth=1 https://github.com/percona/percona-server.git
    testpath = /home/shahriyar.rzaev/XB_TEST/server_dir
    incremental_count = 3
    xb_configs = xb_2_4_ps_5_6.conf xb_2_4_ps_5_7.conf xb_2_3_ps_5_6.conf
    mysql_options = --innodb_buffer_pool_size=1G 2G 3G,--innodb_log_file_size=1G 2G 3G,--innodb_page_size=4K 8K 16K 32K 64K

See ``mysql_options`` parameter. The options are comma separated.


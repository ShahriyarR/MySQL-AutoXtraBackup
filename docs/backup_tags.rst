Backup Tags
===========

The backup tags actually is a result of feature requests by community member `Yusif Yusifli <https://github.com/Komport/>`_.
Read discussions about feature requests below:

`#163 <https://github.com/ShahriyarR/MySQL-AutoXtraBackup/issues/163>`_.
`#164 <https://github.com/ShahriyarR/MySQL-AutoXtraBackup/issues/164>`_.
`#210 <https://github.com/ShahriyarR/MySQL-AutoXtraBackup/issues/210>`_.

So basically how to take backups and create a tag for it?

Taking full backup:
------------------

::

    $ sudo autoxtrabackup --tag="My Full backup" -v \
    -lf /home/shahriyar.rzaev/autoxtrabackup_2_4_5_7.log \
    -l DEBUG --defaults-file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.conf --backup

Taking incremental one:
----------------------

::

    $ autoxtrabackup --tag="First incremental backup" -v \
    -lf /home/shahriyar.rzaev/autoxtrabackup_2_4_5_7.log \
    -l DEBUG --defaults-file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.conf --backup

Taking second incremental:
-------------------------

::

    $ autoxtrabackup --tag="Second incremental backup" -v \
    -lf /home/shahriyar.rzaev/autoxtrabackup_2_4_5_7.log \
    -l DEBUG --defaults-file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.conf --backup

To list available tags(backups):
-------------------------------
For eg, if full backup failed, the result will be something like this:

::

    $ sudo autoxtrabackup --show_tags \
    --defaults-file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.conf
    Backup             	Type	Status	Completion_time    	Size	TAG
    ----------------------------------------------------------------------------------
    2017-12-14_12-01-11	Full	FAILED	2017-12-14_12-01-11	4,0K	'My Full backup'


backup_tags.txt file
--------------------
All tags are stored inside backup_tags.txt file, which will be created in backup directory:

::

    [vagrant@localhost ps_5_7_x_2_4]$ ls
    backup_tags.txt  full  inc
    [vagrant@localhost ps_5_7_x_2_4]$ cat backup_tags.txt
    $ cat backup_tags.txt
    2017-12-14_12-01-11	Full	FAILED	2017-12-14_12-01-11	4,0K	'My Full backup'

Preparing with tag
------------------

That's very nice. Now you can use those tags to prepare your backups.
Say you want to prepare only first incremental and ignore second one(or others).

::

    $ autoxtrabackup --tag="First incremental backup" -v \
    -lf /home/shahriyar.rzaev/autoxtrabackup_2_4_5_7.log \
    -l DEBUG --defaults-file=/home/shahriyar.rzaev/XB_TEST/server_dir/xb_2_4_ps_5_7.conf --prepare
    2017-11-16 20:18:16 DEBUG    <pid.PidFile object at 0x7f7bc69d2048> entering setup
    2017-11-16 20:18:16 DEBUG    <pid.PidFile object at 0x7f7bc69d2048> create pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    2017-11-16 20:18:16 DEBUG    <pid.PidFile object at 0x7f7bc69d2048> check pidfile: /tmp/MySQL-AutoXtraBackup/autoxtrabackup.pid
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    Preparing full/inc backups!
    What do you want to do?
    1. Prepare Backups and keep for future usage. NOTE('Once Prepared Backups Can not be prepared Again')
    2. Prepare Backups and restore/recover/copy-back immediately
    3. Just copy-back previously prepared backups
    Please Choose one of options and type 1 or 2 or 3: 1

    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    2017-11-16 20:18:20 DEBUG    Backup tag will be used to prepare backups
    2017-11-16 20:18:20 DEBUG    - - - - You have Incremental backups. - - - -
    2017-11-16 20:18:20 DEBUG    - - - - Preparing Full backup for incrementals - - - -
    2017-11-16 20:18:20 DEBUG    - - - - Final prepare,will occur after preparing all inc backups - - - -
    .
    .
    .
    2017-11-16 20:18:26 DEBUG    Preparing Incs:
    2017-11-16 20:18:26 DEBUG    Preparing last incremental backup, inc backup dir/name is 2017-11-16_20-12-23

As you see it will mark given incremental backup as last one, because you have specified it in --tag option.

**If you pass wrong/non-existing tag name the tool will raise RuntimeError.**


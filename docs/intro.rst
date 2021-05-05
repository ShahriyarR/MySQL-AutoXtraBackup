Intro
=====

What is this?
-------------

MySQL-AutoXtraBackup is a commandline tool written in Python3 based on
Percona XtraBackup.
It is aimed to simplify the usage of XtraBackup in
daily basis and to help backup admin in certain tasks.

Why you need this?
------------------

The idea for this tool, came from my hard times after accidentally
deleting the table data.
There was a full backup and 12 incremental backups.
It took me 20 minutes to prepare necessary commands for preparing
backups. If you have compressed + encrypted backups you need also,
decrypt and decompress, which is going to add extra time for preparing
backups. Then I decided to automate this process. In other words,
preparing necessary commands for backup and prepare stage were
automated.

If you think that those reasons are not enough - Then just believe me
you need this :)

Is it production ready?
-----------------------

Well, we have famous answer for this - "It depends!".
Basically this tool is based on Percona XtraBackup and it is using XtraBackup's
functionality.
For me, I have used it in production environment after testing for a while in test servers.
But to be clear, just test it enough to be confident.

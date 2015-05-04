Partial Table Recovery
======================

This script is using ["Transportable Taplespace"](http://dev.mysql.com/doc/refman/5.6/en/glossary.html#glos_transportable_tablespace)concept.
MySQL version must be >= 5.6 , script will check version of MySQL server.
Also innodb_file_per_table must be enabled (=1), from 5.6 it is enabled by default, again script will check it.
If MySQL server is down it will fail.

Here is script's workflow:
--------------------------

1. If specified database exists on backup directory but not in working MySQL server(say it is dropped),
it will prompt to create new one.
If you type yes, it will proceed, if no it will exit.
2. If specified table exist on backup directory but not in working MySQL server,(table is dropped for eg.) 
it will extract table create from .frm file and create it before recovery.
(Uses ['mysqlfrm'](http://dev.mysql.com/doc/mysql-utilities/1.5/en/mysqlfrm.html) tool from MySQL Utilities)


Demo Video
----------

[]()


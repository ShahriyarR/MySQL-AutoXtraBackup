#!/usr/bin/env bash

BASEDIR=$1
MYSQL_SOCK=$2
MYSQL_USER=root
#CONN_STR=${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK}


${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "CREATE TEMPORARY TABLE sysbench_test_db.t04 (a TEXT) ENGINE=InnoDB encryption='N';INSERT INTO sysbench_test_db.t04 VALUES ('Praesent tristique eros a tempus fringilla');"
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "CREATE TEMPORARY TABLE sysbench_test_db.t03 (a TEXT) ENGINE=InnoDB ROW_FORMAT=COMPRESSED encryption='N';INSERT INTO sysbench_test_db.t03 VALUES ('Praesent tristique eros a tempus fringilla');"

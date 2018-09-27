#!/usr/bin/env bash

BASEDIR=$1
MYSQL_SOCK=$2
MYSQL_USER=root
#CONN_STR=${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK}

#MC: Changed ENCRYPTION to Y as all temp tables require encryption, Issue: PS-4766
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "CREATE TEMPORARY TABLE sysbench_test_db.t04 (a TEXT) ENGINE=InnoDB ENCRYPTION='Y';INSERT INTO sysbench_test_db.t04 VALUES ('Praesent tristique eros a tempus fringilla');"
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "CREATE TEMPORARY TABLE sysbench_test_db.t03 (a TEXT) ENGINE=InnoDB ROW_FORMAT=COMPRESSED ENCRYPTION='Y';INSERT INTO sysbench_test_db.t03 VALUES ('Praesent tristique eros a tempus fringilla');"
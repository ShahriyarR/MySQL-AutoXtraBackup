#!/usr/bin/env bash

BASEDIR=$1
MYSQL_SOCK=$2
MYSQL_USER=root
#CONN_STR=${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK}


${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "CREATE INDEX t10_b ON sysbench_test_db.t10 (b)"
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "DROP INDEX t10_b ON sysbench_test_db.t10"

${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "CREATE INDEX t10_b ON sysbench_test_db.t10 (b) ALGORITHM=COPY"
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "DROP INDEX t10_b ON sysbench_test_db.t10 ALGORITHM=COPY"

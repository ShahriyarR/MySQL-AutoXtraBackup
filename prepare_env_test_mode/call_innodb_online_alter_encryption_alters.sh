#!/usr/bin/env bash

# This bash file is for creating necessary environment for running tests
# See https://jira.percona.com/browse/PS-3819

BASEDIR=$1
MYSQL_SOCK=$2
FILE_DIR=$3
MYSQL_USER=root

while true; do 
# MC: The sql exits when there is an error, hence added the --force option so that it will keep on executing
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} --force < ${FILE_DIR}/innodb_online_alter_encryption_alters.sql >> /dev/null 2>&1 

# MC: This script must exit after backup in a cycle has completed otherwise there will be multiple processes running, each cycle executes this script in a new process.
${BASEDIR}/bin/mysqladmin ping --user=${MYSQL_USER} --socket=${MYSQL_SOCK} 2>/dev/null 1>&2
if [ $? -ne 0 ]; then
exit 0
fi
done

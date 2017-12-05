#!/usr/bin/env bash
# Executed as create_sleep_queries.sh BASEDIR_PATH 50 SOCKET
BASEDIR=$1
SLEEP_COUNT=$2
MYSQL_SOCK=$3
MYSQL_USER=root

echo "Creating sleep() queries using MYSQL_SOCK=${MYSQL_SOCK}"
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "select sleep(${SLEEP_COUNT})" > /dev/null 2>&1

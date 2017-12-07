#!/usr/bin/env bash
# Executed as run_sql_queries.sh BASEDIR_PATH 50 SOCKET
BASEDIR=$1
MYSQL_SOCK=$2
SQL=$3
MYSQL_USER=root

#echo "Running queries using MYSQL_SOCK=${MYSQL_SOCK}"
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "${SQL}" > /dev/null 2>&1

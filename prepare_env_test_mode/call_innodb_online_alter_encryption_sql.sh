#!/usr/bin/env bash

# This bash file is for creating necessary environment for running tests
# See https://jira.percona.com/browse/PS-3819

BASEDIR=$1
MYSQL_SOCK=$2
FILE_DIR=$3
MYSQL_USER=root

${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} < ${FILE_DIR}/innodb_online_alter_encryption.sql
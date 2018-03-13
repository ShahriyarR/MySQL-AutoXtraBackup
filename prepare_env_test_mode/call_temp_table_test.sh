#!/usr/bin/env bash

PATH=$1
BASEDIR=$2
MYSQL_SOCK=$3

while true; do /usr/bin/bash ${PATH}/temp_table_test.sh ${BASEDIR} ${MYSQL_SOCK}; done
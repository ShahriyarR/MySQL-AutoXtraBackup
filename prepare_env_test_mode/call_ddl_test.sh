#!/usr/bin/env bash

PATH=$1
BASEDIR=$1
MYSQL_SOCK=$2

while true; do /usr/bin/bash ${PATH}/ddl_test.sh ${BASEDIR} ${MYSQL_SOCK}; done
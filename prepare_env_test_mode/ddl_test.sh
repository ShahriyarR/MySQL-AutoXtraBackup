#!/usr/bin/env bash

BASEDIR=$1
MYSQL_SOCK=$2
MYSQL_USER=root
CONN_STR=${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK}

for i in `seq 1 1000`; do
     ${CONN_STR} -e "drop table if exists sysbench_test_db.sb1"
     ${CONN_STR} -e "create table sysbench_test_db.sb1 as select id,c from sysbench_test_db.sbtest1 where id < 150000"
     ${CONN_STR} -e "create unique index ix on sysbench_test_db.sb1 (id)"
#echo "drop table if exists sysbencht_test_db.sb1"|./use
#echo "create table sb1 as select id,c from sbtest1 where id < 150000;"|./use db1
#echo "create unique index ix on sb1 (id)"|./use db1
    sleep 1
    ${CONN_STR} -e "drop table if exists sysbench_test_db.sb2"
    ${CONN_STR} -e "create table sysbench_test_db.sb2 as select id,c from sysbench_test_db.sbtest1 where id < 150000"
    ${CONN_STR} -e "create unique index ix on sysbench_test_db.sb2 (id)"
#echo "drop table if exists db2.sb1"|./use
#echo "create table sb1 as select id,c from sbtest1 where id < 150000;"|./use db2
#echo "create unique index ix on sb1 (id)"|./use db2
done
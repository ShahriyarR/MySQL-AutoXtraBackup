#!/usr/bin/env bash

BASEDIR=$1
MYSQL_SOCK=$2
MYSQL_USER=root
#CONN_STR=${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK}


${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "drop table if exists sysbench_test_db.sb1"
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "create table sysbench_test_db.sb1(id int(11) NOT NULL, c char(120) NOT NULL DEFAULT '')"
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "insert into sysbench_test_db.sb1 select id, c from sysbench_test_db.sbtest1"
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "create unique index ix on sysbench_test_db.sb1 (id)"
#echo "drop table if exists sysbencht_test_db.sb1"|./use
#echo "create table sb1 as select id,c from sbtest1 where id < 150000;"|./use db1
#echo "create unique index ix on sb1 (id)"|./use db1
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "drop table if exists sysbench_test_db.sb2"
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "create table sysbench_test_db.sb2(id int(11) NOT NULL, c char(120) NOT NULL DEFAULT '')"
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "insert into sysbench_test_db.sb2 select id, c from sysbench_test_db.sbtest1"
${BASEDIR}/bin/mysql --user=${MYSQL_USER} --socket=${MYSQL_SOCK} -e "create unique index ix on sysbench_test_db.sb2 (id)"
#echo "drop table if exists db2.sb1"|./use
#echo "create table sb1 as select id,c from sbtest1 where id < 150000;"|./use db2
#echo "create unique index ix on sb1 (id)"|./use db2
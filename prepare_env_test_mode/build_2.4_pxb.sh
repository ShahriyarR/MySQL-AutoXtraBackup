#!/bin/bash

TESTPATH=$1

rm -rf target
mkdir -p target

cmake -DCMAKE_INSTALL_PREFIX=./target -DWITH_DEBUG=1 -DWITH_SSL=system -DWITH_MAN_PAGES=OFF -DDOWNLOAD_BOOST=1 -DWITH_BOOST=/tmp/boost_23/ && make -j2
make install
mkdir ./target/percona-xtrabackup-2.4.x-debug
mv ./target/bin ./target/xtrabackup-test ./target/percona-xtrabackup-2.4.x-debug/
tar -zcf  ${TESTPATH}/percona-xtrabackup-2.4.x-debug.tar.gz ./target/percona-xtrabackup-2.4.x-debug
#!/bin/bash
# Call this inside basedir, it will create start_dynamic executable file.

# Get version specific options
BIN=
if [ -r ${PWD}/bin/mysqld-debug ]; then BIN="${PWD}/bin/mysqld-debug"; fi  # Needs to come first so it's overwritten in next line if both exist
if [ -r ${PWD}/bin/mysqld ]; then BIN="${PWD}/bin/mysqld"; fi
if [ "${BIN}" == "" ]; then echo "Assert: no mysqld or mysqld-debug binary was found!"; fi

JE1="if [ -r /usr/lib64/libjemalloc.so.1 ]; then export LD_PRELOAD=/usr/lib64/libjemalloc.so.1"
JE2=" elif [ -r /usr/lib/x86_64-linux-gnu/libjemalloc.so.1 ]; then export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.1"
JE3=" elif [ -r /usr/local/lib/libjemalloc.so ]; then export LD_PRELOAD=/usr/local/lib/libjemalloc.so"
JE4=" elif [ -r ${PWD}/lib/mysql/libjemalloc.so.1 ]; then export LD_PRELOAD=${PWD}/lib/mysql/libjemalloc.so.1"
JE5=" else echo 'Error: jemalloc not found, please install it first'; exit 1; fi"

START_OPT="--core-file"           # Compatible with 5.6,5.7,8.0

if [ -r ${PWD}/lib/mysql/plugin/ha_tokudb.so ]; then
  TOKUDB="--plugin-load-add=tokudb=ha_tokudb.so --tokudb-check-jemalloc=0"
else
  TOKUDB=""
fi
if [ -r ${PWD}/lib/mysql/plugin/ha_rocksdb.so ]; then
  ROCKSDB="--plugin-load-add=rocksdb=ha_rocksdb.so"
else
  ROCKSDB=""
fi

echo "MYEXTRA_OPT=\"\$*\"" > start_dynamic
echo 'MYEXTRA=" --no-defaults --secure-file-priv="' >> start_dynamic
echo '#MYEXTRA=" --no-defaults --sql_mode="' >> start_dynamic
echo "#MYEXTRA=\" --no-defaults --performance-schema --performance-schema-instrument='%=on'\"  # For PMM" >> start_dynamic
echo '#MYEXTRA=" --no-defaults --default-tmp-storage-engine=MyISAM --rocksdb --skip-innodb --default-storage-engine=RocksDB"' >> start_dynamic
echo '#MYEXTRA=" --no-defaults --event-scheduler=ON --maximum-bulk_insert_buffer_size=1M --maximum-join_buffer_size=1M --maximum-max_heap_table_size=1M --maximum-max_join_size=1M --maximum-myisam_max_sort_file_size=1M --maximum-myisam_mmap_size=1M --maximum-myisam_sort_buffer_size=1M --maximum-optimizer_trace_max_mem_size=1M --maximum-preload_buffer_size=1M --maximum-query_alloc_block_size=1M --maximum-query_prealloc_size=1M --maximum-range_alloc_block_size=1M --maximum-read_buffer_size=1M --maximum-read_rnd_buffer_size=1M --maximum-sort_buffer_size=1M --maximum-tmp_table_size=1M --maximum-transaction_alloc_block_size=1M --maximum-transaction_prealloc_size=1M --log-output=none --sql_mode=ONLY_FULL_GROUP_BY"' >> start_dynamic

echo $JE1 >> start_dynamic; echo $JE2 >> start_dynamic; echo $JE3 >> start_dynamic; echo $JE4 >> start_dynamic; echo $JE5 >> start_dynamic
echo "$BIN  \${MYEXTRA} \${MYEXTRA_OPT} ${START_OPT} --basedir=${PWD} ${TOKUDB} ${ROCKSDB} 2>&1 &" >> start_dynamic
echo "sleep 10" >> start_dynamic

chmod u+x start_dynamic 2>/dev/null
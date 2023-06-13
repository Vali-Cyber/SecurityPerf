#!/bin/bash
sysbench oltp_read_write.lua --threads=4 --db-driver=pgsql --pgsql-host=$REMOTE_TESTING_HOST --pgsql-port=5432 --pgsql-user=sbtest --pgsql-password=password  --pgsql-db=sbtest  --tables=20 --table-size=100000 prepare;

sysbench oltp_read_write.lua --db-driver=pgsql --pgsql-host=$REMOTE_TESTING_HOST --pgsql-port=5432 --pgsql-user=sbtest  --pgsql-password=password  --pgsql-db=sbtest --threads=16 --events=0 --time=3  --tables=20 --delete_inserts=10 --index_updates=10 --non_index_updates=10 --table-size=100000 --db-ps-mode=disable --report-interval=3 run;

#!/bin/bash
sysbench src/lua/oltp_read_write.lua --threads=4 --mysql-host=$REMOTE_TESTING_HOST --mysql-user=root --mysql-password=pass --mysql-port=3306 --tables=20 --table-size=10000 prepare;

sysbench src/lua/oltp_read_write.lua --threads=16 --events=0 --time=3 --mysql-host=$REMOTE_TESTING_HOST --mysql-user=root --mysql-password=pass --mysql-port=3306 --tables=20 --delete_inserts=10 --index_updates=10 --non_index_updates=10 --table-size=10000 --db-ps-mode=disable --report-interval=3 run;

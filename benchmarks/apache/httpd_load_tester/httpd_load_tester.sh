#!/bin/bash
# 1,000,000 requests. It is easier to read this way
NUM_REQUESTS=$((1000*1000))
NUM_CONCURRENT_REQUESTS=100
ab -n $NUM_REQUESTS -c $NUM_CONCURRENT_REQUESTS http://httpd/index.html &> /results/results.txt

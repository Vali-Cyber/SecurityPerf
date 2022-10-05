#!/bin/bash
# 200,000 requests. It is easier to read this way
NUM_REQUESTS=$((1000*200))
ab -n $NUM_REQUESTS http://httpd/index.html &> /results/results.txt

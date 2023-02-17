#!/bin/bash
# 200,000 requests. It is easier to read this way
NUM_REQUESTS=$((1000))
ab -c 100 -n $NUM_REQUESTS http://$REMOTE_TESTING_HOST/index.html

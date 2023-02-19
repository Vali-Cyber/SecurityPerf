#!/bin/bash
NUM_REQUESTS=$((100000))
ab -c 100 -n $NUM_REQUESTS http://$REMOTE_TESTING_HOST/index.html

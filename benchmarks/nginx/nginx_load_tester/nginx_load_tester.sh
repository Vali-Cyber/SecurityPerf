#!/bin/bash
NUM_REQUESTS=$((10000))
ab -c 10 -n $NUM_REQUESTS http://$REMOTE_TESTING_HOST/index.html

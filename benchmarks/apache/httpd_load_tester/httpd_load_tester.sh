#!/bin/bash
ab -n 1000000 -c 100 http://httpd/index.html &> /results/results.txt

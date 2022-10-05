#!/bin/bash
rm -rf results
mkdir results
docker-compose up --build  --abort-on-container-exit
docker-compose down

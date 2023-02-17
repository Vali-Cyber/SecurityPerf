#!/usr/bin/python3
import argparse
import json
import logging
import os
import paramiko
import scp
import statistics
import subprocess

from ..benchmark import Benchmark

logging.basicConfig(level=logging.INFO)

class MysqlBenchmark(Benchmark):

    def __init__(self, *args, **kwargs):
        super(MysqlBenchmark, self).__init__(*args, **kwargs)
        self.name = "mysql"
        self.client_image_name = "mysql_load_tester"
        self.server_image_name = "mysql"
        self.logger = logging.getLogger(self.name + "_benchmark")
        self.server_port = 3306
        self.service_initialization_delay = 10
        self.remote_env = "-e MYSQL_DATABASE=sbtest -e MYSQL_ROOT_PASSWORD=pass"

    def parse_benchmark_results(self):
        result = "Mysql Results (%s):\n" % self.protection_string
        times = []
        run_info = []
        for run_data in sorted(os.listdir("%s/results/%s/%s" % (os.getcwd(), self.protection_string, self.name)), key=lambda f: int(f.split("_")[1])):
            with open("%s/results/%s/%s/%s" % (os.getcwd(), self.protection_string, self.name, run_data)) as f:
                lines = f.readlines()
                parts = run_data.split("_")
                iteration = parts[1]
                protection_status = parts[2].split(".")[0]
                for line in lines:
                    if "transactions:" in line:
                        times.append(float(line.split()[2][1:-1]))
                        run_info.append([iteration, protection_status])
                        break
        mean =  statistics.mean(times)
        std_dev = 0
        if len(times) > 1:
            std_dev = statistics.stdev(times)
        for i, time in enumerate(times):
            result += "\tRun %s transactions per second (%s):\t%f\n" % (run_info[i][0], run_info[i][1], time)
        result += "\tMean (transactions per second): %f\n" % mean
        result += "\tStandard Deviation (transactions per second): %f\n" % std_dev
        return result

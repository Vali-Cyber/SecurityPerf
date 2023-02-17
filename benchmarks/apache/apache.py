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

class ApacheBenchmark(Benchmark):

    def __init__(self, *args, **kwargs):
        super(ApacheBenchmark, self).__init__(*args, **kwargs)
        self.name = "apache"
        self.client_image_name = "apache_load_tester"
        self.server_image_name = "apache"
        self.logger = logging.getLogger(self.name + "_benchmark")
        self.client_command = ["docker", "run", "-e", "REMOTE_TESTING_HOST=%s" % self.remote_ip,
            "--name", self.client_image_name, self.client_image_name]
        self.server_command = ["docker", "run", "--rm", "-d", "--name", self.server_image_name,
            "-p", "%d:%d" % (80, 80), self.server_image_name]

    def parse_benchmark_results(self):
        result = "Apache Results (%s):\n" % self.protection_string
        times = []
        run_info = []
        for run_data in sorted(os.listdir("%s/results/%s/%s" % (os.getcwd(), self.protection_string, self.name)), key=lambda f: int(f.split("_")[1])):
            with open("%s/results/%s/%s/%s" % (os.getcwd(), self.protection_string, self.name, run_data)) as f:
                lines = f.readlines()
                parts = run_data.split("_")
                iteration = parts[1]
                protection_status = parts[2].split(".")[0]
                for line in lines:
                    if "Requests per second" in line:
                        times.append(float(line.split()[3]))
                        run_info.append([iteration, protection_status])
                        break
        mean =  statistics.mean(times)
        std_dev = 0
        if len(times) > 1:
            std_dev = statistics.stdev(times)
        for i, time in enumerate(times):
            result += "\tRun %s requests per second (%s):\t%f\n" % (run_info[i][0], run_info[i][1], time)
        result += "\tMean (requests per second): %f\n" % mean
        result += "\tStandard Deviation (requests per second): %f\n" % std_dev
        return result

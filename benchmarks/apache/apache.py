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
        self.server_port = 80

    def run_benchmark(self, iteration):
        if not self.docker_image_exists(self.client_image_name):
            self.logger.info("Client docker image %s does not exist. Building it now." % (self.client_image_name))
            self.build_docker_image(self.client_image_name)
        if not self.docker_image_exists(self.server_image_name):
            self.logger.info("Docker image %s does not exist. Building it now." % (self.server_image_name))
            self.build_docker_image(self.server_image_name)
        self.run_remote_image(self.server_image_name, self.server_port)

        self.run_benchmark_image(self.client_image_name, self.remote_ip)
        output = subprocess.check_output(["docker", "logs", self.client_image_name], stderr=subprocess.DEVNULL).decode("utf-8")


        os.makedirs("%s/results/%s" % (os.getcwd(), self.name), exist_ok=True)
        filename = "%s_%i_%s.txt" % (self.name, iteration+1, self.protection_string)
        with open("%s/results/apache/%s" % (os.getcwd(), filename), "w") as f:
            f.write(output)

    def parse_benchmark_results(self):
        result = "Apache Results (%s):\n" % self.protection_string
        times = []
        run_info = []
        for run_data in sorted(os.listdir("%s/results/%s" % (os.getcwd(), self.name)), key=lambda f: int(f.split("_")[1])):
            with open("%s/results/%s/%s" % (os.getcwd(), self.name, run_data)) as f:
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
        std_dev = statistics.stdev(times)
        for i, time in enumerate(times):
            result += "\tRun %s requests per second (%s):\t%f\n" % (run_info[i][0], run_info[i][1], time)
        result += "\tMean (requests per second): %f\n" % mean
        result += "\tStandard Deviation (requests per second): %f\n" % std_dev
        return result

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
        self.results_header = "Apache Results (%s):\n" % self.protection_string
        self.target_token = "Requests per second"
        self.line_parser = lambda line: float(line.split()[3])
        self.metric_units = "requests per second"

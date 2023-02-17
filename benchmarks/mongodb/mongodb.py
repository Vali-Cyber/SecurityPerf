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

class MongodbBenchmark(Benchmark):

    def __init__(self, *args, **kwargs):
        super(MongodbBenchmark, self).__init__(*args, **kwargs)
        self.name = "mongodb"
        self.client_image_name = "mongodb_load_tester"
        self.server_image_name = "mongodb"
        self.logger = logging.getLogger(self.name + "_benchmark")
        self.service_initialization_delay = 5
        self.client_command = ["docker", "run", "--name",
                self.client_image_name, self.client_image_name]
        self.server_command = ["docker", "run", "-d", "-e",
                "MONGO_INITDB_ROOT_USERNAME=root", "-e",
                "MONGO_INITDB_ROOT_PASSWORD=pass", "--network=host", "--rm",
                "--name", self.server_image_name, self.server_image_name]
        self.results_header = "Mongodb Results (%s):\n" % self.protection_string
        self.target_token = "Throughput(ops/sec)"
        self.line_parser = lambda line: float(line.split()[2])
        self.metric_units = "operations/sec"

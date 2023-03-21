#!/usr/bin/python3
"""Mongodb benchmark class"""
import logging

from ..benchmark import Benchmark # pylint: disable=relative-beyond-top-level

logging.basicConfig(level=logging.INFO)

class MongodbBenchmark(Benchmark): # pylint: disable=too-many-instance-attributes disable=too-few-public-methods
    """Mongodb benchmark class"""
    def __init__(self, *args, **kwargs):
        super(MongodbBenchmark, self).__init__(*args, **kwargs)
        self.name = "mongodb"
        self.client_image_name = "mongodb_load_tester"
        self.server_image_name = "mongodb"
        self.logger = logging.getLogger(self.name + "_benchmark")
        self.service_initialization_delay = 15
        self.client_command = ["docker", "run", "-e", "REMOTE_TESTING_HOST=%s" %
                               self.remote_ip, "--name", self.client_image_name,
                               self.client_image_name]
        self.server_command = ["docker", "run", "-d", "-e",
                               "MONGO_INITDB_ROOT_USERNAME=root", "-e",
                               "MONGO_INITDB_ROOT_PASSWORD=pass", "--network=host", "--rm",
                               "--name", self.server_image_name, self.server_image_name]
        self.results_header = "Mongodb Results (%s):\n" % self.protection_string
        self.target_token = "Throughput(ops/sec)"
        self.line_parser = lambda line: float(line.split()[2])
        self.metric_units = "operations/sec"

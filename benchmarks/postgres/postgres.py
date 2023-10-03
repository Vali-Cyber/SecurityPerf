#!/usr/bin/python3
"""Postgres benchmark class"""
import logging

from ..benchmark import Benchmark # pylint: disable=relative-beyond-top-level

logging.basicConfig(level=logging.INFO)

class PostgresBenchmark(Benchmark): # pylint: disable=too-many-instance-attributes disable=too-few-public-methods
    """Postgres benchmark class"""

    def __init__(self, *args, **kwargs):
        super(PostgresBenchmark, self).__init__(*args, **kwargs)
        self.name = "postgres"
        self.client_image_name = "postgres_load_tester"
        self.server_image_name = "postgres"
        self.logger = logging.getLogger(self.name + "_benchmark")
        self.service_initialization_delay = 10
        self.client_command = ["docker", "run", "-e", "REMOTE_TESTING_HOST=%s" % self.remote_ip,
                               "--name", self.client_image_name, self.client_image_name]
        self.server_command = ["docker", "run", "-d", "-e", "POSTGRES_PASSWORD=password", "-e",
                               "POSTGRES_USER=sbtest", "--rm", "--name", self.server_image_name,
                               "-p", "%d:%d" % (5432, 5432), self.server_image_name]
        self.results_header = "Postgres Results (%s):\n" % self.protection_string
        self.target_token = "transactions:"
        self.line_parser = lambda line: float(line.split()[2][1::])
        self.metric_units = "transactions per second"

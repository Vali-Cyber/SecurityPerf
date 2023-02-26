#!/usr/bin/python3
"""Mysql benchmark class"""
import logging

from ..benchmark import Benchmark # pylint: disable=relative-beyond-top-level

logging.basicConfig(level=logging.INFO)

class MysqlBenchmark(Benchmark): # pylint: disable=too-many-instance-attributes disable=too-few-public-methods
    """Mysql benchmark class"""

    def __init__(self, *args, **kwargs):
        super(MysqlBenchmark, self).__init__(*args, **kwargs)
        self.name = "mysql"
        self.client_image_name = "mysql_load_tester"
        self.server_image_name = "mysql"
        self.logger = logging.getLogger(self.name + "_benchmark")
        self.service_initialization_delay = 35
        self.client_command = ["docker", "run", "-e", "REMOTE_TESTING_HOST=%s" % self.remote_ip,
                               "--name", self.client_image_name, self.client_image_name]
        self.server_command = ["docker", "run", "-d", "-e", " MYSQL_DATABASE=sbtest", "-e",
                               "MYSQL_ROOT_PASSWORD=pass", "--rm", "--name", self.server_image_name,
                               "-p", "%d:%d" % (3306, 3306), self.server_image_name]
        self.results_header = "Mysql Results (%s):\n" % self.protection_string
        self.target_token = "transactions:"
        self.line_parser = lambda line: float(line.split()[2][1::])
        self.metric_units = "transactions per second"

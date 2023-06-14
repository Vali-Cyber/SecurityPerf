#!/usr/bin/python3
"""Nginx benchmark class"""
import logging

from ..benchmark import Benchmark # pylint: disable=relative-beyond-top-level

logging.basicConfig(level=logging.INFO)

class NginxBenchmark(Benchmark): # pylint: disable=too-many-instance-attributes disable=too-few-public-methods
    """Nginx benchmark class"""

    def __init__(self, *args, **kwargs):
        super(NginxBenchmark, self).__init__(*args, **kwargs)
        self.name = "nginx"
        self.client_image_name = "nginx_load_tester"
        self.server_image_name = "nginx"
        self.service_initialization_delay = 15
        self.logger = logging.getLogger(self.name + "_benchmark")
        self.client_command = ["docker", "run", "-e", "REMOTE_TESTING_HOST=%s" % self.remote_ip,
                               "--name", self.client_image_name, self.client_image_name]
        self.server_command = ["docker", "run", "--rm", "-d", "--name", self.server_image_name,
                               "-p", "%d:%d" % (80, 80), self.server_image_name]
        self.results_header = "Nginx Results (%s):\n" % self.protection_string
        self.target_token = "Requests per second"
        self.line_parser = lambda line: float(line.split()[3])
        self.metric_units = "requests per second"

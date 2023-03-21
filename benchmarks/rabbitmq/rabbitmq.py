#!/usr/bin/python3
"""Rabbitmq benchmark class"""
import logging

from ..benchmark import Benchmark # pylint: disable=relative-beyond-top-level

logging.basicConfig(level=logging.INFO)

class RabbitmqBenchmark(Benchmark): # pylint: disable=too-many-instance-attributes disable=too-few-public-methods
    """Rabbitmq benchmark class"""

    def __init__(self, *args, **kwargs):
        super(RabbitmqBenchmark, self).__init__(*args, **kwargs)
        self.name = "rabbitmq"
        self.client_image_name = "rabbitmq_load_tester"
        self.server_image_name = "rabbitmq"
        self.logger = logging.getLogger(self.name + "_benchmark")
        self.service_initialization_delay = 30
        self.client_command = ["docker", "run", "--network=host", "--name",
                               self.client_image_name, self.client_image_name,
                               "--uri", "amqp://%s" % self.remote_ip, "-z", "30"]
        self.server_command = ["docker", "run", "-d", "--rm", "--name",
                               self.server_image_name, "--network=host", self.server_image_name]
        self.results_header = "Rabbitmq Results (%s):\n" % self.protection_string
        self.target_token = "sending rate avg:"
        self.line_parser = lambda line: float(line.split()[5])
        self.metric_units = "msg/s"

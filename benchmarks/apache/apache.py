#!/usr/bin/python3
"""Apache benchmark class"""
import logging

from ..benchmark import Benchmark # pylint: disable=relative-beyond-top-level

logging.basicConfig(level=logging.INFO)

class ApacheBenchmark(Benchmark): # pylint: disable=too-many-instance-attributes disable=too-few-public-methods
    """Apache benchmark class"""

    def __init__(self, *args, **kwargs):
        super(ApacheBenchmark, self).__init__(*args, **kwargs)
        self.name = "apache" # The name of the benchmark
        self.client_image_name = "apache_load_tester" # The name for the client docker image. Make sure the string matches the name of the subdirectory which contain's the image's corresponding Dockerfile.
        self.server_image_name = "apache" # The name for the server docker image. Make sure the string matches the name of the subdirectory which contain's the image's corresponding Dockerfile.
        self.service_initialization_delay = 15 # How long the benchmark image should wait to test the server image
        self.logger = logging.getLogger(self.name + "_benchmark") # The logger for the benchmark
        self.client_command = ["docker", "run", "-e", "REMOTE_TESTING_HOST=%s" % self.remote_ip,
                               "--name", self.client_image_name, self.client_image_name] # The command used to run the benchmark image
        self.server_command = ["docker", "run", "--rm", "-d", "--name", self.server_image_name,
                               "-p", "%d:%d" % (80, 80), self.server_image_name] # The command used to run the server image
        self.results_header = "Apache Results (%s):\n" % self.protection_string # The header text that should be presented in the summary_results.txt file after all tests have run
        self.target_token = "Requests per second" # The token in the benchmarking results for the line that contains the value we wish to capture and include in the summary_results.txt file
        self.line_parser = lambda line: float(line.split()[3]) # A function that parses the line that contains the target_token and extracts the desired value
        self.metric_units = "requests per second" # The units for the metric captured from the benchmark's results

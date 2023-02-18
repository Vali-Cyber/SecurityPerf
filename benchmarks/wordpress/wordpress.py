#!/usr/bin/python3
"""Wordpress benchmark class"""
import logging
import os
from time import sleep

from ..benchmark import Benchmark # pylint: disable=relative-beyond-top-level

logging.basicConfig(level=logging.INFO)

class WordpressBenchmark(Benchmark): # pylint: disable=too-many-instance-attributes
    """Wordpress benchmark class"""

    def __init__(self, *args, **kwargs):
        super(WordpressBenchmark, self).__init__(*args, **kwargs)
        self.name = "wordpress"
        self.client_image_name = "wordpress_load_tester"
        self.server_image_name = "wordpress"
        self.logger = logging.getLogger(self.name + "_benchmark")
        self.client_command = ["docker", "run", "-e", "REMOTE_TESTING_HOST=%s" % self.remote_ip,
                               "--name", self.client_image_name, self.client_image_name]
        self.server_command = ["docker", "run", "--rm", "-d", "--name", self.server_image_name,
                               "-p", "%d:%d" % (80, 80), self.server_image_name]
        self.results_header = "Apache Results (%s):\n" % self.protection_string
        self.target_token = "Requests per second"
        self.line_parser = lambda line: float(line.split()[3])
        self.metric_units = "requests per second"


    def build_server_image(self):
        """Don't build the sever image. Use the stack.yaml file instead"""

    def run_remote_image(self):
        """Run remote container images with docker swarm"""
        self.run_remote_command("docker stack rm wordpress")
        self.run_remote_command("docker swarm init")
        self.copy_file_to_remote("%s/benchmarks/wordpress/wordpress/wordpress_stack.yml"
                                 % os.getcwd())
        self.run_remote_command("docker stack deploy -c ~/wordpress_stack.yml wordpress",
                                True)
        self.logger.info("Sleeping for %d seconds while services start", 10)
        sleep(10)

    def stop_remote_image(self):
        """Stop and remove remote container images with docker swarm"""
        self.run_remote_command("rm ~/wordpress_stack.yml")
        self.run_remote_command("docker stack rm wordpress")
        self.run_remote_command("docker swarm leave --force")
        self.logger.info("Sleeping for %d seconds while services shutdown", 5)
        sleep(5)
        self.run_remote_command("docker volume rm wordpress_db wordpress_wordpress")
        sleep(1)

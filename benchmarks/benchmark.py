#!/usr/bin/python3
import argparse
import json
import logging
import os
import paramiko
import scp
import statistics
import subprocess
from time import sleep

class Benchmark:
    def __init__(self, ssh_client, remote_ip, protection_string):
        self.client = ssh_client
        self.remote_ip = remote_ip
        self.protection_string = protection_string
        self.service_initialization_delay = 0
        self.remote_env = ""
        self.times = []

    def run_remote_command(self, command, raise_exception=False, exception_message=""):
        stdin,stdout,stderr=self.client.exec_command(command)
        exit_status = stderr.channel.recv_exit_status()
        if exit_status:
            self.logger.error("Remote command %s failed", command)
            if raise_exception:
                raise Exception("Remote command %s failed with error '%s'", (command, stderr.read()))
        else:
            self.logger.info("Remote command %s succeeded", command)
        return stdout.read()

    def docker_image_exists(self, image_name):
        result = str(subprocess.check_output(["docker", "image", "ls", image_name]))
        if image_name not in result:
            return False
        return True

    def build_docker_image(self, image_name):
        old_cwd = os.getcwd()
        os.chdir("./benchmarks/%s/%s" % (self.name, image_name))
        try:
            subprocess.check_output(["docker", "build", ".", "-f", "%s.Dockerfile" % image_name, "-t", image_name], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            self.logger.fatal("Failed to build container image '%s' with error: %s" % (image_name, e.output.decode("utf-8")))
            exit(1)
        os.chdir(old_cwd)

    def copy_image_to_remote(self, image_name):
        filename = "%s.tar" % image_name
        self.logger.info("Copying docker image %s to the remote system" % image_name)
        subprocess.check_output(["docker", "image", "save", image_name, "-o", filename])
        scp_client = scp.SCPClient(self.client.get_transport())
        scp_client.put(filename)
        self.logger.info("Loading docker image %s on remote system" % image_name)
        self.run_remote_command("docker load -i ~/%s" % filename)
        self.run_remote_command("rm ~/%s" % filename)
        os.remove("%s/%s" % (os.getcwd(), filename))

    def run_remote_image(self):
        self.logger.info("Running remote docker image %s" % self.server_image_name)
        remote_images = self.run_remote_command("docker image ls")
        if self.server_image_name not in str(remote_images):
            self.logger.info("Remote docker image %s does not exist on remote system." % self.server_image_name)
            self.copy_image_to_remote(self.server_image_name)
        else:
            self.logger.info("Remote docker image %s exists on remote system." % self.server_image_name)

        self.run_remote_command("docker kill %s" % (self.server_image_name))
        self.run_remote_command(" ".join(self.server_command), True)
        if self.service_initialization_delay:
            self.logger.info("Sleeping for %s seconds so remote service is ready for benchmarking" %
                    self.service_initialization_delay)
            sleep(self.service_initialization_delay)

    def run_client_image(self):
        old_cwd = os.getcwd()
        os.chdir("./benchmarks/%s/%s" % (self.name, self.client_image_name))
        self.logger.info("Running benchmark image %s", self.client_image_name)
        subprocess.run(["docker", "rm", self.client_image_name], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        subprocess.check_output(self.client_command)
        os.chdir(old_cwd)

    def run_benchmark(self, iteration):
        if not self.docker_image_exists(self.client_image_name):
            self.logger.info("Client docker image %s does not exist. Building it now." % (self.client_image_name))
            self.build_docker_image(self.client_image_name)
        if not self.docker_image_exists(self.server_image_name):
            self.logger.info("Docker image %s does not exist. Building it now." % (self.server_image_name))
            self.build_docker_image(self.server_image_name)
        self.run_remote_image()

        self.run_client_image()
        output = subprocess.check_output(["docker", "logs", self.client_image_name], stderr=subprocess.DEVNULL).decode("utf-8")

        os.makedirs("%s/results/%s/%s" % (os.getcwd(), self.protection_string, self.name), exist_ok=True)
        filename = "%s_%i_%s.txt" % (self.name, iteration+1, self.protection_string)
        with open("%s/results/%s/%s/%s" % (os.getcwd(), self.protection_string, self.name, filename), "w") as f:
            f.write(output)

        self.run_remote_command("docker kill %s" % (self.server_image_name))
        subprocess.run(["docker", "kill", self.client_image_name], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        subprocess.run(["docker", "rm", self.client_image_name], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

#!/usr/bin/python3
"""Benchmark class that governs behavior of benchmarks"""
import os
import statistics
import subprocess
import sys

from time import sleep

import scp

class Benchmark: # pylint: disable=too-many-instance-attributes
    """Benchmark class that governs behavior of benchmarks"""
    def __init__(self, ssh_client, remote_ip, protection_string):
        self.client = ssh_client
        self.remote_ip = remote_ip
        self.protection_string = protection_string
        self.service_initialization_delay = 0
        self.remote_env = ""
        self.times = []
        self.logger = None
        self.name = None
        self.client_image_name = None
        self.server_image_name = None
        self.client_command = None
        self.server_command = None
        self.results_header = None
        self.target_token = None
        self.line_parser = lambda line: line
        self.metric_units = None

    def run_remote_command(self, command, raise_exception=False):
        """Run command on remote system with SSH"""
        _, stdout, stderr = self.client.exec_command(command)
        exit_status = stderr.channel.recv_exit_status()
        if exit_status:
            self.logger.error("Remote command %s failed", command)
            if raise_exception:
                raise Exception("Remote command %s failed with error '%s'" %
                                (command, stderr.read()))
        else:
            self.logger.info("Remote command %s succeeded", command)
        return stdout.read()

    def docker_image_exists(self, image_name): # pylint: disable=no-self-use
        """Check if docker image exists on local system"""
        result = str(subprocess.check_output(["docker", "image", "ls", image_name]))
        if image_name not in result:
            return False
        return True

    def build_docker_image(self, image_name):
        """Build a docker image on the local system"""
        old_cwd = os.getcwd()
        os.chdir("./benchmarks/%s/%s" % (self.name, image_name))
        try:
            subprocess.check_output(["docker", "build", ".", "-f", "%s.Dockerfile" %
                                     image_name, "-t", image_name], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exception:
            self.logger.fatal("Failed to build container image '%s' with error: %s" %
                              (image_name, exception.output.decode("utf-8")))
            sys.exit(1)
        os.chdir(old_cwd)

    def copy_file_to_remote(self, filename):
        """Copy a file from the local system to the remote system"""
        scp_client = scp.SCPClient(self.client.get_transport())
        scp_client.put(filename)

    def copy_image_to_remote(self, image_name):
        """Copy a docker image from the local system to the remote system"""
        filename = "%s.tar" % image_name
        self.logger.info("Copying docker image %s to the remote system" % filename)
        subprocess.check_output(["docker", "image", "save", image_name, "-o", filename])
        scp_client = scp.SCPClient(self.client.get_transport())
        scp_client.put(filename)
        self.logger.info("Loading docker image %s on remote system" % image_name)
        self.run_remote_command("docker load -i ~/%s" % filename)
        self.run_remote_command("rm ~/%s" % filename)
        os.remove("%s/%s" % (os.getcwd(), filename))

    def run_remote_image(self):
        """Run a docker image on the remote system"""
        self.logger.info("Running remote docker image %s" % self.server_image_name)
        remote_images = self.run_remote_command("docker image ls")
        if self.server_image_name not in str(remote_images):
            self.logger.info("Remote docker image %s does not exist on remote system."
                             % self.server_image_name)
            self.copy_image_to_remote(self.server_image_name)
        else:
            self.logger.info("Remote docker image %s exists on remote system."
                             % self.server_image_name)

        self.run_remote_command("docker kill %s" % (self.server_image_name))
        self.run_remote_command(" ".join(self.server_command), True)
        if self.service_initialization_delay:
            self.logger.info("Sleeping for %s seconds so remote service is ready for benchmarking" %
                             self.service_initialization_delay)
            sleep(self.service_initialization_delay)

    def run_client_image(self):
        """Run docker image on the local system"""
        old_cwd = os.getcwd()
        os.chdir("./benchmarks/%s/%s" % (self.name, self.client_image_name))
        self.logger.info("Running benchmark image %s", self.client_image_name)
        subprocess.run(["docker", "rm", self.client_image_name], stderr=subprocess.DEVNULL, # pylint: disable=subprocess-run-check
                       stdout=subprocess.DEVNULL)
        subprocess.check_output(self.client_command)
        os.chdir(old_cwd)

    def build_client_image(self):
        """Build an image on the local system"""
        if not self.docker_image_exists(self.client_image_name):
            self.logger.info("Client docker image %s does not exist. Building it now."
                             % (self.client_image_name))
            self.build_docker_image(self.client_image_name)

    def build_server_image(self):
        """Build an image on the server system"""
        if not self.docker_image_exists(self.server_image_name):
            self.logger.info("Docker image %s does not exist. Building it now."
                             % (self.server_image_name))
            self.build_docker_image(self.server_image_name)

    def stop_remote_image(self):
        """Stop the remote image from running"""
        self.run_remote_command("docker kill %s" % (self.server_image_name))

    def run_benchmark(self, iteration):
        """Run a full benchmark"""
        self.build_client_image()
        self.build_server_image()
        self.run_remote_image()

        self.run_client_image()
        output = subprocess.check_output(["docker", "logs", self.client_image_name],
                                         stderr=subprocess.DEVNULL).decode("utf-8")

        os.makedirs("%s/results/%s/%s" % (os.getcwd(), self.protection_string, self.name),
                    exist_ok=True)
        filename = "%s_%i_%s.txt" % (self.name, iteration+1, self.protection_string)
        with open("%s/results/%s/%s/%s"
                  % (os.getcwd(), self.protection_string, self.name, filename), "w") as results:
            results.write(output)

        self.stop_remote_image()
        subprocess.run(["docker", "kill", self.client_image_name], # pylint: disable=subprocess-run-check
                       stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        subprocess.run(["docker", "rm", self.client_image_name], # pylint: disable=subprocess-run-check
                       stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    def parse_benchmark_results(self):
        """Parse the result of a series of benchmark tests"""
        result = self.results_header
        times = []
        run_info = []
        for run_data in sorted(os.listdir("%s/results/%s/%s"
                                          % (os.getcwd(), self.protection_string, self.name)),
                               key=lambda f: int(f.split("_")[1])):
            with open("%s/results/%s/%s/%s"
                      % (os.getcwd(), self.protection_string, self.name, run_data)) as results:
                lines = results.readlines()
                parts = run_data.split("_")
                iteration = parts[1]
                protection_status = parts[2].split(".")[0]
                for line in lines:
                    if self.target_token in line:
                        times.append(self.line_parser(line))
                        run_info.append([iteration, protection_status])
                        break
        mean = statistics.mean(times)
        std_dev = 0
        if len(times) > 1:
            std_dev = statistics.stdev(times)
        for i, time in enumerate(times):
            result += "\tRun %s %s:\t%f\n" % (run_info[i][0], self.metric_units, time)
        result += "\tMean %s: %f\n" % (self.metric_units, mean)
        result += "\tStandard Deviation %s: %f\n" % (self.metric_units, std_dev)
        return result

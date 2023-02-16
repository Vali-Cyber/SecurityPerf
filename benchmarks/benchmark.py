#!/usr/bin/python3
import argparse
import json
import logging
import os
import paramiko
import scp
import statistics
import subprocess

class Benchmark:
    def __init__(self, ssh_client, remote_ip, protection_string):
        self.client = ssh_client
        self.remote_ip = remote_ip
        self.protection_string = protection_string

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

    def run_remote_image(self, image_name, port):
        self.logger.info("Running remote docker image %s" % image_name)
        remote_images = self.run_remote_command("docker image ls")
        if image_name not in str(remote_images):
            self.logger.info("Remote docker image %s does not exist on remote system." % image_name)
            self.copy_image_to_remote(image_name)
        else:
            self.logger.info("Remote docker image %s exists on remote system." % image_name)

        self.run_remote_command("docker kill %s" % (image_name))
        self.run_remote_command("docker run --rm --name %s -d -p %d:%d %s" % (image_name, port, port, image_name), True)

    def run_benchmark_image(self, image_name, ip):
        old_cwd = os.getcwd()
        os.chdir("./benchmarks/%s/%s" % (self.name, image_name))
        self.logger.info("Running benchmark image %s", image_name)
        subprocess.run(["docker", "rm", image_name], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        subprocess.check_output(["docker", "run", "-e", "REMOTE_TESTING_HOST=%s" % ip, "--name", image_name, image_name])
        os.chdir(old_cwd)


    def clean_results(self):
        path = "%s/results/%s" % (os.getcwd(), self.name)
        if os.path.exists(path):
            for f in os.listdir(path):
                if self.protection_string in f:
                    os.remove(path + "/" + f)


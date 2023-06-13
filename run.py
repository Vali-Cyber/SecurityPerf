#!/usr/bin/python3
"""Program to run various benchmarks for popular Linux software"""
import argparse
from datetime import datetime
import logging
import os
import subprocess
import sys

import coloredlogs
import paramiko

from benchmarks.apache.apache import ApacheBenchmark
from benchmarks.mysql.mysql import MysqlBenchmark
from benchmarks.rabbitmq.rabbitmq import RabbitmqBenchmark
from benchmarks.mongodb.mongodb import MongodbBenchmark
from benchmarks.wordpress.wordpress import WordpressBenchmark
from benchmarks.postgres.postgres import PostgresBenchmark


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

logging.basicConfig(level=logging.INFO)
coloredlogs.install()
logger = logging.getLogger('SecurityPerf')



def check_positive(value):
    """Checks if value is positive"""
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError("Iterations must be a positive non-zero value")
    return value

parser = argparse.ArgumentParser()

all_benchmarks = list(
        filter(lambda f: os.path.isdir("%s/benchmarks/%s" % (os.getcwd(), f))
               and f != "__pycache__",
               os.listdir("%s/benchmarks" % os.getcwd())))

parser.add_argument('-b', '--benchmarks', required=False,
                    choices=all_benchmarks,
                    nargs='+', default=all_benchmarks,
                    help="""Specify specific benchmarks you want to run """
                    """as a comma separted list. If you want to run all benchmarks, """
                    """don't use this option For example, to run the apache and mysql """
                    """benchmarks, simple run "run.py -b apache -b mysql""")

parser.add_argument('-i', '--iterations', default=5, type=check_positive, required=False,
                    help="""The number of times to run each benchmark. The default is 5.""")

parser.add_argument('-ip', '--ip', required=True,
                    help="""The IPv4 address for the remote system that will run services being """
                    """benchmarked.""")

parser.add_argument('-p', '--password', required=True,
                    help="""The password that should be used to log in to the remote system.""")

parser.add_argument('-u', '--user', required=True,
                    help="""The user that should be used to log in to the remote system.""")

parser.add_argument('-t', '--tag', type=str, default="baseline",
                    help="""The name of the subdirectory used to store results.""")

def run_remote_command(command, raise_exception=False):
    """Run command on remote system with SSH"""
    _, stdout, stderr = client.exec_command(command)
    exit_status = stderr.channel.recv_exit_status()
    if exit_status:
        logger.fatal("Remote command %s failed", command)
        if raise_exception:
            raise Exception("Remote command %s failed with error '%s'" % (command, stderr.read()))
    else:
        logger.info("Remote command %s succeeded", command)
    return stdout.read()

def validate_ssh_host_connection(host, user, password):
    """Check whether supplied credentials allow an SSH connection to be established"""
    try:
        client.connect(host, username=user, password=password, timeout=3)
        logger.info("Successful SSH connection to host %s", host)
    except: # pylint: disable=broad-except disable=bare-except
        logger.fatal("Failed SSH connection to host %s", host)
        sys.exit(1)

def validate_docker_install():
    """Check whether docker installation iis valid"""
    try:
        subprocess.call(["docker", "ps"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("Docker engine is present on the client system.")
    except: # pylint: disable=broad-except disable=bare-except
        logger.fatal("""Docker engine is not present on the client system. """
                     """Please install docker on the remote system.""")
        sys.exit(1)
    try:
        run_remote_command("docker ps", True)
        logger.info("Docker engine is present on the remote system.")
    except: # pylint: disable=broad-except disable=bare-except
        logger.fatal("""Docker engine is not present on the remote system. """
                     """Please install docker on the remote system.""")
        sys.exit(1)

def validate_run_location():
    """Check that his script is run from the top level directory of the
    security perf repo"""
    if not os.path.exists("%s/benchmarks" % os.getcwd()):
        logger.fatal("""This script must be run from the top level directory """
                     """of the securityperf repository.""")
        sys.exit(1)

def run_benchmarks(args):
    """Run each selected benchmark"""
    results = ""
    protection_string = args.tag + "_" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    benchmarks = {"apache": ApacheBenchmark(client, args.ip, protection_string),
                  "mysql": MysqlBenchmark(client, args.ip, protection_string),
                  "rabbitmq": RabbitmqBenchmark(client, args.ip, protection_string),
                  "mongodb": MongodbBenchmark(client, args.ip, protection_string),
                  "wordpress": WordpressBenchmark(client, args.ip, protection_string),
                  "postgres": PostgresBenchmark(client, args.ip, protection_string)}

    for benchmark in args.benchmarks:
        benchmark_runner = benchmarks[benchmark]
        for i in range(args.iterations):
            logger.info("%s: Executing iteration %d/%d", benchmark, i+1, args.iterations)
            benchmark_runner.run_benchmark(i)
        results += benchmark_runner.parse_benchmark_results()

    with open('results/%s/summary_results.txt' % protection_string, 'w') as summary:
        summary.write(results)

def main():
    """Main function"""
    args = parser.parse_args()
    validate_run_location()
    validate_ssh_host_connection(args.ip, args.user, args.password)
    validate_docker_install()
    run_benchmarks(args)

if __name__ == '__main__':
    main()

#!/usr/bin/python3
"""Program to download MITRE EVAL jsons"""
import argparse
import json
import logging
import os
import paramiko
import scp
import statistics
import subprocess
from benchmarks.benchmark import Benchmark
from benchmarks.apache.apache import ApacheBenchmark
from benchmarks.mysql.mysql import MysqlBenchmark
from benchmarks.rabbitmq.rabbitmq import RabbitmqBenchmark

logging.basicConfig(level=logging.INFO)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
logger = logging.getLogger('SecurityPerf')

def check_positive(value):
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError("Iterations must be a positive non-zero value")
    return value

def is_valid_path(value):
    value = str(value)
    if not os.path.exists(value):
        raise argparse.ArgumentTypeError("SSH key path must be a valid path")
    return value

parser = argparse.ArgumentParser()

all_benchmarks = list(filter(lambda f: os.path.isdir("%s/benchmarks/%s" % (os.getcwd(), f)) and f != "__pycache__",
        os.listdir("%s/benchmarks" % os.getcwd())))

parser.add_argument('-b', '--benchmarks', required=False,
        choices=all_benchmarks,
        nargs='+', default=all_benchmarks,
    help="""Specify specific benchmarks you want to run """
    """as a comma separted list. If you want to run all benchmarks, don't use this option"""
    """For example, to run the apache and mysql benchmarks, simple run "run.py -b apache -b mysql""")

parser.add_argument('-i', '--iterations', type=check_positive, required=False,
        help="""The number of times to run each benchmark. The default is 5.""")

parser.add_argument('-ip', '--ip', required=True,
        help="""The IPv4 address for the remote system that will run services being benchmarked.""")

parser.add_argument('-p', '--password', required=True,
        help="""The password that should be used to log in to the remote system.""")

parser.add_argument('-u', '--user', required=True,
        help="""The user that should be used to log in to the remote system.""")

parser.add_argument('-se', '--security-enabled', action="store_true",
        help="""Whether the system under test has securty enabled.""")

def run_remote_command(command, raise_exception=False, exception_message=""):
    stdin,stdout,stderr=client.exec_command(command)
    exit_status = stderr.channel.recv_exit_status()
    if exit_status:
        logger.fatal("Remote command %s failed", command)
        if raise_exception:
            raise Exception("Remote command %s failed with error '%s'", (command, stderr.read()))
    else:
        logger.info("Remote command %s succeeded", command)
    return stdout.read()

def validate_ssh_host_connection(host, user, password):
    try:
        client.connect(host, username=user, password=password, timeout=3)
        logger.info("Successful SSH connection to host %s" % host)
    except:
        logger.fatal("Failed SSH connection to host %s" % host)
        exit(1)

def validate_docker_install():
    try:
        subprocess.call(["docker", "ps"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("Docker engine is present on the client system.")
    except:
        logger.fatal("Docker engine is not present on the client system. Please install docker on the remote system.")
        exit(1)
    try:
        run_remote_command("docker ps", True)
        logger.info("Docker engine is present on the remote system.")
    except:
        logger.fatal("Docker engine is not present on the remote system. Please install docker on the remote system.")
        exit(1)

def validate_run_location():
    if not os.path.exists("%s/benchmarks" % os.getcwd()):
        logger.fatal("This script must be run from the top level directory of the securityperf repository.")
        exit(1)

def clean_existing_results(protection_string):
    path = "%s/results/%s" % (os.getcwd(), protection_string)
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

def run_benchmarks(args):
    results = ""
    protection_string = "unprotected"
    if args.security_enabled:
        protection_string = "protected"
    benchmarks = {"apache": ApacheBenchmark(client, args.ip, protection_string),
            "mysql": MysqlBenchmark(client, args.ip, protection_string),
            "rabbitmq": RabbitmqBenchmark(client, args.ip, protection_string)}

    clean_existing_results(protection_string)

    for benchmark in args.benchmarks:
        benchmark_runner = benchmarks[benchmark]
        for i in range(args.iterations):
            benchmark_runner.run_benchmark(i)
        results += benchmark_runner.parse_benchmark_results()

    with open('results/%s/summary_results.txt' % protection_string, 'w') as f:
        f.write(results)

def main():
    """Main function"""
    args = parser.parse_args()
    if not args.iterations:
        args.iterations = 5
    validate_run_location()
    validate_ssh_host_connection(args.ip, args.user, args.password)
    validate_docker_install()
    run_benchmarks(args)

if __name__ == '__main__':
    main()

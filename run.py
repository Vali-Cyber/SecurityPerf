#!/usr/bin/python3
"""Program to download MITRE EVAL jsons"""
import argparse
import csv
import json
import logging
import os
import paramiko

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

parser.add_argument('-b', '--benchmarks', required=False, choices=["apache", "mysql"],
    help="""Specify specific benchmarks you want to run """
    """as a comma separted list. If you want to run all benchmarks, don't use this option"""
    """For example, to run the apache and mysql benchmarks, simple run "run.py -b apache -b mysql""")

parser.add_argument('-i', '--iterations', type=check_positive, required=False,
        help="""The number of times to run each benchmark. The default is 5.""")

parser.add_argument('-c', '--config', type=is_valid_path,
        help="""The file path of the SSH config used to run benchmarks on a remote machine.""")

parser.add_argument('-r', '--remote', required=True,
        help="""The remote system that will run services being benchmarked. This should be a host in the SSH provided SSH config.""")

parser.add_argument('-p', '--password',
        help="""The password that should be used to log in to the remote system.""")

parser.add_argument('-u', '--user',
        help="""The user that should be used to log in to the remote system.""")

def validate_ssh_host(host, config_path, user, password):
    if (config_path):
        client.load_host_keys(config_path)
    client.connect(host, username=user, password=password, timeout=3)
    logger.info("Successful SSH connection to host %s" % host)

def run_apache_benchmark():
    pass

def run_benchmarks(args):
    pass

def main():
    """Main function"""
    args = parser.parse_args()
    if args.iterations:
        args.iterations = args.iterations
    else:
        args.iterations = 5
    validate_ssh_host(args.remote, args.config, args.user, args.password)
    run_benchmarks(args)

if __name__ == '__main__':
    main()





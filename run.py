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
        logger.error("Docker engine is not present on the client system. Please install docker on the remote system.")
    try:
        run_remote_command("docker ps", True)
        logger.info("Docker engine is present on the remote system.")
    except:
        logger.fatal("Docker engine is not present on the remote system. Please install docker on the remote system.")

def docker_image_exists(image_name):
    result = str(subprocess.check_output(["docker", "image", "ls", image_name]))
    if image_name not in result:
        return False
    return True

def build_docker_image(test_name, client_image_name):
    old_cwd = os.getcwd()
    os.chdir("./benchmarks/%s/%s" % (test_name, client_image_name))
    try:
        subprocess.check_output(["docker", "build", ".", "-f", "%s.Dockerfile" % client_image_name, "-t", client_image_name], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logger.error("Failed to build container image '%s' for test '%s' with error '%s'" % (client_image_name, test_name, e.output))
    os.chdir(old_cwd)

def copy_image_to_remote(image_name):
    filename = "%s.tar" % image_name
    try:
        os.remove("%s/filename" % os.getcwd())
    except FileNotFoundError:
        pass
    logger.info("Copying docker image %s to the remote system" % image_name)
    subprocess.check_output(["docker", "image", "save", image_name, "-o", filename])
    scp_client = scp.SCPClient(client.get_transport())
    scp_client.put(filename)
    logger.info("Loading docker image %s on remote system" % image_name)
    run_remote_command("docker load -i ~/%s" % filename)
    run_remote_command("rm ~/%s" % filename)
    os.remove("%s/filename" % os.getcwd())

def run_remote_image(image_name, port):
    logger.info("Running remote docker image %s" % image_name)
    remote_images = run_remote_command("docker image ls")
    if image_name not in str(remote_images):
        logger.info("Remote docker image %s does not exist on remote system" % image_name)
        copy_image_to_remote(image_name)
    else:
        logger.info("Remote docker image %s exists on remote system" % image_name)

    run_remote_command("docker kill %s" % (image_name))
    run_remote_command("docker run --rm --name %s -d -p %d:%d %s" % (image_name, port, port, image_name), True)

def run_benchmark_image(test_name, image_name, ip):
    old_cwd = os.getcwd()
    os.chdir("./benchmarks/%s/%s" % (test_name, image_name))
    logger.info("Running benchmark image %s", image_name)
    subprocess.run(["docker", "rm", image_name], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    subprocess.check_output(["docker", "run", "-e", "REMOTE_TESTING_HOST=%s" % ip, "--name", image_name, image_name])
    os.chdir(old_cwd)

def run_apache_benchmark(ip, protection_string, iteration):
    test_name = "apache"
    client_image_name = "apache_load_tester"
    server_image_name = "apache"
    if not docker_image_exists(client_image_name):
        logger.info("Client docker image %s for test %s does not exist. Building it now." % (client_image_name, test_name))
        build_docker_image(test_name, client_image_name)

    if not docker_image_exists(server_image_name):
        logger.info("Docker image %s for test %s does not exist. Building it now." % (server_image_name, test_name))
        build_docker_image(test_name, server_image_name)

    run_remote_image(server_image_name, 80)
    run_benchmark_image("apache", client_image_name, ip)
    output = subprocess.check_output(["docker", "logs", client_image_name]).decode("utf-8")

    os.makedirs("%s/results/apache" % os.getcwd(), exist_ok=True)
    filename = "apache_%i_%s.txt" % (iteration+1, protection_string)
    with open("%s/results/apache/%s" % (os.getcwd(), filename), "w") as f:
        f.write(output)

def generate_results_csv(results):
    try:
        os.remove("%s/results/summary_results.csv" % os.getcwd())
    except FileNotFoundError:
        pass
    with open('results/summary_results.txt', 'w') as f:
        f.write(results)

def parse_apache_results():
    result = "Apache Results:\n"
    times = []
    run_info = []
    for run_data in sorted(os.listdir("%s/results/apache" % os.getcwd()), key=lambda f: int(f.split("_")[1])):
        with open("%s/results/apache/%s" % (os.getcwd(), run_data)) as f:
            lines = f.readlines()
            parts = run_data.split("_")
            iteration = parts[1]
            protection_status = parts[2].split(".")[0]
            for line in lines:
                if "Requests per second" in line:
                    times.append(float(line.split()[3]))
                    run_info.append([iteration, protection_status])
                    break
    print(times)
    mean =  statistics.mean(times)
    std_dev = statistics.stdev(times)
    for i, time in enumerate(times):
        result += "\tRun %s requests per second (%s):\t%f\n" % (run_info[i][0], run_info[i][1], time)
    result += "\tMean: %f\n" % mean
    result += "\tStandard Deviation: %f\n" % std_dev
    return result

def clean_results(test, protection_status):
    path = "%s/results/%s" % (os.getcwd(), test)
    if os.path.exists(path):
        for f in os.listdir(path):
            if protection_status in f:
                os.remove(path + "/" + f)

def run_benchmarks(args):
    results = ""
    protection_string = "unprotected"
    if args.security_enabled:
        protection_string = "protected"
    clean_results("apache", protection_string)
    for i in range(args.iterations):
        run_apache_benchmark(args.ip, protection_string, i)
    results += parse_apache_results()

    generate_results_csv(results)

def main():
    """Main function"""
    args = parser.parse_args()
    if args.iterations:
        args.iterations = args.iterations
    else:
        args.iterations = 5
    validate_ssh_host_connection(args.ip, args.user, args.password)
    validate_docker_install()

    run_benchmarks(args)

if __name__ == '__main__':
    main()





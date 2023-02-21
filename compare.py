#!/usr/bin/python3
"""Program to run various benchmarks for popular Linux software"""
import argparse
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SecurityPerfCompare')

def check_file_exists(value):
    """Checks if value is positive"""
    value = str(value)
    if not os.path.exists(value):
        raise argparse.ArgumentTypeError("The file %s does not exist" % value)
    return value

parser = argparse.ArgumentParser()

all_benchmarks = list(
        filter(lambda f: os.path.isdir("%s/benchmarks/%s" % (os.getcwd(), f))
               and f != "__pycache__",
               os.listdir("%s/benchmarks" % os.getcwd())))

parser.add_argument('-pf', '--protected-file', type=check_file_exists, required=True,
                    help="""The summary_results.txt file containing the data for a protected """
                         """run.""")

parser.add_argument('-uf', '--unprotected-file', type=check_file_exists, required=True,
                    help="""The summary_results.txt file containing the data for an unprotected """
                         """run.""")


def parse_results(data):
    """Parse results file and gather mean and standard deviation metrics"""
    results = {}
    for i in range(len(data)): # pylint: disable=consider-using-enumerate
        if "Results" in data[i]:
            test = data[i].split()[0]
            mean = -1
            stdev = -1
            for j in range(i, len(data)):
                if "Mean" in data[j]:
                    mean = float(data[j].split()[-1])
                elif "Standard Deviation" in data[j]:
                    stdev = float(data[j].split()[-1])
                if mean != -1 and stdev != -1:
                    i = j
                    break
            results[test] = {"mean": mean, "stdev": stdev}
    return results

def compare_files(protected_file, unprotected_file):
    """Compare two results files"""
    protected_results = None
    unprotected_results = None
    with open(protected_file) as protected_f:
        protected_results = parse_results(protected_f.readlines())

    with open(unprotected_file) as unprotected_f:
        unprotected_results = parse_results(unprotected_f.readlines())

    output = ""

    for test in protected_results:
        if test in unprotected_results:
            output += "%s\n" % test
            mean_overhead = (protected_results[test]["mean"]
                             - unprotected_results[test]["mean"]) / protected_results[test]["mean"]
            output += "\tProtected mean %s\n" % protected_results[test]["mean"]
            output += "\tUnprotected mean %s\n" % unprotected_results[test]["mean"]
            output += "\tProtected stdev %s\n" % protected_results[test]["stdev"]
            output += "\tUnprotected stdev %s\n" % unprotected_results[test]["stdev"]
            output += "\tOverhead %f\n\n" % mean_overhead
        else:
            logger.warn("Test %s missing from unprotected results file.", test) # pylint: disable=deprecated-method

        with open("comparison_results.txt", "w") as comparison_results:
            comparison_results.write(output)

def main():
    """Main function"""
    args = parser.parse_args()
    compare_files(args.protected_file, args.unprotected_file)

if __name__ == '__main__':
    main()

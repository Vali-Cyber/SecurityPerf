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

parser.add_argument('-modified', '--modified', type=check_file_exists, required=True,
                    help="""The summary_results.txt file containing the data for a modified """
                         """system.""")

parser.add_argument('-b', '--baseline', type=check_file_exists, required=True,
                    help="""The summary_results.txt file containing the data for a baseline """
                         """system.""")


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

def compare_files(modified_file, baseline_file):
    """Compare two results files"""
    modified_results = None
    baseline_results = None
    with open(modified_file) as modified_f:
        modified_results = parse_results(modified_f.readlines())

    with open(baseline_file) as baseline_f:
        baseline_results = parse_results(baseline_f.readlines())

    output = ""

    for test in modified_results:
        if test in baseline_results:
            output += "%s\n" % test
            mean_overhead = (baseline_results[test]["mean"]
                             - modified_results[test]["mean"]) / baseline_results[test]["mean"]
            output += "\tModified mean %s\n" % modified_results[test]["mean"]
            output += "\tBaseline mean %s\n" % baseline_results[test]["mean"]
            output += "\tModified stdev %s\n" % modified_results[test]["stdev"]
            output += "\tBaseline stdev %s\n" % baseline_results[test]["stdev"]
            output += "\tOverhead %f%%\n\n" % (mean_overhead*100)
        else:
            logger.warn("Test %s missing from baseline results file.", test) # pylint: disable=deprecated-method

        with open("comparison_results.txt", "w") as comparison_results:
            comparison_results.write(output)

def main():
    """Main function"""
    args = parser.parse_args()
    compare_files(args.modified, args.baseline)

if __name__ == '__main__':
    main()

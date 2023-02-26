# SecurityPerf

SecurityPerf is a tool designed to make benchmarking production workloads easy.
The development of SecurityPerf was motivated by the need to accurately determine
the overhead of a security solution when it is deployed on diverse production
workloads in a manner that is reproducible by anyone and provides meaningful results
for enterprise-grade production systems.
Many benchmarking tools and suites exist, though some are expensive
and many are specific to a given use case. SecurityPerf addresses these problems
by providing an open source, always free to use solution that leverages other
open-source benchmarking tools and containerization to allow anyone to run
realistic benchmarks for common production workloads.

SecurityPerf focuses on Linux server software. The currently available benchmarks
are:

1. Apache
2. Mongodb
3. MySQL
4. Rabbitmq
5. WordPress (Using a MySQL database)

Other planned benchmarks are:

1. Postgress
2. WordPress (Using a Postgress database)
3. Postfix
4. Apache Kafka

Additional benchmarks are open for consideration. If there is a benchmark you'd
like to see integrated into SecurityPerf, submit an issue and we'll respond
as quickly as we can.

# Prerequisites

To use SecurityPerf, you need two Linux systems that have the latest Docker engine
and python3 installed. One of the systems must have SSH installed. SecurityPerf uses
password-based SSH authentication to log in to systems.

The requirements.txt file provides the python dependencies
required to run SecurityPerf. You must install the dependencies on the system where you
run `run.py`. You can install the dependencies with the following command.

`pip3 install -r requirements.txt`

You must be able to run docker commands without `sudo` on both systems. This step
can be achieved with the following command:

`sudo usermod -aG docker USERNAME`

You cannot run any services on the systems with ports that conflict with the services
being tested. The services being tested use their default ports. For example,
apache uses port 80.

# How It Works

SecurityPerf takes advantage of containerization to run diverse workloads and
benchmarking tools on any Linux system a user might choose. SecurityPerf uses
two systems, one that represents a server which runs the services being benchmarked
and one that represents the client.
The client system runs the benchmarking software.

SecurityPerf builds the container images located in the `benchmarks directory.
It then copies service images to sever system. Benchmark images remain on the
client system. The client system runs the benchmarking software and puts the service
under load. After each iteration of a benchmarking test, SecurityPerf saves
the results as a text file in the "results" directory under a subdirectory
with the name of the service being tested. After all iterations of tests
for all services are tested, a summary file is generated that aggregates
the results and calculated the mean and standard deviation of the results
for each service.

For more details, run `./run.py -h` for details on the run script and its
parameters.

# Getting started

To get started, set up two systems and run the Apache benchmark. Here is an example
instantiation of the `run.py` script that will run only the Apache benchmark.

`./run.py -ip 192.168.1.2 -u username -p password -b apache`

SecurityPerf is designed to compare the results from two runs. A single run
will produce a `summary_results.txt` file in the `results` directory.
All results are stored in a subdirectory of results that contains is tagged using
the `-t` flag and a timestamp. An example name is `baseline_2023-02-20_21-18-22`.
To change the tag the results directory, use the `-t` flag that `run.py` provides.
For example, running with `-t unprotected` will create a subdirectory similar to
`unprotected_2023-02-20_21-18-22`.

You may compare two `summary_results.txt` files using `compare.py`. `compare.py`
will produce a file called `comparison_results.txt`. Here is an example
invocation of the `compare.py` script:

`./compare.py  --protected results/protected_2023-02-20_21-18-22/summary_results.txt --unprotected results/unprotected_2023-02-20_22-19-13/summary_results.txt`


# Adding a New Benchmark

To add a new benchmark, create a new subdirectory for the service
in the benchmarks directory. Then, create two subdirectories within that directory.
One subdirectory for the benchmarking docker image, and one subdirectory for
the service's docker image. Each service contains a python script that defines
a subclass for the benchmark. The parent class is in `benchmarks/benchmark.py`.
Most benchmarks simply define how to run the docker images and the names of
various strings. The wordpress.py file is slightly more complicated, as it
overrides some functions the Benchmarks class defines. The reason for this
distinction is the fact that WordPress starts two services rather than one,
Apache and MySQL.

For more detail, look at the `apache.py` script. It is commented well with
details about each field.

# Common Pitfalls

If a benchmark doesn't connect to its service, it may be caused by the service
not being ready yet. Each benchmark subclass defines a parameter called
`service_initialization_delay`. This class member defines how long the benchmark
should wait for the service to be ready. Increasing this number will address
issues caused by a service being slow to start.

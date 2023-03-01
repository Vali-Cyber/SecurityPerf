FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install -y  maven default-jdk curl python2.7
RUN ln -s /usr/bin/python2.7 /usr/bin/python
RUN curl -O --location https://github.com/brianfrankcooper/YCSB/releases/download/0.17.0/ycsb-0.17.0.tar.gz
RUN tar xfvz ycsb-0.17.0.tar.gz
WORKDIR ycsb-0.17.0
RUN sed -i -e 's/recordcount=1000/recordcount=500000/g' ./workloads/workloada && \
    sed -i -e 's/operationcount=1000/operationcount=500000/g' ./workloads/workloada && \
    sed -i -e 's/readproportion=0.5/readproportion=0.4/g' ./workloads/workloada && \
    sed -i -e 's/updateproportion=0.5/updateproportion=0.4/g' ./workloads/workloada && \
    sed -i -e 's/scanproportion=0.0/scanproportion=0.1/g' ./workloads/workloada && \
    sed -i -e 's/insertproportion=0.0/insertproportion=0.1/g' ./workloads/workloada
ENTRYPOINT ./bin/ycsb load mongodb -s -P workloads/workloada -threads $(grep -c ^processor /proc/cpuinfo) -p mongodb.url=mongodb://root:pass@$REMOTE_TESTING_HOST:27017

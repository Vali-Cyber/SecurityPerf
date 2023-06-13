FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt -y install curl
RUN curl -s https://packagecloud.io/install/repositories/akopytov/sysbench/script.deb.sh | bash
RUN apt -y install sysbench
COPY postgres_load_tester.sh .
COPY oltp_read_write.lua .
ENTRYPOINT ["./postgres_load_tester.sh"]

FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install -y  default-libmysqlclient-dev libtool pkg-config gcc make
ADD sysbench-1.0.20.tar.gz /
WORKDIR sysbench-1.0.20
RUN ./autogen.sh
RUN ./configure
RUN make
RUN make install
COPY mysql_load_tester.sh .
ENTRYPOINT ["./mysql_load_tester.sh"]

FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install -y apache2
COPY httpd_load_tester.sh /
RUN useradd -ms /bin/bash httpd_load_tester_user
USER httpd_load_tester_user
ENTRYPOINT ["/httpd_load_tester.sh"]

FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install -y apache2
COPY httpd_load_tester.sh /
RUN useradd -ms /bin/bash httpd_load_tester_user
USER httpd_load_tester_user
# Run 1,000,000 requests with 100 requests being sent concurrently. Results are provided to the volume /results
ENTRYPOINT ["/httpd_load_tester.sh"]

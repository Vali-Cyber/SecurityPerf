FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install -y apache2
WORKDIR /app
COPY apache_load_tester.sh /app
RUN useradd -ms /bin/bash apache_load_tester_user
USER apache_load_tester_user
# Run 1,000,000 requests with 100 requests being sent concurrently. Results are provided to the volume /results
ENTRYPOINT ["./apache_load_tester.sh"]

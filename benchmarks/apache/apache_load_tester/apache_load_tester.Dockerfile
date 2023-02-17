FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install -y apache2
WORKDIR /app
COPY apache_load_tester.sh /app
RUN useradd -ms /bin/bash apache_load_tester_user
USER apache_load_tester_user
ENTRYPOINT ["./apache_load_tester.sh"]

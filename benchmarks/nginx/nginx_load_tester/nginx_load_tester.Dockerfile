FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install -y apache2
WORKDIR /app
COPY nginx_load_tester.sh /app
RUN useradd -ms /bin/bash nginx_load_tester_user
USER nginx_load_tester_user
ENTRYPOINT ["./nginx_load_tester.sh"]

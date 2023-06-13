FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install -y apache2
CMD ["apachectl", "-D", "FOREGROUND"]

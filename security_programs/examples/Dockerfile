FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install -y gcc g++ cmake
RUN mkdir /app
CMD ["apachectl", "-D", "FOREGROUND"]
RUN useradd -ms /bin/bash builder
RUN chown builder /app
USER builder
WORKDIR /app

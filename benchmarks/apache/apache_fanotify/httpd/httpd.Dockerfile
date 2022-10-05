FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install -y apache2
COPY ./run.sh /run.sh
COPY fanotify/fanotify /bin
RUN chmod +x run.sh bin/fanotify
CMD ["/run.sh"]

FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install -y apache2
WORKDIR /app
COPY wordpress_load_tester.sh /app
RUN useradd -ms /bin/bash wordpress_load_tester_user
USER wordpress_load_tester_user
ENTRYPOINT ["./wordpress_load_tester.sh"]

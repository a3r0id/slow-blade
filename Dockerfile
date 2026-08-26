FROM kalilinux/kali-rolling:latest

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    kali-linux-headless \
    iputils-ping \
    dnsutils \
    net-tools \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER root

WORKDIR /app

CMD ["tail", "-f", "/dev/null"]
FROM ubuntu

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        qemu-system-s390x telnet

WORKDIR /app

CMD ["./boot.sh"]

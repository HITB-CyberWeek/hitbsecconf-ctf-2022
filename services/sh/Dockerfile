FROM ubuntu:latest

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        python3 python3-pip \
        7zip unace unalz arj bzip2 cabextract cpio gzip lzip lzop unrar tar xz-utils unzip

RUN groupadd -g 998 docker
RUN useradd sh -m -u 12345 -U -G docker

WORKDIR /home/sh
USER sh

RUN pip3 install --user docker patool rq minio
COPY --chown=sh:sh . /home/sh/

FROM ubuntu

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        python3 python3-pip \
        p7zip bzip2 gzip unrar unzip

ARG DOKER_GROUP=999
RUN groupadd -g ${DOKER_GROUP} docker
RUN useradd sh -m -u 12345 -U -G docker

WORKDIR /home/sh
USER sh

RUN pip3 install --user docker patool rq minio fastapi uvicorn[standard] python-multipart
COPY --chown=sh:sh . /home/sh/

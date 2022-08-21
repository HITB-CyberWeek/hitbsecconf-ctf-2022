FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        python3 pip pkg-config build-essential \
        git \
        libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev libglib2.0-dev

RUN pip3 install ninja

RUN git config --global --add safe.directory '*'

CMD cd /qemu && rm -rf build && mkdir build && cd build && ../configure && make -j4

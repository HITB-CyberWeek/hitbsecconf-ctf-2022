FROM ghcr.io/hackerdom/checksystem:master

# Checker deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip software-properties-common && \
    apt-add-repository non-free && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        p7zip bzip2 gzip rar zip
RUN pip install patool requests

# Config
COPY cs/cs.conf /app/c_s.conf

# Checkers
COPY checkers/sh /app/checkers/sh

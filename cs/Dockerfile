FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build-dot-net-checkers
WORKDIR /app

COPY checkers/smallword/src/ /app/
RUN dotnet publish -c release -o ./smallword-publish


FROM ghcr.io/hackerdom/checksystem:master

# Checker deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip software-properties-common && \
    apt-add-repository non-free && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        p7zip bzip2 gzip rar zip
RUN pip install patool requests beautifulsoup4

ENV DOTNET_CLI_TELEMETRY_OPTOUT=1

RUN wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && apt-get install -y dotnet-sdk-6.0

# Config
COPY cs/cs.conf /app/c_s.conf

# Checkers
COPY checkers/sh /app/checkers/sh
COPY checkers/crs /app/checkers/crs
COPY checkers/smallword /app/checkers/smallword
COPY checkers/mypack /app/checkers/mypack
COPY checkers/wallet /app/checkers/wallet
COPY checkers/n0tes /app/checkers/n0tes
COPY --from=build-dot-net-checkers /app/smallword-publish/ /app/checkers/smallword/src/bin/Release/net6.0/publish

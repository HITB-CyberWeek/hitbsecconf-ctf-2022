#!/bin/bash
set -eu

URL="https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-s390x.img"
CACHE="/tmp/jammy-server-cloudimg-s390x.img"

if [ -f "$CACHE" ]; then
    echo "Cached file exists at '$CACHE'."
else
    echo "Downloading $URL to '$CACHE' ..."
    wget $URL -O $CACHE
fi

echo "Copying to working directory ..."
cp -v $CACHE qemu.img

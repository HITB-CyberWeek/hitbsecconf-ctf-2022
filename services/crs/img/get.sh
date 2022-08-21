#!/bin/bash
set -eu

#URL="https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-s390x.img"
#CACHE="/tmp/jammy-server-cloudimg-s390x.img"
#
# User process fault: interruption code 0011 ilc:3
# https://bugs.launchpad.net/ubuntu/+source/openssh/+bug/1970076

URL="https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-s390x.img"
CACHE="/tmp/focal-server-cloudimg-s390x.img"

if [ -f "$CACHE" ]; then
    echo "Cached file exists at '$CACHE'."
else
    echo "Downloading $URL to '$CACHE' ..."
    wget --no-verbose $URL -O $CACHE
fi

echo "Copying to working directory ..."
cp -v $CACHE qemu.img

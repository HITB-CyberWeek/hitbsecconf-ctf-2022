#!/bin/bash
set -eu

IMAGE="qemu.img"

mkdir -p mnt
modprobe nbd max_part=8
qemu-nbd --connect=/dev/nbd0 $IMAGE
sleep 3
mount /dev/nbd0p1 ./mnt

echo "Mounted."

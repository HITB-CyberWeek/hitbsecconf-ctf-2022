#!/bin/bash
set -eux

cd img

./get.sh
sudo ./mount.sh
sudo ./prepare.sh
sudo ./umount.sh

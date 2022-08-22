#!/bin/bash
set -eux

cd img

sudo ./umount.sh || true  # Just in case previous step has failed.

./get.sh
sudo ./mount.sh
sudo ./prepare.sh
sudo ./umount.sh

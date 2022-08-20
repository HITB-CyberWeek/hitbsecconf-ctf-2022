#!/bin/bash
set -eux

cd img

./get.sh
./mount.sh
./prepare.sh
./umount.sh

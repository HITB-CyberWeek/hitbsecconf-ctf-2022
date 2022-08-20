#!/bin/bash

umount ./mnt
qemu-nbd --disconnect /dev/nbd0
sleep 3
rmmod nbd

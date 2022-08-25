#!/bin/bash
set -eu

IMAGE="qemu.img"
CPU="max,zpci=on,msa-base=off"
MEM=4096
CORES=$(nproc)


SERIAL="-chardev stdio,id=char0,mux=on,logfile=serial.log,signal=off -serial chardev:char0 -mon chardev=char0"

# Telnet serial console can be used if ssh to vm is broken:
# * uncomment,
# * restart docker container,
# * telnet localhost 4441,
# * use root password: WA7NERURoVlDegBUVyM1Kk
#
# SERIAL="-serial telnet::4441,server=on,wait=off"

qemu-system-s390x -machine s390-ccw-virtio -cpu $CPU -m $MEM \
    $SERIAL -display none \
    -drive format=qcow2,file=$IMAGE,cache=none,id=drive-virtio-disk0,if=none \
    -device virtio-blk-ccw,devno=fe.0.0001,drive=drive-virtio-disk0,id=virtio-disk0,bootindex=1,scsi=off \
    -smp $CORES \
    -device virtio-net,netdev=vmnic -netdev user,id=vmnic,hostfwd=tcp::4444-:4444,hostfwd=tcp::2222-:22

#!/bin/bash
set -eu

IMAGE="qemu.img"
CPU="max,zpci=on"
MEM=4096
CORES=4

qemu-system-s390x -machine s390-ccw-virtio -cpu $CPU -m $MEM \
    -chardev stdio,id=char0,mux=on,logfile=serial.log,signal=off \
    -serial chardev:char0 -mon chardev=char0 -display none \
    -drive format=qcow2,file=$IMAGE,cache=none,id=drive-virtio-disk0,if=none \
    -device virtio-blk-ccw,devno=fe.0.0001,drive=drive-virtio-disk0,id=virtio-disk0,bootindex=1,scsi=off \
    -smp $CORES \
    -device virtio-net,netdev=vmnic -netdev user,id=vmnic,hostfwd=tcp::14444-:4444

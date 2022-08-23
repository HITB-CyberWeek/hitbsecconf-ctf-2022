#!/bin/bash

screen -dmS ClearOld python3 ./ClearLast20mins.py

mkdir -p data
chown mypack:mypack data
chmod +x parser.elf

while true; do
    socat -dd TCP4-LISTEN:3777,reuseaddr,fork,keepalive exec:./run.sh,end-close
    sleep 5
done

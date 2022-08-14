#!/bin/sh

while true; do
    socat TCP-LISTEN:31337,reuseaddr,fork EXEC:"timeout 30 python3.9 -u main.py"
done

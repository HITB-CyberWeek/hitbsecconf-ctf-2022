#!/bin/bash
# removes rules for teams snat
# this script shouldn't be run normally :)

for num in {0..767}; do 
    ip="10.$((80 + num / 256)).$((num % 256)).1"

    iptables -t nat -D POSTROUTING -o team${num} -d 10.60.0.0/14 -j SNAT --to-source ${ip}
done

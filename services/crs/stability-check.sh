#!/bin/bash
while true; do
    echo -e "\n **** $(date) ****\n"
    docker compose restart
    echo "Sleeping..."
    sleep 180
    echo "Logs:"
    docker logs crs -n 10
    echo "Service checks:"
    echo 123 | timeout 1 nc localhost 4444 | tail -n1
    echo
done

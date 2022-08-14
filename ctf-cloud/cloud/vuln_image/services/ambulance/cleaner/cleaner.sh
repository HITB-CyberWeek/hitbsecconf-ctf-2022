#!/bin/sh

while true; do
    date -uR

    find "/tmp/users/" \
        -type f \
        -and -not -newermt "-1800 seconds" \
        -delete

    find "/tmp/diseases/" \
        -type f \
        -and -not -newermt "-1800 seconds" \
        -delete

    sleep 60
done

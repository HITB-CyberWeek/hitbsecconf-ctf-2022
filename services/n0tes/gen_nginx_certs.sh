#!/bin/bash

HOST="n0tes.hitb.org"

echo "Generating self-signed certificate for $HOST"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/n0tes.key -out nginx/n0tes.crt -subj "/CN=$HOST"

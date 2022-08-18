#!/bin/bash

HOST="n0tes.hitb.org"
ADMIN_HOST="admin.n0tes.hitb.org"

if [ ! -f nginx/n0tes.key ] || [ ! -f nginx/n0tes.crt ] ; then
    echo "Generating self-signed certificate for $HOST and $ADMIN_HOST"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/n0tes.key -out nginx/n0tes.crt -subj "/CN=$HOST" -addext "subjectAltName = DNS:$ADMIN_HOST"
fi

if [ ! -f  n0tes-admin.key ] || [ ! -f n0tes-admin.crt ] ; then
    echo "Generating admin self-signed certificate"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout n0tes-admin.key -out n0tes-admin.crt -subj "/CN=n0tes admin"
    cp n0tes-admin.crt nginx/
fi

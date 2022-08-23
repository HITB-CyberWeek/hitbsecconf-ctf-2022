#!/bin/bash

HOST="n0tes.ctf.hitb.org"
ADMIN_HOST="admin.n0tes.ctf.hitb.org"

if [ ! -f nginx/n0tes.key ] || [ ! -f nginx/n0tes.crt ] ; then
    echo "Generating self-signed certificate for $HOST and $ADMIN_HOST"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/n0tes.key -out nginx/n0tes.crt -subj "/CN=$HOST" -addext "subjectAltName = DNS:$ADMIN_HOST"
    cp nginx/n0tes.crt ../../checkers/n0tes/
fi

if [ ! -f  ../../checkers/n0tes/n0tes-admin.key ] || [ ! -f ../../checkers/n0tes/n0tes-admin.crt ] ; then
    echo "Generating admin self-signed certificate"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ../../checkers/n0tes/n0tes-admin.key -out ../../checkers/n0tes/n0tes-admin.crt -subj "/CN=n0tes admin"
    cp ../../checkers/n0tes/n0tes-admin.crt nginx/
fi

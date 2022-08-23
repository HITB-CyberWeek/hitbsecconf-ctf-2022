#!/bin/bash

n=$1
HOST="${HOST:-localhost}"
CHECKER_DIRECT_CONNECT="${CHECKER_DIRECT_CONNECT:-1}"
export CHECKER_DIRECT_CONNECT


function random_string () {
    chars=123qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM
    rand_string=
    for i in {1..20} ; do
        rand_string="${rand_string}${chars:RANDOM%${#chars}:1}"
    done
}

function check_verdict () {
    verdict=$?
    if [ $verdict -ne 101 ]
    then
        echo "ERROR:Bad_vardict:$verdict"
        exit 200
    fi
}

for i in $(seq 1 $n)
do
    echo "RUN:$i"
    random_string
    flag=${rand_string}
    flag_id=$RANDOM

    ./kv.checker.py check $HOST
    check_verdict

    flag_id=$(./kv.checker.py put $HOST $flag_id $flag 1)
    check_verdict
    echo "FLAG_ID:${flag_id}"

    ./kv.checker.py get $HOST "${flag_id}" "${flag}" 1
    check_verdict

done

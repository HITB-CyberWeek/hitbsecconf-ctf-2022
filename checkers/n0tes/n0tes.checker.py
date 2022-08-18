#!/usr/bin/env python3

import sys
import traceback
import requests
import random
import string
import json
requests.packages.urllib3.disable_warnings()
from checker_helper import *

PORT = 8443
TIMEOUT = 30

def info():
    verdict(OK, "vulns: 1\npublic_flag_description: Flag ID is a title of the note containing the flag")

def check(args):
    if len(args) != 1:
        verdict(CHECKER_ERROR, "Checker error", "Wrong args count for check()")
    host = args[0]
    trace("check(%s)" % host)

    verdict(OK)

def get_random_string(min_len, max_len):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(random.randint(min_len, max_len)))

def login(host, user, password):
    n0tes_url = f"https://{host}:{PORT}/"

    try:
        r = requests.get(n0tes_url, timeout=TIMEOUT, verify=False)
    except (requests.exceptions.ConnectionError, ConnectionRefusedError, http.client.RemoteDisconnected) as e:
        return (DOWN, "Connection error", "Connection error during login: %s" % e, None)
    except requests.exceptions.Timeout as e:
        return (DOWN, "Timeout", "Timeout during login: %s" % e, None)

    session = requests.Session()

    return (OK, "", "", session)

def put(args):
    if len(args) != 4:
        verdict(CHECKER_ERROR, "Checker error", "Wrong args count for put()")
    host, flag_id, flag, vuln = args
    trace("put(%s, %s, %s, %s)" % (host, flag_id, flag, vuln))

    note_title = flag_id
    user = get_random_string(5, 15)
    password = get_random_string(7, 20)

    (status, out, err, session) = login(host, user, password)
    if status != OK:
        verdict(status, out, err)

    flag_id = json.dumps({"public_flag_id": note_title, "user": user, "password": password})
    verdict(OK, flag_id)

def get(args):
    if len(args) != 4:
        verdict(CHECKER_ERROR, "Checker error", "Wrong args count for get()")
    host, flag_id, flag_data, vuln = args
    trace("get(%s, %s, %s, %s)" % (host, flag_id, flag_data, vuln))

    verdict(OK)

def main(args):
    if len(args) == 0:
        verdict(CHECKER_ERROR, "Checker error", "No args")
    try:
        if args[0] == "info":
            info()
        elif args[0] == "check":
            check(args[1:])
        elif args[0] == "put":
            put(args[1:])
        elif args[0] == "get":
            get(args[1:])
        else:
            verdict(CHECKER_ERROR, "Checker error", "Wrong action: " + args[0])
    except Exception as e:
        verdict(CHECKER_ERROR, "Checker error", "Exception: %s" % traceback.format_exc())

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
        verdict(CHECKER_ERROR, "Checker error", "No verdict")
    except Exception as e:
        verdict(CHECKER_ERROR, "Checker error", "Exception: %s" % e)

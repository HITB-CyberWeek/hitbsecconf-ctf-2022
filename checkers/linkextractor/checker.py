#!/usr/bin/env python3

import sys
import os
import socket
import hashlib
import random
import time
import json
import traceback
from urllib.parse import urljoin

import requests

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110

PORT = 80
TIMEOUT = 10

#CHECKER_DIRECT_CONNECT = os.environ.get("CHECKER_DIRECT_CONNECT")

def verdict(exit_code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    sys.exit(exit_code)



def info():
    verdict(OK, "vulns: 1\npublic_flag_description: Flag ID is page ID, flag is in page url\n")


def gen_login():
    ABC = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ" #_$()'
    return "".join(random.choice(ABC) for i in range(random.randrange(6, 10)))


def gen_password():
    ABC = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ" #_@$.,';:
    return "".join(random.choice(ABC) for i in range(random.randrange(10, 16)))


def gen_text():
    return random.choice([gen_password(), gen_login(), gen_color(), "hello", "cccc", "#121212121"])


def register_or_login_user(session, base_url, user, password):
    register_data = {"login": user, "password": password}
    try:
        r = session.post(urljoin(base_url, "/users"), data=json.dumps(register_data), verify=False)
    except (requests.exceptions.ConnectionError, ConnectionRefusedError) as e:
        return (DOWN, "Connection error", "Connection error during registration or login: %s" % e)
    except requests.exceptions.Timeout as e:
        return (DOWN, "Timeout", "Timeout during registration or login: %s" % e)

    if r.status_code != 200:
        return (MUMBLE, "Can't register or login", "Unexpected register or login result: '%d' -> %s" %(r.status_code, r.text))

    return (OK, "", "")


def check(host):
    base_url = f"http://{host}:{PORT}/"
    session = requests.Session()

    login = gen_login()
    password = gen_password()
    (status, out, err) = register_or_login_user(session, base_url, login, password)
    if status != OK:
        verdict(status, out, err)

    if random.random() < 0.5:
        (status, out, err) = register_or_login_user(session, base_url, login, password)
        if status != OK:
            verdict(status, out, err)


    try:
        r = session.get(urljoin(base_url, "/users/whoami"))
    except (requests.exceptions.ConnectionError, ConnectionRefusedError) as e:
        verdict(DOWN, "Connection error", "Connection error during whoami: %s" % e, None)
    except requests.exceptions.Timeout as e:
        verdict(DOWN, "Timeout", "Timeout during whoami: %s" % e, None)

    if r.status_code != 200 or r.text != login:
        verdict(MUMBLE, "Can't check user", "Unexpected whoami result: '%d' -> %s" %(r.status_code, r.text))

    verdict(OK)

def put(host, flag_id, flag, vuln):
    raise Exception("put not implemented")
    


def get(host, flag_id, flag, vuln):
    raise Exception("put not implemented")

def main(args):
    CMD_MAPPING = {
        "info": (info, 0),
        "check": (check, 1),
        "put": (put, 4),
        "get": (get, 4),
    }

    if not args:
        verdict(CHECKER_ERROR, "No args", "No args")

    cmd, args = args[0], args[1:]
    if cmd not in CMD_MAPPING:
        verdict(CHECKER_ERROR, "Checker error", "Wrong command %s" % cmd)

    handler, args_count = CMD_MAPPING[cmd]
    if len(args) != args_count:
        verdict(CHECKER_ERROR, "Checker error", "Wrong args count for %s" % cmd)

    try:
        handler(*args)

    except ConnectionRefusedError as E:
        verdict(DOWN, "Connect refused", "Connect refused: %s" % E)
    except ConnectionError as E:
        verdict(MUMBLE, "Connection aborted", "Connection aborted: %s" % E)
    except OSError as E:
        verdict(DOWN, "Connect error", "Connect error: %s" % E)
    except Exception as E:
        verdict(CHECKER_ERROR, "Checker error", "Checker error: %s" % traceback.format_exc())
    verdict(CHECKER_ERROR, "Checker error", "No verdict")


if __name__ == "__main__":
    main(args=sys.argv[1:])

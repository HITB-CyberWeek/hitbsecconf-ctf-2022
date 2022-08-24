#!/usr/bin/env python3

import json
import os
import random
import re
import requests
import string
import sys
import traceback

requests.packages.urllib3.disable_warnings()
from checker_helper import *

PORT = 3000
TIMEOUT = 30
CHECKER_DIRECT_CONNECT = os.environ.get("CHECKER_DIRECT_CONNECT")
KEYS_COUNT_RE = re.compile(r'Currently stored keys: (\d+)')


def info():
    verdict(OK, "vulns: 1\npublic_flag_description: Flag ID is a client secret and a filename, flag is a file content")


def get_random_string(min_len, max_len):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(random.randint(min_len, max_len)))


def url_prefix(host):
    if CHECKER_DIRECT_CONNECT == "1":
        return f"http://{host}:{PORT}"
    return f"https://{host}"


def register(url_prefix):
    url = url_prefix + "/register"
    resp = requests.post(url, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def get_filename(url_prefix, creds, filename):
    url = url_prefix + "/kv/{}".format(filename)
    headers = {
        'X-Client-ID': creds['client_id'],
        'X-Client-Secret': creds['client_secret']
    }
    resp = requests.get(url, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def put_filename(url_prefix, creds, filename, content):
    url = url_prefix + "/kv/{}".format(filename)
    headers = {
        'X-Client-ID': creds['client_id'],
        'X-Client-Secret': creds['client_secret'],
        'Content-Type': 'application/json',
    }
    resp = requests.put(url, data=content, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()


@checker_action
def check(args):
    if len(args) != 1:
        verdict(CHECKER_ERROR, "Checker error", "Wrong args count for check()")
    host = args[0]
    url = url_prefix(host)
    trace(f"check({url})")

    resp = requests.get(url, timeout=TIMEOUT)
    resp.raise_for_status()

    content = resp.text
    match = KEYS_COUNT_RE.search(content)
    if not match:
        verdict(MUMBLE, "Bad index page; can't find keys count", f"CONTENT:{content}")

    verdict(OK)


@checker_action
def put(args):
    if len(args) != 4:
        verdict(CHECKER_ERROR, "Checker error", "Wrong args count for put()")
    host, flag_id, flag, vuln = args
    url = url_prefix(host)

    trace(f"put0({url}, {flag_id}, {flag}, {vuln})")

    creds = register(url)
    client_id = creds["client_id"]
    client_secret = creds["client_secret"]
    filename = get_random_string(10, 15)

    trace(f"put1({url}, {flag_id}, {flag}, {vuln}, {client_id}, {client_secret}, {filename})")

    put_filename(url, creds, filename, flag)

    flag_id = json.dumps({
                            "public_flag_id": f"client_id:{client_id} filename:{filename}",
                            "client_id": client_id,
                            "client_secret": client_secret,
                            "filename": filename,
                            "orig_flag_id": flag_id,
                        })
    verdict(OK, flag_id)


@checker_action
def get(args):
    if len(args) != 4:
        verdict(CHECKER_ERROR, "Checker error", "Wrong args count for get()")
    host, flag_id, flag_data, vuln = args
    url = url_prefix(host)
    trace("get(%s, %s, %s, %s)" % (url, flag_id, flag_data, vuln))

    data = json.loads(flag_id)
    creds = {
        'client_id': data['client_id'],
        'client_secret': data['client_secret'],
    }
    filename = data['filename']

    try:
        resp = get_filename(url, creds, filename)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code // 100 == 4:  # 4xx
            err = f"HTTP error! URL:{e.response.url}; http status:{e.response.status_code}"
            err_private = f"HTTPError:{e}"
            verdict(CORRUPT, err, err_private)
        raise

    if "headers" not in resp:
        verdict(MUMBLE, "Bad get response", "No 'headers' key in answer")

    if "content" not in resp:
        verdict(MUMBLE, "Bad get response", "No 'content' key in answer")

    headers = resp["headers"]
    for header in ["X-Forwarded-Proto", "Content-Length", "Content-Type"]:
        if header not in headers:
            verdict(MUMBLE, "Bad get response", f"No '{header}' header in answer")

    content = resp.get('content')
    if content == flag_data:
        verdict(OK)
    verdict(CORRUPT, "Wrong flag", f"{flag_data} != {content}")


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

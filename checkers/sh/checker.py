#!/usr/bin/env python3

import json
import logging
import os
import random
import requests
import string
import sys
import tempfile
import time
import traceback

from pathlib import Path
from patoolib import create_archive

logging.basicConfig(format="%(asctime)s [%(process)d] %(levelname)-8s %(message)s",
                    level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stderr)])

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
ARCHIVE_TYPES = ["zip", "rar", "7z", "tgz", "tbz2"]
TIMEOUT = 5


def verdict(exit_code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    sys.exit(exit_code)


def random_name(length=10):
    return ''.join(random.choices(
        string.ascii_lowercase + string.digits, k=length))


def get_base_url(host):
    base_url = f"http://{host}/"

    try:
        r = requests.options(base_url, timeout=3, allow_redirects=False)
        if r.status_code > 300 and r.status_code < 400 and r.headers["Location"]:
            base_url = r.headers["Location"]
            if not base_url[-1] == '/':
                base_url += '/'
    except:
        pass

    return base_url


def info():
    verdict(OK, "vulns: 1\npublic_flag_description: Flag ID is a bucket name, flag is a content of the file with '.txt' suffix in the bucket")


def check(host):
    bucket = random_name()
    file_name = random_name(length=5)

    base_url = get_base_url(host)
    url = f"{base_url}~{bucket}/{file_name}.txt"
    logging.info(f"Check url '{url}' on host '{host}'")

    r = requests.get(url, timeout=TIMEOUT)
    if r.status_code == 404:
        verdict(OK)
    else:
        verdict(MUMBLE, public="Wrong HTTP status code")


def put(host, flag_id, flag, vuln):
    bucket = random_name()
    file_name = random_name(length=5)
    archive_name = random_name(length=5)
    external_archive_name = random_name(length=5)

    state = {"public_flag_id": bucket, "file_name": file_name}

    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as workdir:
        os.chdir(workdir)
        logging.info(f"Changed current directory to '{workdir}'")
        flag_file = Path(f"{file_name}.txt")
        flag_file.write_text(flag)
        logging.info(f"Created file with flag '{flag_file}'")

        (suffix1, suffix2) = random.sample(ARCHIVE_TYPES, 2)
        archive = Path(workdir) / f"{archive_name}.{suffix1}"
        create_archive(archive=archive, filenames=[flag_file], verbosity=-1)
        logging.info(f"Created archive '{archive}' with flag '{flag_file}'")

        filenames = [f"{archive_name}.{suffix1}"]
        for _ in range(3):
            f = Path(random_name(length=5) + ".txt")
            f.write_text(random_name(length=1024))
            filenames.append(f.name)
        external_archive = Path(workdir) / f"{external_archive_name}.{suffix2}"
        create_archive(archive=external_archive,
                       filenames=filenames, verbosity=-1)
        logging.info(f"Created external archive '{external_archive}'")

        base_url = get_base_url(host)
        url = f"{base_url}bucket/~{bucket}"
        logging.info(f"Put to url '{url}' on host '{host}'")
        r = requests.post(
            url, files={"input": external_archive.open(mode="rb")}, timeout=TIMEOUT)
        if r.status_code != 200:
            verdict(MUMBLE, public="Wrong HTTP status code")

    os.chdir(cwd)
    logging.info("Waiting for process...")
    time.sleep(15)

    verdict(OK, json.dumps(state))


def get(host, flag_id, flag, vuln):
    state = json.loads(flag_id)

    bucket = state["public_flag_id"]
    file_name = state["file_name"]

    base_url = get_base_url(host)
    url = f"{base_url}~{bucket}/{file_name}.txt"
    logging.info(f"Get from url '{url}' on host '{host}'")

    r = requests.get(url, timeout=5)
    if r.status_code == 404:
        verdict(CORRUPT, public="Wrong HTTP status code")
    if r.status_code != 200:
        verdict(MUMBLE, public="Wrong HTTP status code")

    responce = r.text
    if responce != flag:
        logging.info(f"Responce '{responce}' does not equal flag '{flag}'")
        verdict(CORRUPT, public="Wrong flag data")
    else:
        verdict(OK)


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
        verdict(CHECKER_ERROR, "Checker error", f"Wrong command {cmd}")

    handler, args_count = CMD_MAPPING[cmd]
    if len(args) != args_count:
        verdict(CHECKER_ERROR, "Checker error",
                f"Wrong args count for {cmd}")

    try:
        handler(*args)
    except (requests.Timeout, requests.ConnectionError):
        logging.debug(traceback.format_exc())
        verdict(DOWN, public="Can't get HTTP response")

    verdict(CHECKER_ERROR, "Checker error", "No verdict")


if __name__ == "__main__":
    main(args=sys.argv[1:])

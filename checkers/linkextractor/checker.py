#!/usr/bin/env python3

import sys
import os
import socket
import hashlib
import random
import time
import json
import traceback
import logging
from urllib.parse import urljoin, quote_plus, urlparse

import requests

logging.basicConfig(format="%(asctime)s [%(process)d] %(levelname)-8s %(message)s",
                    level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stderr)])

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110

PORT = 80
TIMEOUT = 10

def verdict(exit_code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    sys.exit(exit_code)



def info():
    verdict(OK, "vulns: 1\npublic_flag_description: Flag ID is page ID, flag is in page url\n")


def gen_login():
    ABC = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ$@()'._-"
    return "".join(random.choice(ABC) for i in range(random.randrange(6, 10)))


def gen_password():
    ABC = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ_@$.,';:"
    return "".join(random.choice(ABC) for i in range(random.randrange(10, 16)))


def gen_description():
    ABC = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    return "".join(random.choice(ABC) for i in range(random.randrange(2, 16)))

def gen_domain_segment():
    ABC = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ-"
    LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return random.choice(LETTERS) + ("".join(random.choice(ABC) for i in range(random.randrange(2, 10))))

def gen_path_segment():
    ABC = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ-~_."
    return "".join(random.choice(ABC) for i in range(random.randrange(1, 6)))


def call_register_or_login_user(session, base_url, user, password):
    register_data = {"login": user, "password": password}
    logging.info(f"call_register_or_login_user: POST /users: register_data {register_data}")
    r = session.post(urljoin(base_url, "/users"), data=json.dumps(register_data), verify=False, timeout=TIMEOUT)
    logging.info("request done")
    if r.status_code != 200:
        verdict(MUMBLE, "Can't register or login", "Unexpected register or login result on cred '%s': %d -> %s" %(register_data, r.status_code, r.text))

def call_get_pages(session, base_url):
    logging.info(f"call_get_pages: GET /pages")
    r = session.get(urljoin(base_url, "/pages"), verify=False, timeout=TIMEOUT)
    logging.info("request done")
    if r.status_code != 200:
        verdict(MUMBLE, "Can't GET pages", "Unexpected GET /pages result: %d -> %s" %(r.status_code, r.text))

    try:
        return r.json()
    except Exception:
        verdict(MUMBLE, "Bad json in GET pages result", "Bad json in GET /pages result: %s (exception %s)" % (r.text, traceback.format_exc()))

def call_get_page(session, base_url, page_id):
    logging.info(f"call_get_page: GET /pages/{page_id}")
    r = session.get(urljoin(base_url, f"/pages/{page_id}"), verify=False, timeout=TIMEOUT)
    logging.info("request done")
    if r.status_code != 200:
        verdict(MUMBLE, f"Can't GET page {page_id}", "Unexpected GET /pages/%d result: %d -> %s" %(page_id, r.status_code, r.text))

    try:
        return r.json()
    except Exception:
        verdict(MUMBLE, f"Bad json in GET page {page_id} result", "Bad json in GET /pages/%d result: %s (exception %s)" % (page_id, r.text, traceback.format_exc()))

def call_parse_page(session, base_url, page_url, text):
    quoted_page_url = quote_plus(page_url)
    logging.info(f"call_parse_page: POST /pages/?url={quoted_page_url}: {text}")
    r = session.post(urljoin(base_url, f"/pages/?url={quoted_page_url}"), data=text, verify=False, timeout=TIMEOUT)
    logging.info("request done")
    if r.status_code != 200:
        verdict(MUMBLE, "Can't POST page to parse", "Unexpected POST page to parse with url '%s' and text '%s' result: %d -> %s" %(page_url, text, r.status_code, r.text))
    try:
        return r.json()
    except Exception:
        verdict(MUMBLE, f"Bad json in POST page to parse result", "Bad json in POST page to parse with url '%s' and text '%s' result: '%s' (exception %s)" % (page_url, text, r.text, traceback.format_exc()))

def gen_page(page_url):
    links = []
    relative = gen_relative_url_upper()
    links.append(relative)
    if page_url[-1] == '/':
        links.append(page_url + relative)
    else:
        links.append(page_url + '/' + relative)

    for i in range(random.randrange(1, 8)):
        choice = random.random()
        if choice < 0.2:
            links.append(gen_absolute_url())
        elif choice < 0.4:
            links.append(gen_absolute_url_preserving_protocol())
        elif choice < 0.6:
            links.append(gen_relative_url_from_root())
        elif choice < 0.8:
            links.append(gen_relative_url_upper())
        else:
            if page_url[-1] == '/':
                links.append(gen_relative_url())
            else:
                links.append(gen_relative_url_from_root())

    random.shuffle(links)

    html = "<html>\n"
    for link in links:
        description = gen_description()
        html += f"<a href=\"{link}\">{description}</a>\n"

    html += "</html>"
    return (html, links)

def gen_absolute_url():
    proto = random.choice(["http", "https"])
    domain = ".".join(gen_domain_segment() for i in range(random.randrange(2,4)))
    path = "/".join(gen_path_segment() for i in range(random.randrange(0,5)))
    return f"{proto}://{domain}/{path}"

def gen_absolute_url_preserving_protocol():
    domain = ".".join(gen_domain_segment() for i in range(random.randrange(2,4)))
    path = "/".join(gen_path_segment() for i in range(random.randrange(0,5)))
    return f"//{domain}/{path}"

def gen_relative_url_from_root():
    path = "/".join(gen_path_segment() for i in range(random.randrange(0,5)))
    return f"/{path}"

def gen_relative_url_upper():
    upperLevels = "/".join(".." for i in range(random.randrange(1,5)))
    path = "/".join(gen_path_segment() for i in range(random.randrange(0,5)))
    return f"{upperLevels}/{path}"

def gen_relative_url():
    return "/".join(gen_path_segment() for i in range(random.randrange(0,5)))

def format_flag(flag):
    return "https://" + flag + ".linkextractor.ctf.hitb.org"


#TODO random small timeouts between requests
def check(host):
    linkextractor_base_url = f"http://{host}:{PORT}/"
    session = requests.Session()
    login = gen_login()
    password = gen_password()
    call_register_or_login_user(session, linkextractor_base_url, login, password)

    if random.random() < 0.65:
        call_register_or_login_user(session, linkextractor_base_url, login, password)

    logging.info(f"check: GET /users/whoami")
    r = session.get(urljoin(linkextractor_base_url, "/users/whoami"), verify=False, timeout=TIMEOUT)
    logging.info("request done")

    if r.status_code != 200 or r.text != login:
        verdict(MUMBLE, "Can't check user", "Unexpected whoami result: '%d' -> %s" %(r.status_code, r.text))

    verdict(OK)

def put(host, flag_id, flag, vuln):
    linkextractor_base_url = f"http://{host}:{PORT}/"
    session = requests.Session()
    login = gen_login()
    password = gen_password()

    call_register_or_login_user(session, linkextractor_base_url, login, password)

    if random.random() < 0.5:
        page_url = gen_absolute_url() + '/'
        (page_content, links) = gen_page(page_url)
        call_parse_page(session, linkextractor_base_url, page_url, page_content)

    page_url = format_flag(flag)
    (page_content, links) = gen_page(page_url)
    page_model = call_parse_page(session, linkextractor_base_url, page_url, page_content)

    try:
        parsed_pageId = int(page_model.get("pageId"))
        parsed_linksCount = int(page_model.get("linksCount"))
        parsed_pageUrl = page_model.get("pageUrl")

        if parsed_pageUrl != page_url:
            verdict(MUMBLE, f"Invalid page url returned in result model from parse page request", "Invalid page url returned in result model from parse page request '%s' with content '%s': %s" % (page_url, page_content, json.dumps(page_model)))

        if parsed_linksCount >= len(links) or parsed_linksCount < 0:
            verdict(MUMBLE, f"Invalid links count parsed from page", "Invalid links count parsed from page '%s' (parsed %d, sent %d) with content '%s': %s" % (page_url, parsed_linksCount, len(links), page_content, json.dumps(page_model)))
    except Exception:
        verdict(MUMBLE, f"Invalid model from successful result of parse page request", "Invalid model from successful result of parse page request '%s' with content '%s': %s (exception %s)" % (page_url, page_content, json.dumps(page_model), traceback.format_exc()))

    verdict(OK, json.dumps({"public_flag_id": str(parsed_pageId), "login": login, "password": password}))

def get(host, flag_id, flag, vuln):
    linkextractor_base_url = f"http://{host}:{PORT}/"
    session = requests.Session()

    try:
        info = json.loads(flag_id)
        page_id = int(info["public_flag_id"])
        login = info["login"]
        password = info["password"]
    except Exception:
        verdict(CHECKER_ERROR, "Bad flag id", "Bad flag_id: %s" % traceback.format_exc())

    call_register_or_login_user(session, linkextractor_base_url, login, password)

    page_model = call_get_page(session, linkextractor_base_url, page_id)
    if "pageUrl" not in page_model:
        verdict(MUMBLE, "Failed to get page", "Failed to get page %s: %s %s" % (page_id, login, password))

    page_url = page_model["pageUrl"]
    expected_page_url = format_flag(flag)

    if page_url != expected_page_url:
        verdict(CORRUPT, "Flag not found", "Flag not found expected %s, got %s" %(expected_page_url, page_url))

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
        verdict(CHECKER_ERROR, "Checker error", "Wrong command %s" % cmd)

    handler, args_count = CMD_MAPPING[cmd]
    if len(args) != args_count:
        verdict(CHECKER_ERROR, "Checker error", "Wrong args count for %s, expected %d got %d" % (cmd, args_count, len(args)))

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

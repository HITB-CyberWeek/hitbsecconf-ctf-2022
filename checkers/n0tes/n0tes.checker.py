#!/usr/bin/env python3

import sys
import traceback
import requests
import random
import string
import http
import json
from urllib.parse import urljoin
from lxml import etree
requests.packages.urllib3.disable_warnings()
from checker_helper import *

PORT = 443
VERIFY = False
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

    login_data = {"ReturnUrl": "/", "Username": user, "Password": password}
    session = requests.Session()

    trace("Trying to login using %s:%s" % (user, password))

    try:
        r = session.post(urljoin(n0tes_url, "/login"), data=login_data, timeout=TIMEOUT, verify=VERIFY)
    except (requests.exceptions.ConnectionError, ConnectionRefusedError, http.client.RemoteDisconnected) as e:
        return (DOWN, "Connection error", "Connection error during login: %s" % e, None, None)
    except requests.exceptions.Timeout as e:
        return (DOWN, "Timeout", "Timeout during login: %s" % e, None, None)

    if r.status_code != 200:
        return (MUMBLE, "Can't login", "Unexpected login result: '%d'" % r.status_code, None, None)

    try:
        parser = etree.HTMLParser()
        parser.feed(r.text)
        doc = parser.close()
    except Exception as e:
        return (MUMBLE, "Unexpected login result", "Can't parse result html: '%s'" % e, None, None)

    user_element = doc.xpath("//li[contains(@class, 'nav-item')]/span")
    if len(user_element) != 1:
        return (MUMBLE, "Unexpected login result", "Can't find username HTML element in '%s'" % r.text, None, None)

    actual_user = user_element[0].text.removesuffix(' | ')
    if actual_user != user:
        return (MUMBLE, "Unexpected login result", "Wrong username: '%s'" % actual_user, None, None)

    trace("Successfully logged in")

    return (OK, "", "", session, r.text)

def parse_note_element(html, note_title):
    try:
        parser = etree.HTMLParser()
        parser.feed(html)
        doc = parser.close()
    except Exception as e:
        return (MUMBLE, "Unexpected result", "Can't parse note list html: '%s'" % e, None)

    row_element = doc.xpath("//tbody/tr[td/a[contains(text(), '%s')]]" % note_title)

    if len(row_element) != 1:
        return (MUMBLE, "Unexpected result", "Can't find note '%s' in '%s'" % (note_title, html), None)

    return (OK, "", "", row_element[0])

def create_note(host, session, title, content):
    n0tes_url = f"https://{host}:{PORT}/"

    note_data = {"Title": title, "Content": content}
    try:
        r = session.post(urljoin(n0tes_url, "/notes"), data=note_data, timeout=TIMEOUT, verify=VERIFY)
    except (requests.exceptions.ConnectionError, ConnectionRefusedError, http.client.RemoteDisconnected) as e:
        return (DOWN, "Connection error", "Connection error during creating note: %s" % e)
    except requests.exceptions.Timeout as e:
        return (DOWN, "Timeout", "Timeout during creating note: %s" % e)

    if r.status_code != 200:
        return (MUMBLE, "Can't create note", "Unexpected status code when creating a note: '%d'" % r.status_code)

    (status, out, err, row_element) = parse_note_element(r.text, title)
    if status != OK:
        verdict(status, out, err)

    trace("Note with title '%s' successfully created" % title)

    return (OK, "", "")

def dom_element_to_str(element):
    return etree.tostring(element, pretty_print=True)

def get_note_content(host, session, note_row_element):
    n0tes_url = f"https://{host}:{PORT}/"

    link = note_row_element.xpath("./td/a/@href")
    if len(link) != 2:
        return (MUMBLE, "Unexpected result", "Can't find note link in: '%s'" % dom_element_to_str(note_row_element), None)

    try:
        r = session.get(urljoin(n0tes_url, link[0]), timeout=TIMEOUT, verify=VERIFY)
    except (requests.exceptions.ConnectionError, ConnectionRefusedError, http.client.RemoteDisconnected) as e:
        return (DOWN, "Connection error", "Connection error during reading a note: %s" % e, None)
    except requests.exceptions.Timeout as e:
        return (DOWN, "Timeout", "Timeout during reading a note: %s" % e, None)

    if r.status_code != 200:
        return (MUMBLE, "Can't create note", "Unexpected status code when reading a note: '%d'" % r.status_code, None)

    try:
        parser = etree.HTMLParser()
        parser.feed(r.text)
        doc = parser.close()
    except Exception as e:
        return (MUMBLE, "Unexpected result", "Can't parse note html: '%s'" % e, None)

    note_content = doc.xpath("//textarea[@id='Content']/text()")

    if len(note_content) != 1:
        return (MUMBLE, "Unexpected result", "Can't find note content in '%s'" % r.text, None)

    trace("Successfully got note content")

    return (OK, "", "", note_content[0].strip())

def put(args):
    if len(args) != 4:
        verdict(CHECKER_ERROR, "Checker error", "Wrong args count for put()")
    host, flag_id, flag, vuln = args
    trace("put(%s, %s, %s, %s)" % (host, flag_id, flag, vuln))

    note_title = flag_id
    user = get_random_string(5, 15)
    password = get_random_string(7, 20)

    (status, out, err, session, html) = login(host, user, password)
    if status != OK:
        verdict(status, out, err)

    (status, out, err) = create_note(host, session, note_title, flag)
    if status != OK:
        verdict(status, out, err)

    flag_id = json.dumps({"public_flag_id": note_title, "user": user, "password": password})
    verdict(OK, flag_id)

def get(args):
    if len(args) != 4:
        verdict(CHECKER_ERROR, "Checker error", "Wrong args count for get()")
    host, flag_id, flag_data, vuln = args
    trace("get(%s, %s, %s, %s)" % (host, flag_id, flag_data, vuln))

    info = json.loads(flag_id)
    user = info['user']
    password = info['password']
    note_title = info['public_flag_id']

    (status, out, err, session, html) = login(host, user, password)
    if status != OK:
        verdict(status, out, err)

    (status, out, err, row_element) = parse_note_element(html, note_title)
    if status != OK:
        verdict(status, out, err)

    (status, out, err, note_content) = get_note_content(host, session, row_element)
    if status != OK:
        verdict(status, out, err)

    if note_content != flag_data:
        verdict(CORRUPT, "Can't find flag in note", "Can't find flag in note, actual flag: '%s'" % note_content)

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

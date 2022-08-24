#!/usr/bin/env python3

import sys
import os
import socket
import hashlib
import random
import time
import json
import traceback

import requests

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110

TIMEOUT = 10

ABC = "".join(chr(i) for i in range(1, 127) if chr(i) != "'")

CHECKER_DIRECT_CONNECT = os.environ.get("CHECKER_DIRECT_CONNECT")


def gen_rand_string(l=12):
    ABC = "abcdefghijklmnopqrstuvwxyz"
    return "".join(random.choice(ABC) for i in range(l))



def verdict(exit_code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    sys.exit(exit_code)


def info():
    verdict(OK, "vulns: 1\npublic_flag_description: Flag ID is user ID, flag is in picture\n")


def encrypt(s):
    N = 0xb3aefb131cf5485561fe3e3408bbc7d466ee79573efb3a3a1333f84110959cb256b15ebec238356995408d42d7421cc25d4b7cb3b3fd015153eee433b66cf559fd194cc5e674b3f1597db275eede5de63abfa4b7067701474f87c947af70470d57a61237a22a73318e96edde0b777c7a4eb570a63bb47355f5db3d223ac99dec76ce338fcb2e65489d504f321307bcc77a3c62d1e73632313ae15b673fc4f946a2c0bb05201007cb54c2dad05a56489ee5f1b5763e1b4413e3bfff954374997e89743cd7ff1cf054fd5268852c2af8eadc657e57b860e2d2e17a9c7cb3222b77c7724bb420838aebdfc91526efd754bd4f158144627e86a3d705274ea0bdbf0f
    E = 65537

    msg_as_num = 0
    for i in range(0, len(s)):
        msg_as_num <<= 8
        msg_as_num += ord(s[i])

    encrypted = pow(msg_as_num, E, N)
    return "%x" % encrypted


def call_api(s, ip, params):
    data = {"p": encrypt(json.dumps(params))}
    if CHECKER_DIRECT_CONNECT == "1":
        resp = s.post(f"http://{ip}/api.php", data=data, timeout=TIMEOUT)
    else:
        resp = s.post(f"https://{ip}/api.php", data=data, timeout=TIMEOUT)

    if resp.status_code == 502:
        verdict(DOWN, "Proxy returned 502", "Proxy returned 502: %s" % resp.text)

    try:
        return resp.json()
    except Exception:
        verdict(MUMBLE, "Bad json in ans", "Bad json in ans: %s" % resp.text)


def gen_login():
    ABC = "abcdefghijklmnopqrstuvwxyz01234567890!@#$%^&*(){}'<>ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    name = "".join(random.choice(ABC) for i in range(random.randrange(6, 10)))

    if random.random() < 0.01:
        return name + ";select id from get_users()"
    if random.random() < 0.01:
        return name + " union select id from users -- "
    if random.random() < 0.01:
        return name + " union select add_action(id, 39) -- "
    if random.random() < 0.01:
        return name + ";select add_action(id, 39) "
    return name


def gen_password():
    FLAG_LETTERS = "0123456789ABCDEFG"
    return "".join(random.choice(FLAG_LETTERS) for i in range(31)) + "="


def gen_color():
    return random.choice(["#000000", "#ff0000", "#00ff00", "#0000ff", "#800080"])


def gen_text():
    return random.choice([gen_password(), gen_login().replace("'", ""), gen_color(), "hello", "cccc", "#121212121"])


def gen_action():
    tool = random.choice(["line", "point", "rect", "circle", "text"])

    x = random.randint(0, 500)
    y = random.randint(0, 500)

    action = {
        "color": gen_color(),
        "tool": tool,
        "params": {
            "x": x,
            "y": y
        }
    }

    if tool == "circle":
        action["params"]["r"] = random.randint(10, 100)
    elif tool == "line":
        action["params"]["x2"] = x + random.randint(-50, 50)
        action["params"]["y2"] = y + random.randint(-50, 50)
    elif tool == "rect":
        action["params"]["w"] = random.randint(20, 100)
        action["params"]["h"] = random.randint(20, 100)
    elif tool == "text":
        action["params"]["t"] = gen_text()

    return action


def check(host):
    login = gen_login()
    password = gen_password()

    s = requests.session()

    reg_resp = call_api(s, host, {"action": "register", "login": login, "password": password})

    if "userid" not in reg_resp:
        verdict(MUMBLE, "Failed to register a new user", "Failed to register: %s %s" % (login, password))


    userid = reg_resp["userid"]

    actions = []

    for i in range(random.randrange(1, 4)):
        actions.append(gen_action())


    for action in actions:
        params = {"action":"add_action", "action_data":action}
        reg_resp = call_api(s, host, params)

        if reg_resp.get("result") != "ok":
            verdict(MUMBLE, "Failed to add an action", "Failed to add_action: %s %s" % (params, reg_resp))


    actions_resp = call_api(s, host, {"action": "get_actions"})
    if actions_resp.get("result") != "ok":
        verdict(MUMBLE, "Failed to get actions", "Failed to get_actions: %s" % (actions_resp, ))

    recorded_actions = actions_resp.get("actions", [])

    if len(actions) != len(recorded_actions):
        verdict(MUMBLE, "Some actions were lost", "Some actions were lost: %s" % (len(actions), len(recorded_actions)))


    for our, their in zip(actions, recorded_actions):
        try:
            their = json.loads(their.get("action", {}))
        except Exception:
            verdict(MUMBLE, "Some actions are corrupted", "Some actions are corrupted, probably bad json: %s" % (their, ))

        if our != their:
            verdict(MUMBLE, "Some actions are corrupted", "Some actions are corrupted: %s vs %s" % (our, their))


    verdict(OK)


def put(host, flag_id, flag, vuln):
    login = gen_login()
    password = gen_password()

    s = requests.session()

    reg_resp = call_api(s, host, {"action": "register", "login": login, "password": password})

    if "userid" not in reg_resp:
        verdict(MUMBLE, "Failed to register a new user", "Failed to register: %s %s" % (login, password))


    userid = reg_resp["userid"]


    params = {"action":"add_action", "action_data": {
            "color": gen_color(),
            "tool": "text",
            "params": {
                "x": random.randrange(0, 500),
                "y": random.randrange(0, 500),
                "t": flag
            }
    }}
    reg_resp = call_api(s, host, params)


    if reg_resp.get("result") != "ok":
        verdict(MUMBLE, "Failed to add an action", "Failed to add_action: %s %s" % (params, reg_resp))


    verdict(OK, json.dumps({"public_flag_id": str(userid), "login": login, "password": password}))


def get(host, flag_id, flag, vuln):

    s = requests.session()
    try:
        info = json.loads(flag_id)
        login = info["login"]
        password = info["password"]
    except Exception:
        verdict(CHECKER_ERROR, "Bad flag id", "Bad flag_id: %s" % traceback.format_exc())

    resp = call_api(s, host, {"action": "login", "login": login, "password": password})

    if "userid" not in resp:
        verdict(MUMBLE, "Failed to login user", "Failed to login: %s %s" % (login, password))

    userid = resp["userid"]


    actions_resp = call_api(s, host, {"action": "get_actions"})
    if actions_resp.get("result") != "ok":
        verdict(MUMBLE, "Failed to get actions", "Failed to get_actions: %s" % (actions_resp, ))

    actions = actions_resp.get("actions", [])

    if not actions:
        verdict(MUMBLE, "Failed to get actions", "No actions: %s" % (actions, ))

    try:
        action = json.loads(actions[0].get("action", '{}'))
        stored_flag = action.get("params", {}).get("t", "")
    except Exception:
        verdict(MUMBLE, "Bad answer", "Probably bad json: %s" % (actions,))

    if stored_flag != flag:
        verdict(CORRUPT, "No such flags",
            "No such flag %s, stored_flag %s" % (flag, stored_flag))


    verdict(OK, flag_id)


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

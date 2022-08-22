#!/usr/bin/env python3
import json
import logging
import random
import select
import socket
import string
import time

import sys
import traceback

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110


PORT = 4444
CMD_DELAY = 5
RECV_BUFFER = 32 * 1024
CONNECT_TIMEOUT = 15
CHARSET = string.ascii_lowercase + string.digits


def random_str(length):
    return ''.join(random.choice(CHARSET) for i in range(length))


class Client:
    def __init__(self, host):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(CONNECT_TIMEOUT)
        logging.info("Connecting to %s:%d ...", host, PORT)
        self.s.connect((host, PORT))
        logging.info("Connected.")
        self._recv("Command ==> ")
        self._last_cmd_time = 0

    def _recv(self, end, timeout=10):
        if isinstance(end, str):
            end = [end]
        start = time.monotonic()
        response = ""
        while time.monotonic() < start + timeout:
            select_timeout = min(float(timeout), start + timeout - time.monotonic())
            if select_timeout < 0:
                select_timeout = 0.1  # Last chance!
            ready = select.select([self.s], [], [], select_timeout)
            if not ready[0]:
                raise Exception("No expected response from remote side in {} sec. Actual response: {!r}".format(
                    timeout, response))
            response += self.s.recv(RECV_BUFFER).decode(errors="ignore")

            if all(e in response for e in end):
                logging.info("Received <<< %r.", response)
                return response

    def _send(self, line):
        logging.info("Sending  >>> %r.", line)
        data = (line + "\n").encode()
        self.s.sendall(data)

    def _command(self, cmd):
        self._ensure_command_delay()
        self._send(cmd)
        self._update_command_time()

    def _ensure_command_delay(self):
        left = self._last_cmd_time + CMD_DELAY - time.monotonic()
        if left > 0:
            logging.info("Sleeping %.2f sec before next command...", left)
            time.sleep(left)

    def _update_command_time(self):
        self._last_cmd_time = time.monotonic()

    def register(self, user, password):
        start = time.monotonic()
        logging.info("Registering %r with password %r ...", user, password)

        self._command("REGISTER")

        self._recv("Username ==> ")
        self._send(user)

        self._recv("Password ==>")
        self._send(password)

        self._recv(["OK.", "Command ==> "])

        logging.info("Registration succeeded (%.2f sec).", time.monotonic() - start)

    def login(self, user, password):
        start = time.monotonic()
        logging.info("Logging in as %r with password %r ...", user, password)

        self._command("LOGIN")

        self._recv("Username ==> ")
        self._send(user)

        self._recv("Password ==>")
        self._send(password)

        self._recv(["OK.", "Command ==> "])

        logging.info("Login succeeded (%.2f sec).", time.monotonic() - start)

    def store(self, data):
        start = time.monotonic()
        logging.info("Storing %r ...", data)

        self._command("STORE")

        self._recv("Data ==> ")
        self._send(data)

        self._recv(["OK.", "Command ==> "])

        logging.info("Store succeeded (%.2f sec).", time.monotonic() - start)

    def retrieve(self):
        start = time.monotonic()
        logging.info("Retrieving ...")

        self._command("RETRIEVE")
        data = self._recv("Command ==> ").split("\n")[0]

        logging.info("Retrieve succeeded (%.2f sec).", time.monotonic() - start)
        return data

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.s.close()


def gen_str(charset: str, length: int):
    return "".join(random.choices(charset, k=length))


def verdict(exit_code, public="", private=""):
    if private:
        logging.error(private)
    if public:
        logging.info("Public verdict: %r.", public)
        print(public)
    logging.info("Exit with code: %d.", exit_code)
    sys.exit(exit_code)


def info():
    verdict(OK, "\n".join([
        "vulns: 1",
        "public_flag_description: Flag ID is Username, flag is user's private info."
    ]))


def check(host):
    verdict(OK)


def put(host, flag_id, flag, vuln):
    user = random_str(8)
    password = random_str(12)

    client = Client(host)
    client.register(user, password)
    client.login(user, password)
    client.store(flag)

    json_flag_id = json.dumps({
        "public_flag_id": user,
        "password": password,
    }).replace(" ", "")
    verdict(OK, json_flag_id)


def get(host, flag_id, flag, vuln):
    json_flag_id = json.loads(flag_id)

    user = json_flag_id["public_flag_id"]
    password = json_flag_id["password"]

    client = Client(host)
    client.login(user, password)
    flag2 = client.retrieve()

    if flag not in flag2:
        verdict(MUMBLE, public="Flag not found")

    verdict(OK, "Flag found")


class ProtocolViolationError(Exception):
    pass


def main(args):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    cmd_mapping = {
        "info":     (info, 0),
        "check":    (check, 1),
        "put":      (put, 4),
        "get":      (get, 4),
    }

    if not args:
        verdict(CHECKER_ERROR, "No args", "No args")

    cmd, args = args[0], args[1:]
    if cmd not in cmd_mapping:
        verdict(CHECKER_ERROR, "Checker error", "Wrong command %s" % cmd)

    handler, args_count = cmd_mapping[cmd]
    if len(args) != args_count:
        verdict(CHECKER_ERROR, "Checker error", "Wrong args count for %s (%d, expected: %d)" %
                (cmd, len(args), args_count))

    try:
        handler(*args)
    except ProtocolViolationError as E:
        verdict(MUMBLE, "Protocol violation", "Protocol violation: %s" % traceback.format_exc())
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

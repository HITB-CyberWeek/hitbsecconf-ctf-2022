#!/usr/bin/env python3

import sys
from urllib import request
import requests
import http.client

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110

class VerdictError(Exception):
    def __init__(self, exit_code, public="", private=""):
        self.exit_code = exit_code
        self.public = public
        self.private = private


def checker_action(fn):
    def wrapper(*args, **kwarg):
        try:
            return fn(*args, **kwarg)
        except VerdictError as e:
            verdict(e.exit_code, e.public, e.private)
        except (requests.exceptions.ConnectionError, ConnectionRefusedError, http.client.RemoteDisconnected) as e:
            verdict(DOWN, "Connection error", "Connection error during login: %s" % e)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code // 100 == 4:  # 4xx
                verdict(CORRUPT, "HTTP error", "HTTPError: %s" % e)
            verdict(DOWN, "HTTP error", "HTTPError: %s" % e)  # 5xx
        except requests.exceptions.Timeout as e:
            verdict(DOWN, "Timeout", "Timeout during login: %s" % e)
        except requests.exceptions.JSONDecodeError as e:
            verdict(MUMBLE, "JSON expected", "JSON decode while request: %s" % e)
        except Exception as e:
            verdict(CHECKER_ERROR, "Checker err", f"Unknown exception:{e}")
    return wrapper


def trace(message):
    print(message, file=sys.stderr)


def verdict(exit_code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    sys.exit(exit_code)

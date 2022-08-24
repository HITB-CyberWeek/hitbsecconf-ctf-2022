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
            verdict(DOWN, "Connection error", "Connection error: %s" % e)
        except requests.exceptions.HTTPError as e:
            err = f"HTTP error! URL:{e.response.url}; http status:{e.response.status_code}"
            err_private = f"HTTPError:{e}"
            if e.response.status_code // 100 == 4:  # 4xx
                verdict(MUMBLE, err, err_private)
            verdict(DOWN, err, err_private)  # 5xx
        except requests.exceptions.Timeout as e:
            verdict(DOWN, f"Timeout! URL:{e.response.url}", "Timeout: %s" % e)
        except requests.exceptions.JSONDecodeError as e:
            verdict(MUMBLE, f"JSON expected! URL:{e.response.url}", "JSON decode while request: %s" % e)
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

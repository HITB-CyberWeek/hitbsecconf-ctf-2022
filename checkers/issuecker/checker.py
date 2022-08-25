#!/usr/bin/env python3
import base64
import json
import sys
import traceback

import requests
from gornilo import (
    CheckRequest,
    Verdict,
    PutRequest,
    GetRequest,
    VulnChecker,
    NewChecker,
)

import generators


checker = NewChecker()


URL_TEMPLATE = 'http://{host}/app.cgi/{method}'


def make_request(host, method, data, cookies=None):
    kwargs = {'json': data}
    if cookies:
        kwargs['cookies'] = cookies

    r = requests.post(
        URL_TEMPLATE.format(host=host, method=method),
        **kwargs
    )
    print("REQUEST: ", host, method, data, cookies)
    print("RESPONSE: ", r.content)

    r.raise_for_status()
    content = json.loads(r.content) if r.content else None
    return r.cookies, content


class ErrorChecker:
    def __init__(self):
        self.verdict = Verdict.OK()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is None:
            return True

        if exc_type:
            print(exc_type)
            print(exc_value.__dict__)

            traceback.print_tb(exc_traceback, file=sys.stdout)

        if isinstance(exc_value, (json.decoder.JSONDecodeError, KeyError)):
            self.verdict = Verdict.MUMBLE('Incorrect json: {} {}'.format(exc_type, exc_value))
            return True

        if isinstance(exc_value, (requests.exceptions.ConnectionError,)):
            self.verdict = Verdict.DOWN('Connection error: {}'.format(exc_value))
            return True

        if isinstance(exc_value, (requests.exceptions.HTTPError,)):
            if exc_value.response.status_code // 100 == 5:
                self.verdict = Verdict.DOWN(str(exc_value))
            else:
                self.verdict = Verdict.MUMBLE('Incorrect status code: {}'.format(exc_value))
            return True

        self.verdict = Verdict.CHECKER_ERROR('Checker error')
        return True


@checker.define_check
async def check_service(request: CheckRequest) -> Verdict:
    return Verdict.OK()


@checker.define_vuln('Flag ID is a ticket ID')
class CryptoChecker(VulnChecker):
    @staticmethod
    def put(request: PutRequest) -> Verdict:
        with ErrorChecker() as ec:
            username = generators.gen_string(3, 20)
            password = generators.gen_string(3, 20)
            data = {'username': username, 'password': password}
            cookies, _ = make_request(
                request.hostname, 'register', data=data
            )

            queue_name = generators.gen_queue_name()

            _, resp_data = make_request(
                request.hostname,
                'add_queue',
                cookies=cookies,
                data={'queue_name': queue_name},
            )

            if not isinstance(resp_data, dict):
                return Verdict.MUMBLE("Incorrect resp_data type: {}".format(type(resp_data)))

            if not isinstance(resp_data["queue_key"], str):
                return Verdict.MUMBLE("Incorrect {} type: {}".format("queue_key", type(resp_data["queue_key"])))

            if not isinstance(resp_data["queue_id"], int):
                return Verdict.MUMBLE("Incorrect {} type: {}".format("queue_id", type(resp_data["queue_id"])))

            queue_id = resp_data['queue_id']
            queue_key = resp_data['queue_key']

            ticket_title = base64.b64encode(
                ('title: ' + generators.gen_string(3, 50)).encode()
            ).decode()
            ticket_description = base64.b64encode(
                ('DESCRIPTION: ' + generators.gen_description() + '\n\n' + request.flag).encode()
            ).decode()

            _, resp_data = make_request(
                request.hostname,
                'add_ticket',
                cookies=cookies,
                data={
                    'queue_id': queue_id,
                    'title': ticket_title,
                    'description': ticket_description,
                },
            )

            if not isinstance(resp_data, dict):
                return Verdict.MUMBLE("Incorrect resp_data type: {}".format(type(resp_data)))

            ticket_id = resp_data['ticket_id']
            flag_id = json.dumps(
                {
                    'username': username,
                    'password': password,
                    'queue_name': queue_name,
                    'queue_id': queue_id,
                    'queue_key': queue_key,
                    'ticket_title': ticket_title,
                    'ticket_description': ticket_description,
                    'ticket_id': ticket_id,
                }
            )

            ec.verdict = Verdict.OK_WITH_FLAG_ID(ticket_id, flag_id)
        return ec.verdict

    @staticmethod
    def get(request: GetRequest) -> Verdict:
        with ErrorChecker() as ec:
            flag_id_json = json.loads(request.flag_id)

            cookies, _ = make_request(request.hostname, 'login', data={
                'username': flag_id_json['username'],
                'password': flag_id_json['password'],
            })

            data = {
                'queue_id': flag_id_json['queue_id'],
                'ticket_id': flag_id_json['ticket_id'],
                'title': flag_id_json['ticket_title'],
                'description': flag_id_json['ticket_description'],
            }
            _, res_data = make_request(request.hostname, 'find_tickets', data, cookies=cookies)

            if not isinstance(res_data, list):
                return Verdict.MUMBLE('Wrong response data type')

            if len(res_data) != 1:
                return Verdict.CORRUPT('Can not find related ticket')

            real_ticket = res_data[0]
            if not isinstance(real_ticket, dict):
                return Verdict.MUMBLE('Wrong ticket data type')

            if res_data[0]['title'] != flag_id_json['ticket_title']:
                return Verdict.CORRUPT('Incorrect ticket title')

            if res_data[0]['description'] != flag_id_json['ticket_description']:
                return Verdict.CORRUPT('Incorrect ticket description')

            actual_flag = base64.b64decode(res_data[0]['description'].encode()).decode().split()[-1].strip()
            if actual_flag != request.flag:
                return Verdict.CORRUPT('Incorrect flag')

        return ec.verdict


if __name__ == '__main__':
    checker.run()

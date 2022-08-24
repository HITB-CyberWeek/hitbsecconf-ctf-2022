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


URL_TEMPLATE = 'http://{host}/cgi-bin/app/{method}'


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
        if exc_type:
            print(exc_type)
            print(exc_value.__dict__)
            traceback.print_tb(exc_traceback, file=sys.stdout)

        self.verdict = Verdict.CHECKER_ERROR('error')
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

            queue_name = generators.gen_string(3, 40)

            _, resp_data = make_request(
                request.hostname,
                'add_queue',
                cookies=cookies,
                data={'queue_name': queue_name},
            )
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

            print("resp data: {}".format(res_data))
            if not isinstance(res_data, list):
                return Verdict.MUMBLE('Wrong resp data type')

            if len(res_data) != 1:
                return Verdict.CORRUPT('Can not find related ticket')

            real_ticket = res_data[0]
            if not isinstance(real_ticket, dict):
                return Verdict.MUMBLE('Wrong ticket data type')

            if res_data[0]['title'] != flag_id_json['ticket_title']:
                return Verdict.CORRUPT('Incorrect ticket title')

            if res_data[0]['description'] != flag_id_json['ticket_description']:
                return Verdict.CORRUPT('Incorrect ticket description')

        return ec.verdict


if __name__ == '__main__':
    checker.run()
# print(generators.gen_description())

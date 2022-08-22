#!/usr/bin/python3

import asyncio

PORT_TOO_MANY_REQUESTS = 429

PORT_USE_PROXY = 20

MSG_TOO_MANY_REQUESTS = """429 Too many requests!

This CTF service has a limitation for request count from the team.
Your team has made too many requests, and now service will return this message for some time. Take a break!
"""

MSG_USE_PROXY = """Use a proxy!

Direct connections to other teams' services are prohibited.
Please, use a proxy located on <service-name>.team<team-id>.ctf.hitb.org
"""


async def accept_too_many_requests(reader, writer):
    try:
        writer.write(MSG_TOO_MANY_REQUESTS.encode())
    finally:
        writer.close()


async def accept_use_proxy(reader, writer):
    try:
        writer.write(MSG_USE_PROXY.encode())
    finally:
        writer.close()


def main():
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.start_server(accept_too_many_requests, host="0.0.0.0", port=PORT_TOO_MANY_REQUESTS),
        asyncio.start_server(accept_use_proxy, host="0.0.0.0", port=PORT_USE_PROXY),
    ]
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.run_forever()


if __name__ == '__main__':
    main()

#!/usr/bin/python3

import asyncio

PORT = 429

MSG = """429 Too many requests!

This CTF service has a limitation for request count from the team.
Your team has made too many requests, and now service will return this message for some time. Take a break!
"""


async def accept_client(reader, writer):
    try:
        writer.write(MSG.encode())
    finally:
        writer.close()


def main():
    loop = asyncio.get_event_loop()
    f = asyncio.start_server(accept_client, host="0.0.0.0", port=PORT)
    loop.run_until_complete(f)
    loop.run_forever()


if __name__ == '__main__':
    main()

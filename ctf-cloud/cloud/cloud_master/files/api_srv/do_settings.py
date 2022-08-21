import json
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(SCRIPT_DIR, "do_vulnimages.json")) as vulnimages_file:
    vulnimages = json.load(vulnimages_file)

CLOUD_FOR_NEW_VMS = "hitb"
CLOUD_FOR_DNS = "hitb"
DOMAIN = "cloud.ctf.hitb.org"

CLOUDS = {
    "hitb": {
        "region": "ams3",
        "router_image": 114818893,
        "router_ssh_keys": [27173548, 35847579],
        "vulnimages": vulnimages,
        "vulnimage_ssh_keys": [27173548],
        "sizes": {
            "default": "c-2",
            "router": "s-2vcpu-4gb",
            "empty": "s-8vcpu-16gb",
            "sh": "c-4",
            "crs": "s-8vcpu-16gb",
        }
    },
    "bay": {
        "router_image": 0,
        "vulnimages": {3: 0},
        "ssh_keys": [0, 0]
    }
}

DO_SSH_ID_FILE = "do_deploy_key"


import pathlib

from environs import Env

env = Env()
env.read_env()  # read .env file, if it exists


DO_API_TOKEN = env.str("DO_API_TOKEN")

wildcard_ctf_hitb_org = pathlib.Path("../../certificates/team1.ctf.hitb.org/")
team500_ctf_hitb_org = pathlib.Path("../../certificates/team500.ctf.hitb.org/")
admin_n0tes_ctf_hitb_org = pathlib.Path("../../certificates/admin.n0tes.ctf.hitb.org/")
n0tes = pathlib.Path("../checkers/n0tes/")
PROXY_CERTIFICATES = {
    "wildcard.ctf.hitb.org": (wildcard_ctf_hitb_org / "fullchain.pem", wildcard_ctf_hitb_org / "privkey.pem"),
    "team500.ctf.hitb.org": (team500_ctf_hitb_org / "fullchain.pem", team500_ctf_hitb_org / "privkey.pem"),
    "n0tes_client": (n0tes / "n0tes-admin.crt", n0tes / "n0tes-admin.key"),
    "admin.n0tes.ctf.hitb.org": (admin_n0tes_ctf_hitb_org / "fullchain.pem", admin_n0tes_ctf_hitb_org / "privkey.pem"),
}
PROXY_SSH_KEY = env.path("PROXY_SSH_KEY", "../ctf-cloud/cloud/cloud_master/files/api_srv/do_deploy_key")
PROXY_SSH_PORT = env.int("PROXY_SSH_PORT", 2222)
PROXY_SSH_USERNAME = env.str("PROXY_SSH_USERNAME", "root")

BASE_TEAM_NETWORK = env.str("BASE_TEAM_NETWORK", "10.60.0.0/14")
TEAM_NETWORK_MASK = env.int("TEAM_NETWORK_MASK", 24)

DNS_ZONE = env.str("DNS_ZONE", "ctf.hitb.org")

PROXY_HOSTS = {
    1: "10.80.1.2",
    2: "10.80.2.2",
}

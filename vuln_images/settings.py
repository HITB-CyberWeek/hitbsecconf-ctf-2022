import pathlib

from environs import Env

env = Env()
env.read_env()  # read .env file, if it exists


DO_API_TOKEN = env.str("DO_API_TOKEN")

wildcard_ctf_hitb_org = pathlib.Path("../../certificates/team1.ctf.hitb.org/")
team500_ctf_hitb_org = pathlib.Path("../../certificates/team500.ctf.hitb.org/")
PROXY_CERTIFICATES = {
    "wildcard.ctf.hitb.org": (wildcard_ctf_hitb_org / "fullchain.pem", wildcard_ctf_hitb_org / "privkey.pem"),
    "team500.ctf.hitb.org": (team500_ctf_hitb_org / "fullchain.pem", team500_ctf_hitb_org / "privkey.pem"),
}
PROXY_HOSTS = {
    500: "10.81.244.2"
}
PROXY_SSH_KEY = env.path("PROXY_SSH_KEY", "../ctf-cloud/cloud/cloud_master/files/api_srv/do_deploy_key")
PROXY_SSH_PORT = env.int("PROXY_SSH_PORT", 2222)
PROXY_SSH_USERNAME = env.str("PROXY_SSH_USERNAME", "root")

BASE_TEAM_NETWORK = env.str("BASE_TEAM_NETWORK", "10.60.0.0/14")
TEAM_NETWORK_MASK = env.int("TEAM_NETWORK_MASK", 24)

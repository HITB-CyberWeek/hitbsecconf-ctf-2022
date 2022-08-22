## Tool 1: Image builder 

This tool builds DigitalOcean's image for every service
with respect of its deployment config (aka `deploy.yaml`).

### How it works

Basically, this script runs the packer tool (https://packer.io/) with DigitalOcean builder,
which launches a VM (aka Droplet) in DigitalOcean, installs updates, deploys your service,
shutdowns it and creates a snapshot for further copying.

## Tool 2: Proxy deployer 

This tool deploys HTTP-proxy to team's router
with respect of service's deployment config (aka `deploy.yaml`).

### How it works

Basically, this script copies some nginx configs and run some commands
on teams routers. You can see an example of configs in `nginx/`.

## Example of deploy.yaml

Write your own `deploy.yaml` and put it into the service folder (in `services/<service-name>`).

```yaml
# Just a version of the file format. For now, it's always 1.
version: 1

# Name of the service. Required field. Available as $SERVICE in some places below.
service: test

# Name of the user. Specify it if you want to create a user and a home directory.
# Most probably, you want.
# Available as $USERNAME in some places below.
username: test

# Scripts/commands for running on different build stages.
# If your build instructions are complicated, extract them into a separate file, and
# run it as a script here, i.e.:
#
# scripts:
#   build_outside_vm: ./build.sh
# 
# Moreover, you should run your build scripts inside of the prepared docker environment, because
# we don't guarantee that compilers or other tools will be installed in the 
# building environment.
#
# All paths here are relative to the folder contained deploy.yaml, so you can write 
# ./build.sh it build.sh is in the same folder as deploy.yaml.
scripts:
  # First command: build_outside_vm
  # This command will be run outside the target VM. Here you can compile you code, 
  # if you don't want to deploy source codes to VM.
  build_outside_vm: make -j4
  # Second command: build_inside_vm
  # This command will be run inside the target VM. DON'T RUN YOUR SERVICE HERE,
  # only build it. Most probably, it will be single `docker compose build --pull` command here.
  build_inside_vm: docker compose -f /home/$USERNAME/docker-compose.yaml build --pull
  # Third command: start_one
  # As far as your docker containers should be restarted by docker daemon itself 
  # (don't forget to specify "restart: unless-stopped" in your docker-compose.yaml!),
  # here we need a command which will be run only once, at first boot of team's VM.
  start_once: docker compose -f /home/$USERNAME/docker-compose.yaml up -d

# Here you have to specify files which we need to deliver to the VM.
# You can upload a single file or a complete directory. 
files:
  # Will copy all files from ./deploy/ folder to /home/$SERVICE/.
  - source: ./deploy/
    destination: /home/$USERNAME
  # Will copy all files from ./deploy/ folder to /home/$SERVICE/deploy/
  # (because there is no trailing slash in source! See https://www.packer.io/docs/provisioners/file#directory-uploads
  # for details).
  - source: ./deploy
    destination: /home/$USERNAME
  # Will copy different files into one destination.
  - sources:
      - docker-compose.yaml
      - Dockerfile
      - service.py
    destination: /home/$USERNAME

# Here you can specify proxies list. In common cases you should have
# only one HTTPS proxy.
proxies:  
    # Any name of the proxy, should be unique across all proxies in your service.   
  - name: main
    listener:
      # Protocol for the proxy. Now only "http" and "tcp" are supported. 
      # If you want to deploy HTTPS proxy, specify "http" here and certificate below.
      protocol: http
      # [HTTP only] Hostname for the proxy. We use asterisk here, because real domain is test.team42.ctf.hitb.org
      # Optional. If not specified, "$SERVICE.*" will be used.      
      hostname: test.*
      # [HTTP Only] Certificate name (as specified in PROXY_CERTIFICATES in settings.py).
      # Optional. If not specified, only HTTP proxy will be deployed, without TLS. 
      # Attention! Omit this option only if you have really strong reasons to disable TLS!
      certificate: wildcard.ctf.hitb.org
      # [HTTP Only] Client certificate name (as specified in PROXY_CERTIFICATES in settings.py).
      # Optional. Specify only if you want to check client certificate on
      # the proxy side.
      client_certificate: n0tes_client
      # [TCP only] Amount of simultaneous connections accepted by the proxy FROM ONE TEAM.
      # Optional. Default is unlimited. 
      tcp_simultaneous_connections: 1
      # [HTTP only] Make a server default for incoming requests.
      # Optional and dangerous! Use only if you understand what you do. Default value is false.
      # Nginx can not handle multiple "default" servers.
      default: false
    upstream:
      # Host's index on team's network where proxy should send all requests.
      # I.e, if service is deployed on 10.60.10.3, specify 3 here.
      host_index: 3
      # Port of the service on upstream host.
      port: 80
      # Protocol for the upstream. "tcp", "http" or "https"
      # Optional. Default: "http" for HTTP proxies, "tcp" for TCP proxies
      protocol: http
      # [HTTP only] Client certificate name (as specified in PROXY_CERTIFICATES in settings.py)
      # to be used for upstream requests.
      # Optional. Specify only if your backend checks client certificate.
      client_certificate: n0tes_client
    # List of limits (can be empty).
    limits:
      # Only "team" is supported as a source now.
      # It means that limit will be applied per-/24 network.
      - source: team
        # [HTTP only] You can create different limits for different locations.
        location: /
        # Limit. 
        # 
        # For HTTP proxies: limit in terms of nginx's limit_req_zone directive: 
        # http://nginx.org/en/docs/http/ngx_http_limit_req_module.html#limit_req_zone.
        # 
        # For TCP proxies limit in terms of iptables hashlimit's option:
        # https://fossies.org/linux/iptables/extensions/libxt_hashlimit.man
        limit: 5r/m  # "5/minute" for TCP proxies
        # Burst.
        # 
        # For HTTP proxies: Burst in terms of nginx's limit_req directive:
        # http://nginx.org/en/docs/http/ngx_http_limit_req_module.html#limit_req.
        # Optional. If specified, it will be applied together "nodelay" option.
        #
        # For TCP proxies: Burst in terms of iptables hashlimit's option −−hashlimit−burst:
        # https://fossies.org/linux/iptables/extensions/libxt_hashlimit.man
        # Optional. Default value is 5
        burst: 10
    # List of DNS records for proxies (can be empty). 
    # Records will be created in team's DNS zone, i.e. test.team42.ctf.hitb.org. 
    dns_records:
      - test
```

## How to run ./build_image.py

1. Install packer 1.7.0 or higher: https://learn.hashicorp.com/tutorials/packer/get-started-install-cli#
2. Install Python 3.8 or higher
3. Install requirements: `pip install -Ur requirements.txt`
4. Get the API Token for Digital Ocean: https://cloud.digitalocean.com/settings/applications
5. Run `DO_API_TOKEN=<...> python3 build_image.py ../services/<service-name>/deploy.yaml`

You can also put you `DO_API_TOKEN` into `.env` file in following format:
```dotenv
DO_API_TOKEN=<...>
```

The tool will also update file with id's of snaphots for cloud infrastructure 
(`ctf-cloud/cloud/cloud_master/files/api_srv/do_vulnimages.json`),
don't forget to commit and deploy it.

## How to run ./deploy_proxies.py

1. Install Python 3.8 or higher
2. Install requirements: `pip install -Ur requirements.txt`
3. Fill `settings.py`, specify:
   - `PROXY_HOSTS` — map of teams' routers
   - `PROXY_SSH_KEY` — path to SSH key for connecting to proxies
   - `PROXY_CERTIFICATES` — list of TLS certificates (see example)
   - Other variables if their default values are wrong
4. Run `python3 deploy_proxies.py [--skip-preparation] ../services/<service-name>/deploy.yaml`

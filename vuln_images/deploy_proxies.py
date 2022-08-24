#!/usr/bin/env python3
import asyncio
import ipaddress
import json
import os
import pathlib
import tempfile
from typing import Optional, List

import asyncssh
import digitalocean
import jinja2
import typer

import settings
from config import DeployConfigV1, DeployConfig, ProxyConfigV1, ListenerProtocol

CURRENT_FOLDER = pathlib.Path(__file__).parent


# Limits for TCP proxies
IPTABLES_CHECKSYSTEM_RULE = "iptables -t nat -A PREROUTING -p tcp -j ACCEPT --destination {host} -m tcp --dport {port} -m state --state NEW --source 10.10.10.0/24"
IPTABLES_LIMIT_RULE = "iptables -t nat -A PREROUTING -p tcp -j ACCEPT --destination {host} -m tcp --dport {port} -m state --state NEW -m hashlimit --hashlimit {limit} --hashlimit-mode srcip --hashlimit-srcmask 24 --hashlimit-name {name}"
IPTABLES_LOG_RULE = "iptables -t nat -A PREROUTING -p tcp -j LOG --log-prefix '** 429 TOO MANY ** ' --destination {host} -m tcp --dport {port} -m state --state NEW"
IPTABLES_BLOCK_RULE = "iptables -t nat -A PREROUTING -p tcp -j DNAT --to-destination {host}:429 --destination {host} -m tcp --dport {port} -m state --state NEW"


# Block direct connection to services
IPTABLES_ALLOW_SAME_TEAM_RULE = "iptables -t nat -A PREROUTING -p tcp -j ACCEPT --source {source} --destination {upstream} -m tcp --dport {upstream_port}"
IPTABLES_BLOCK_DIRECT_RULE = "iptables -t nat -A PREROUTING -p tcp -j DNAT --to-destination {host}:{redirect_port} --destination {upstream} -m tcp --dport {upstream_port}"


# Block connections to metrics exporters
# -I because it should before DOCKER chain
IPTABLES_BLOCK_EXPORTERS_RULE = "iptables -t nat -I PREROUTING ! -s 10.10.10.0/24 -d {host}/32 -p tcp --dport {port} -j DNAT --to-destination {host}:1"


def create_ssh_connection(host):
    return asyncssh.connect(host,
                            port=settings.PROXY_SSH_PORT,
                            username=settings.PROXY_SSH_USERNAME,
                            client_keys=[settings.PROXY_SSH_KEY],
                            known_hosts=None)


async def remove_proxies(host: str, service_name: str):
    async with create_ssh_connection(host) as ssh:
        typer.echo(f"[{host}] Removing old nginx configs for {service_name}")
        await ssh.run(f"rm -rf /etc/nginx/sites-enabled/{service_name}_*", check=True)
        await ssh.run(f"rm -rf /etc/nginx/stream.d/{service_name}_*", check=True)


def get_team_network(team_id: int) -> ipaddress.IPv4Network:
    team_network_ip = ipaddress.IPv4Network(settings.BASE_TEAM_NETWORK)[
        team_id * (2 ** (32 - settings.TEAM_NETWORK_MASK))
    ]
    return ipaddress.IPv4Network(f"{team_network_ip}/{settings.TEAM_NETWORK_MASK}")


def get_upstream_ip_address(proxy: ProxyConfigV1, team_id: int) -> ipaddress.IPv4Address:
    team_network = get_team_network(team_id)
    return team_network[proxy.upstream.host_index]


async def deploy_http_proxy(ssh: asyncssh.SSHClientConnection, host: str, team_id: int, service_name: str, proxy: ProxyConfigV1):
    upstream_ip = get_upstream_ip_address(proxy, team_id)

    locations = []
    has_global_location = False
    for index, limit in enumerate(proxy.limits, start=1):
        locations.append({
            "index": index,
            "location": limit.location,
            "limit": limit.limit,
            "burst": limit.burst,
        })
        if limit.location == "/":
            has_global_location = True
    if not has_global_location:
        locations.append({
            "index": len(proxy.limits) + 1,
            "location": "/",
            "burst": 0,
        })

    jinja2_variables = {
        "service_name": service_name,
        "default": proxy.listener.default,
        "proxy_name": proxy.name,
        "server_name": proxy.listener.hostname if proxy.listener.hostname else f"{service_name}.*",
        "use_ssl": proxy.listener.certificate is not None,
        "ssl_certificate": f"/etc/ssl/{proxy.listener.certificate}/fullchain.pem",
        "ssl_certificate_key": f"/etc/ssl/{proxy.listener.certificate}/privkey.pem",
        "client_certificate": (
            f"/etc/ssl/{proxy.listener.client_certificate}/fullchain.pem"
            if proxy.listener.client_certificate else None
        ),
        "upstream_address": f"{upstream_ip}:{proxy.upstream.port}",
        "upstream_protocol": proxy.upstream.protocol,
        "upstream_client_certificate": (
            f"/etc/ssl/{proxy.upstream.client_certificate}/fullchain.pem"
            if proxy.upstream.client_certificate else None
        ),
        "upstream_client_certificate_key": (
            f"/etc/ssl/{proxy.upstream.client_certificate}/privkey.pem"
            if proxy.upstream.client_certificate else None
        ),
        "locations": locations,
        "proxy_host": host,
    }
    template = jinja2.Template((CURRENT_FOLDER / "nginx/http_server.conf.jinja2").read_text())
    filename = tempfile.mktemp(prefix=f"nginx-{service_name}-{proxy.name}-", suffix=".conf")
    with open(filename, "w") as f:
        f.write(template.render(**jinja2_variables))

    target_nginx_config_name = f"/etc/nginx/sites-enabled/{service_name}_{proxy.name}"
    try:
        typer.echo(f"[{host}]    Uploading HTTP config to {target_nginx_config_name}")
        await asyncssh.scp(filename, (ssh, target_nginx_config_name))
    finally:
        os.unlink(filename)


async def deploy_http_monitoring_config(host: str, team_id: int, service_name: str, proxies: List[ProxyConfigV1]):
    monitoring_config = "/root/monitoring/config/prometheus-nginxlog-exporter.yaml"
    access_log_format = "$remote_addr - $remote_user [$time_local] \"$request\" $status $body_bytes_sent \"$http_referer\" \"$http_user_agent\""

    configs = []
    for proxy in proxies:
        configs.extend([{
          "name": f"{service_name}_{proxy.name}_access",
          "format": access_log_format,
          "source": {"files": [f"/var/log/nginx/{service_name}_{proxy.name}_access.log"]},
          "labels": {"service": service_name, "proxy": proxy.name, "team_id": team_id},
          "histogram_buckets": [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
        }])

    async with create_ssh_connection(host) as ssh:
        typer.echo(f"[{host}] Nginx logs monitoring")
        typer.echo(f"[{host}]    Patching monitoring config file {monitoring_config}")
        # Remove old configs from .namespaces and add new ones
        await ssh.run(f"jq 'walk(if type==\"object\" and .name != null and (.name | startswith(\"{service_name}_\")) then empty else . end) "
                      f"| .namespaces |= . + {json.dumps(configs)}' < {monitoring_config} > {monitoring_config}.new",
                      check=True)
        await ssh.run(f"mv {monitoring_config}.new {monitoring_config}", check=True)

        typer.echo(f"[{host}]    Restarting nginx-logs-monitoring")
        await ssh.run("docker-compose -f /root/monitoring/docker-compose.yaml restart", check=True)


async def deploy_tcp_proxy(ssh: asyncssh.SSHClientConnection, host: str, team_id: int, service_name: str, proxy: ProxyConfigV1):
    # 1. Deploy nginx part
    upstream_ip = get_upstream_ip_address(proxy, team_id)

    jinja2_variables = {
        "service_name": service_name,
        "proxy_name": proxy.name,
        "upstream_address": f"{upstream_ip}:{proxy.upstream.port}",
        "port": proxy.listener.port,
        "simultaneous_connections": proxy.listener.tcp_simultaneous_connections,
    }
    template = jinja2.Template((CURRENT_FOLDER / "nginx/tcp_server.conf.jinja2").read_text())
    filename = tempfile.mktemp(prefix=f"nginx-{service_name}-{proxy.name}-", suffix=".conf")
    with open(filename, "w") as f:
        f.write(template.render(**jinja2_variables))

    target_nginx_config_name = f"/etc/nginx/stream.d/{service_name}_{proxy.name}"
    try:
        typer.echo(f"[{host}]    Uploading TCP config to {target_nginx_config_name}")
        await asyncssh.scp(filename, (ssh, target_nginx_config_name))
    finally:
        os.unlink(filename)

    # 2. Remove old iptables rules
    await remove_iptables_blocking_rules(ssh, host, host, proxy.listener.port)

    # 3. Deploy new iptables rules
    assert len(proxy.limits) <= 1, "TCP proxy can have at most one limit"
    for limit in proxy.limits:
        checksystem_rule = IPTABLES_CHECKSYSTEM_RULE.format(host=host, port=proxy.listener.port)
        limit_rule = IPTABLES_LIMIT_RULE.format(
            host=host, port=proxy.listener.port, limit=limit.limit, name=f"{service_name}_{proxy.name}"
        )
        if limit.burst:
            limit_rule += f" --hashlimit-burst {limit.burst}"
        log_rule = IPTABLES_LOG_RULE.format(host=host, port=proxy.listener.port)
        block_rule = IPTABLES_BLOCK_RULE.format(host=host, port=proxy.listener.port)

        for rule in [checksystem_rule, limit_rule, log_rule, block_rule]:
            typer.echo(f"[{host}]    Adding iptables rules: {rule}")
            await ssh.run(rule, check=True)


async def deploy_proxy(host: str, team_id: int, service_name: str, proxy: ProxyConfigV1):
    async with create_ssh_connection(host) as ssh:
        # 1. Deploy proxy
        typer.echo(f"[{host}] Deploying proxy for {service_name}:{proxy.name}")
        if proxy.listener.protocol == "http":
            await deploy_http_proxy(ssh, host, team_id, service_name, proxy)
        elif proxy.listener.protocol == "tcp":
            await deploy_tcp_proxy(ssh, host, team_id, service_name, proxy)
        else:
            raise ValueError(f"Unknown proxy type for deploying: {proxy.listener.protocol}")

        # 2. Remove old iptables rules
        upstream_ip = get_upstream_ip_address(proxy, team_id)

        if proxy.listener.protocol == "http":
            redirect_port = 10
        elif proxy.listener.protocol == "tcp":
            redirect_port = 20
        else:
            raise ValueError()

        typer.echo(f"[{host}] Rejecting all incoming requests to {upstream_ip}:{proxy.upstream.port} "
                   f"by redirecting them to :{redirect_port}")
        await remove_iptables_rules_blocking_direct_connections(ssh, host, proxy, upstream_ip)

        # 3. Deploy blocking direct access rule
        allow_same_team_rule = IPTABLES_ALLOW_SAME_TEAM_RULE.format(
            host=host, redirect_port=redirect_port, upstream=upstream_ip, upstream_port=proxy.upstream.port,
            source=get_team_network(team_id),
        )
        block_rule = IPTABLES_BLOCK_DIRECT_RULE.format(
            host=host, redirect_port=redirect_port, upstream=upstream_ip, upstream_port=proxy.upstream.port,
        )
        for rule in [allow_same_team_rule, block_rule]:
            typer.echo(f"[{host}]    Adding new iptables rule: {rule}")
            await ssh.run(rule, check=True)


async def disable_proxy(host: str, proxy: ProxyConfigV1, upstream_ip: ipaddress.IPv4Address):
    async with create_ssh_connection(host) as ssh:
        await remove_iptables_blocking_rules(ssh, host, str(upstream_ip), proxy.upstream.port)


async def remove_iptables_blocking_rules(
    ssh: asyncssh.SSHClientConnection, host: str, destination_host: str, destination_port: int
):
    result = await ssh.run(
        f"iptables-save -t nat | grep -- '--dport {destination_port}' | grep -- '-d {destination_host}/32'"
    )
    rules = result.stdout.splitlines()
    for rule in rules:
        typer.echo(f"[{host}]    Removing old iptables rules: {rule}")
        await ssh.run(f"iptables -t nat {rule.replace('-A', '-D')}")


async def prepare_host_for_proxies(host: str, team_id: int):
    typer.echo(f"[{host}] Preparing host for being a proxy")
    async with create_ssh_connection(host) as ssh:
        # 1. Install nginx
        typer.echo(f"[{host}]    Installing nginx, openssl and docker")
        await ssh.run("apt-get install -y nginx openssl docker.io docker-compose jq", check=True)

        # 2. Generate dhparam — only once!
        typer.echo(f"[{host}]    Generating /etc/nginx/dhparam.pem if not exists")
        await ssh.run(
            # Why we use -dsaparam? Because it's still secure and much more faster:
            # https://security.stackexchange.com/questions/95178/diffie-hellman-parameters-still-calculating-after-24-hours
            "/bin/bash -c '[ ! -f /etc/nginx/dhparam.pem ] && "
            "openssl dhparam -dsaparam -out /etc/nginx/dhparam.pem 4096'"
        )

        # 3. Copy TLS certificates
        for certificate_name, certificate in settings.PROXY_CERTIFICATES.items():
            if type(certificate) is dict:
                for teams_range, teams_range_certificate in certificate.items():
                    if team_id in teams_range:
                        certificate = teams_range_certificate
                        break
                else:
                    raise ValueError(f"Can not find suitable certificate {certificate_name} for team {team_id}. "
                                     f"Check your PROXY_CERTIFICATES in settings.py")

            chain, private_key = certificate
            typer.echo(f"[{host}]    Uploading /etc/ssl/{certificate_name}/{{fullchain.pem,privkey.pem}}")
            await ssh.run(f"mkdir -p /etc/ssl/{certificate_name}", check=True)
            await asyncssh.scp(chain.as_posix(), (ssh, f"/etc/ssl/{certificate_name}/fullchain.pem"), preserve=True)
            await asyncssh.scp(private_key.as_posix(), (ssh, f"/etc/ssl/{certificate_name}/privkey.pem"), preserve=True)

        # 4. Upload files
        typer.echo(f"[{host}]    Uploading /etc/nginx/nginx.conf")
        await asyncssh.scp("nginx/nginx.conf", (ssh, "/etc/nginx/nginx.conf"))
        typer.echo(f"[{host}]    Uploading /var/www/html/too_many_requests.html")
        await asyncssh.scp("nginx/too_many_requests.html", (ssh, "/var/www/html/too_many_requests.html"))
        typer.echo(f"[{host}]    Uploading /var/www/html/use_proxy.html")
        await asyncssh.scp("nginx/use_proxy.html", (ssh, "/var/www/html/use_proxy.html"))
        typer.echo(f"[{host}]    Uploading /etc/nginx/conf.d/gzip.conf")
        await asyncssh.scp("nginx/gzip.conf", (ssh, "/etc/nginx/conf.d/gzip.conf"))
        typer.echo(f"[{host}]    Uploading /etc/nginx/conf.d/use_proxy.conf")
        await asyncssh.scp("nginx/use_proxy.conf", (ssh, "/etc/nginx/conf.d/use_proxy.conf"))

        await ssh.run("mkdir -p /etc/nginx/stream.d", check=True)
        await ssh.run("mkdir -p /root/monitoring/config", check=True)

        typer.echo(f"[{host}]    Uploading /root/too_many_requests.py")
        await asyncssh.scp("iptables/too_many_requests.py", (ssh, "/root/too_many_requests.py"))
        typer.echo(f"[{host}]    Uploading /etc/systemd/system/too_many_requests.service")
        await asyncssh.scp("iptables/too_many_requests.service", (ssh, "/etc/systemd/system/too_many_requests.service"))
        await ssh.run("systemctl daemon-reload", check=True)

        # 5. Disable default nginx site
        typer.echo(f"[{host}]    Unlinking /etc/nginx/sites-enabled/default")
        await ssh.run("unlink /etc/nginx/sites-enabled/default")

        # 6. Enable too_many_requests.service
        typer.echo(f"[{host}]    Enabling and starting /etc/systemd/system/too_many_requests.service")
        await ssh.run("systemctl enable too_many_requests", check=True)
        await ssh.run("systemctl restart too_many_requests", check=True)

        # 7. Restart nginx
        typer.echo(f"[{host}]    Restarting nginx")
        await ssh.run("nginx -t", check=True)
        await ssh.run("systemctl restart nginx", check=True)

        # 8.
        typer.echo(f"[{host}]    Uploading monitoring config to /root/monitoring/docker-compose.yaml "
                   f"and /root/monitoring/config/prometheus-nginxlog-exporter.yaml")
        await asyncssh.scp("monitoring/docker-compose.yaml", (ssh, "/root/monitoring/docker-compose.yaml"))
        await asyncssh.scp("monitoring/prometheus-nginxlog-exporter.yaml",
                           (ssh, "/root/monitoring/config/prometheus-nginxlog-exporter.yaml"))
        await ssh.run("docker-compose -f /root/monitoring/docker-compose.yaml up -d", check=True)

        typer.echo(f"[{host}]    Blocking incoming connections to metrics exporters: :59999 and :59998")
        for port in [59998, 59999]:
            await remove_iptables_blocking_rules(ssh, host, host, port)
            await ssh.run(IPTABLES_BLOCK_EXPORTERS_RULE.format(port=port, host=host), check=True)


async def post_deploy(host: str, team_id: int):
    async with create_ssh_connection(host) as ssh:
        typer.echo(f"[{host}] Reloading nginx")
        await ssh.run("nginx -t", check=True)
        await ssh.run("systemctl reload nginx", check=True)


async def create_dns_record(hostname: str, value: str, ttl: int = 60):
    domain = digitalocean.Domain(token=settings.DO_API_TOKEN, name=settings.DNS_ZONE)
    for record in domain.get_records():
        if record.name == hostname and record.type == "A":
            if record.data != value or record.ttl != ttl:
                typer.echo(f"[{value}] Updating DNS record {hostname}.{settings.DNS_ZONE} → {value}")
                record.data = value
                record.ttl = ttl
                record.save()
            else:
                typer.echo(f"[{value}] DNS record already exists: {hostname}.{settings.DNS_ZONE} → {value}")
            return

    typer.echo(f"[{value}] Creating DNS record {hostname}.{settings.DNS_ZONE} → {value}")
    domain.create_new_domain_record(
        type="A",
        name=hostname,
        data=value,
        ttl=ttl,
    )


async def deploy_proxies_for_team(
    config: DeployConfig, host: str, skip_preparation: bool, prepare_only: bool, team_id: int
):
    # 1. Prepare host
    if not skip_preparation:
        await prepare_host_for_proxies(host, team_id)

    if prepare_only:
        return

    # 2. Remove old configs
    await remove_proxies(host, config.service)

    # 3. Deploy new configs for all proxies in specified in the config
    for proxy in config.proxies:
        if proxy.disable:
            typer.echo(f"[{host}] Disabling proxy {config.service}:{proxy.name}")
            upstream_ip = get_upstream_ip_address(proxy, team_id)
            await disable_proxy(host, proxy, upstream_ip)
            for dns_record_prefix in proxy.dns_records:
                await create_dns_record(dns_record_prefix + f".team{team_id}", str(upstream_ip))
            continue

        await deploy_proxy(host, team_id, config.service, proxy)
        for dns_record_prefix in proxy.dns_records:
            await create_dns_record(dns_record_prefix + f".team{team_id}", host)

    http_proxies = [proxy for proxy in config.proxies if proxy.listener.protocol == ListenerProtocol.HTTP and not proxy.disable]
    await deploy_http_monitoring_config(host, team_id, config.service, http_proxies)

    # 4. Run some post-deploy steps such as reloading nginx
    await post_deploy(host, team_id)


async def deploy_proxies(
    config: DeployConfig, skip_preparation: bool, prepare_only: bool, only_for_team_id: Optional[int]
):
    tasks = []

    for team_id, host in settings.PROXY_HOSTS.items():
        if only_for_team_id is not None and only_for_team_id != team_id:
            continue

        tasks.append(deploy_proxies_for_team(config, host, skip_preparation, prepare_only, team_id))

    await asyncio.gather(*tasks)


def main(
    config_path: typer.FileText,
    check: bool = typer.Option(False, "--check", help="Only check the config, don't deploy anything"),
    skip_preparation: bool = typer.Option(
        False, "--skip-preparation",
        help="Skip common preparation steps: generating dhparam, copying certificates, ..."
    ),
    prepare_only: bool = typer.Option(
        False, "--prepare-only",
        help="Run only preparation steps: generating dhparam, copying certificates, ..."
    ),
    team_id: Optional[int] = typer.Option(None, "--team-id", help="Deploy proxy only for specified team"),
):
    if skip_preparation and prepare_only:
        typer.echo("[ERROR] --skip-preparation and --prepare-only can not be used together")
        raise typer.Exit(code=1)

    config = DeployConfigV1.parse_file(config_path.name)
    if check:
        raise typer.Exit()

    asyncio.run(deploy_proxies(config, skip_preparation, prepare_only, team_id))


if __name__ == "__main__":
    typer.run(main)

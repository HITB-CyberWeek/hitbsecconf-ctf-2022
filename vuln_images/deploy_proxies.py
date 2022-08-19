#!/usr/bin/env python3
import asyncio
import ipaddress
import os
import pathlib
import tempfile
from typing import Optional

import asyncssh
import digitalocean
import jinja2
import typer

import settings
from config import DeployConfigV1, DeployConfig, ProxyConfigV1

CURRENT_FOLDER = pathlib.Path(__file__).parent


def create_ssh_connection(host):
    return asyncssh.connect(host,
                            port=settings.PROXY_SSH_PORT,
                            username=settings.PROXY_SSH_USERNAME,
                            client_keys=[settings.PROXY_SSH_KEY],
                            known_hosts=None)


async def deploy_http_proxy(host: str, team_id: int, service_name: str, proxy: ProxyConfigV1):
    async with create_ssh_connection(host) as ssh:
        team_network_ip = ipaddress.IPv4Network(settings.BASE_TEAM_NETWORK)[
            team_id * (2 ** (32 - settings.TEAM_NETWORK_MASK))
        ]
        team_network = ipaddress.IPv4Network(f"{team_network_ip}/{settings.TEAM_NETWORK_MASK}")
        target_ip = team_network[proxy.target_host_index]
        target = f"http://{target_ip}:{proxy.target_port}"

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
            "server_name": proxy.hostname if proxy.hostname else f"{service_name}.*",
            "use_ssl": proxy.certificate is not None,
            "ssl_certificate": f"/etc/ssl/{proxy.certificate}/fullchain.pem",
            "ssl_certificate_key": f"/etc/ssl/{proxy.certificate}/privkey.pem",
            "target": target,
            "locations": locations,
        }
        template = jinja2.Template((CURRENT_FOLDER / "nginx/http_server.conf.jinja2").read_text())
        filename = tempfile.mktemp(prefix=f"nginx-{service_name}-{proxy.name}-", suffix=".conf")
        with open(filename, "w") as f:
            f.write(template.render(**jinja2_variables))

        target_nginx_config_name = f"/etc/nginx/sites-enabled/{service_name}_{proxy.name}"
        try:
            typer.echo(f"   Uploading HTTP config to {target_nginx_config_name}")
            await asyncssh.scp(filename, (ssh, target_nginx_config_name))
        finally:
            os.unlink(filename)


async def deploy_proxy(host: str, team_id: int, service_name: str, proxy: ProxyConfigV1):
    typer.echo(f"Deploying proxy for {service_name}:{proxy.name} to {host}")
    if proxy.type == "http":
        await deploy_http_proxy(host, team_id, service_name, proxy)
    else:
        raise ValueError(f"Unknown proxy type for deploying: {proxy.type}")


async def prepare_host_for_proxies(host: str):
    typer.echo(f"Preparing host {host} for being a proxy:")
    async with await create_ssh_connection(host) as ssh:
        # 1. Install nginx
        typer.echo("   Installing nginx and openssl")
        await ssh.run("apt-get install -y nginx openssl")

        # 2. Generate dhparam — only once!
        typer.echo("   Generating /etc/nginx/dhparam.pem if not exists")
        await ssh.run(
            # Why we use -dsaparam? Because it's still secure and much more faster:
            # https://security.stackexchange.com/questions/95178/diffie-hellman-parameters-still-calculating-after-24-hours
            "/bin/bash -c '[ ! -f /etc/nginx/dhparam.pem ] && "
            "openssl dhparam -dsaparam -out /etc/nginx/dhparam.pem 4096'"
        )

        # 3. Copy TLS certificates
        for certificate_name, (chain, private_key) in settings.PROXY_CERTIFICATES.items():
            typer.echo(f"   Uploading /etc/ssl/{certificate_name}/{{fullchain.pem,privkey.pem}}")
            await ssh.run(f"mkdir -p /etc/ssl/{certificate_name}")
            await asyncssh.scp(chain.as_posix(), (ssh, f"/etc/ssl/{certificate_name}/fullchain.pem"), preserve=True)
            await asyncssh.scp(private_key.as_posix(), (ssh, f"/etc/ssl/{certificate_name}/privkey.pem"), preserve=True)

        # 4. Copy too_many_requests.html
        typer.echo("   Uploading /var/www/html/too_many_requests.html")
        await asyncssh.scp("nginx/too_many_requests.html", (ssh, "/var/www/html/too_many_requests.html"))


async def post_deploy(host: str, team_id: int):
    async with create_ssh_connection(host) as ssh:
        typer.echo(f"Reloading nginx on {host}")
        await ssh.run("nginx -t", check=True)
        await ssh.run("systemctl reload nginx", check=True)


async def create_dns_record(host: str, service_name: str, team_id: int):
    hostname = settings.DNS_RECORD_TEMPLATE.replace("$SERVICE", service_name).replace("$TEAM_ID", str(team_id))
    typer.echo(f"Creating DNS record {hostname}.{settings.DNS_ZONE} → {host}")
    domain = digitalocean.Domain(token=settings.DO_API_TOKEN, name=settings.DNS_ZONE)
    domain.create_new_domain_record(
        type="A",
        name=hostname,
        data=host
    )


async def deploy_proxies(config: DeployConfig, skip_preparation: bool, only_for_team_id: Optional[int]):
    for team_id, host in settings.PROXY_HOSTS.items():
        if only_for_team_id is not None and only_for_team_id != team_id:
            continue

        if not skip_preparation:
            await prepare_host_for_proxies(host)

        for proxy in config.proxies:
            await deploy_proxy(host, team_id, config.service, proxy)

        if config.proxies:
            await create_dns_record(host, config.service, team_id)

        await post_deploy(host, team_id)


def main(
        config_path: typer.FileText,
        check: bool = typer.Option(False, "--check", help="Only check the config, don't deploy anything"),
        skip_preparation: bool = typer.Option(
            False, "--skip-preparation",
            help="Skip common preparation step: generating dhparam, copying certificates, ..."
        ),
        team_id: Optional[int] = typer.Option(None, "--team-id", help="Deploy proxy only for specified team"),
):
    config = DeployConfigV1.parse_file(config_path.name)
    if check:
        raise typer.Exit()

    asyncio.get_event_loop().run_until_complete(deploy_proxies(config, skip_preparation, team_id))


if __name__ == "__main__":
    typer.run(main)

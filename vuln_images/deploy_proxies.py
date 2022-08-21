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


async def remove_proxies(host: str, service_name: str):
    async with create_ssh_connection(host) as ssh:
        typer.echo(f"[{host}] Removing old nginx configs for {service_name}")
        await ssh.run(f"rm -rf /etc/nginx/sites-enabled/{service_name}_*", check=True)


async def deploy_http_proxy(host: str, team_id: int, service_name: str, proxy: ProxyConfigV1):
    async with create_ssh_connection(host) as ssh:
        team_network_ip = ipaddress.IPv4Network(settings.BASE_TEAM_NETWORK)[
            team_id * (2 ** (32 - settings.TEAM_NETWORK_MASK))
        ]
        team_network = ipaddress.IPv4Network(f"{team_network_ip}/{settings.TEAM_NETWORK_MASK}")
        upstream_ip = team_network[proxy.upstream.host_index]
        upstream = f"{proxy.upstream.protocol}://{upstream_ip}:{proxy.upstream.port}"

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
            "server_name": proxy.listener.hostname if proxy.listener.hostname else f"{service_name}.*",
            "use_ssl": proxy.listener.certificate is not None,
            "ssl_certificate": f"/etc/ssl/{proxy.listener.certificate}/fullchain.pem",
            "ssl_certificate_key": f"/etc/ssl/{proxy.listener.certificate}/privkey.pem",
            "client_certificate": (
                f"/etc/ssl/{proxy.listener.client_certificate}/fullchain.pem"
                if proxy.listener.client_certificate else None
            ),
            "upstream": upstream,
            "upstream_client_certificate": (
                f"/etc/ssl/{proxy.upstream.client_certificate}/fullchain.pem"
                if proxy.upstream.client_certificate else None
            ),
            "upstream_client_certificate_key": (
                f"/etc/ssl/{proxy.upstream.client_certificate}/privkey.pem"
                if proxy.upstream.client_certificate else None
            ),
            "locations": locations,
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


async def deploy_proxy(host: str, team_id: int, service_name: str, proxy: ProxyConfigV1):
    typer.echo(f"[{host}] Deploying proxy for {service_name}:{proxy.name}")
    if proxy.listener.protocol == "http":
        await deploy_http_proxy(host, team_id, service_name, proxy)
    else:
        raise ValueError(f"Unknown proxy type for deploying: {proxy.listener.protocol}")


async def prepare_host_for_proxies(host: str):
    typer.echo(f"[{host}] Preparing host for being a proxy")
    async with create_ssh_connection(host) as ssh:
        # 1. Install nginx
        typer.echo(f"[{host}]    Installing nginx and openssl")
        await ssh.run("apt-get install -y nginx openssl", check=True)

        # 2. Generate dhparam — only once!
        typer.echo(f"[{host}]    Generating /etc/nginx/dhparam.pem if not exists")
        await ssh.run(
            # Why we use -dsaparam? Because it's still secure and much more faster:
            # https://security.stackexchange.com/questions/95178/diffie-hellman-parameters-still-calculating-after-24-hours
            "/bin/bash -c '[ ! -f /etc/nginx/dhparam.pem ] && "
            "openssl dhparam -dsaparam -out /etc/nginx/dhparam.pem 4096'"
        )

        # 3. Copy TLS certificates
        for certificate_name, (chain, private_key) in settings.PROXY_CERTIFICATES.items():
            typer.echo(f"[{host}]    Uploading /etc/ssl/{certificate_name}/{{fullchain.pem,privkey.pem}}")
            await ssh.run(f"mkdir -p /etc/ssl/{certificate_name}", check=True)
            await asyncssh.scp(chain.as_posix(), (ssh, f"/etc/ssl/{certificate_name}/fullchain.pem"), preserve=True)
            await asyncssh.scp(private_key.as_posix(), (ssh, f"/etc/ssl/{certificate_name}/privkey.pem"), preserve=True)

        # 4. Copy too_many_requests.html
        typer.echo(f"[{host}]    Uploading /var/www/html/too_many_requests.html")
        await asyncssh.scp("nginx/too_many_requests.html", (ssh, "/var/www/html/too_many_requests.html"))


async def post_deploy(host: str, team_id: int):
    async with create_ssh_connection(host) as ssh:
        typer.echo(f"[{host}] Reloading nginx")
        await ssh.run("nginx -t", check=True)
        await ssh.run("systemctl reload nginx", check=True)


async def create_dns_record(hostname: str, value: str):
    domain = digitalocean.Domain(token=settings.DO_API_TOKEN, name=settings.DNS_ZONE)
    for record in domain.get_records():
        if record.name == hostname and record.type == "A":
            if record.data != value:
                typer.echo(f"[{value}] Updating DNS record {hostname}.{settings.DNS_ZONE} → {value}")
                record.data = value
                record.save()
            else:
                typer.echo(f"[{value}] DNS record already exists: {hostname}.{settings.DNS_ZONE} → {value}")
            return

    typer.echo(f"[{value}] Creating DNS record {hostname}.{settings.DNS_ZONE} → {value}")
    domain.create_new_domain_record(
        type="A",
        name=hostname,
        data=value
    )


async def deploy_proxies_for_team(
    config: DeployConfig, host: str, skip_preparation: bool, prepare_only: bool, team_id: int
):
    # 1. Prepare host
    if not skip_preparation:
        await prepare_host_for_proxies(host)

    if prepare_only:
        return

    # 2. Remove old configs
    await remove_proxies(host, config.service)

    # 3. Deploy new configs for all proxies in specified in the config
    for proxy in config.proxies:
        await deploy_proxy(host, team_id, config.service, proxy)
        for dns_record_prefix in proxy.dns_records:
            await create_dns_record(dns_record_prefix + f".team{team_id}", host)

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

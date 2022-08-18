#!/usr/bin/env python3
import json
import os
import pathlib
import subprocess
import tempfile

import jinja2
import typer

import settings
from config import DeployConfig, DeployConfigV1, substitute_variables

PACKER_TOOL = "packer"
CURRENT_FOLDER = pathlib.Path(__file__).parent
VULNIMAGES_CONFIG_PATH = CURRENT_FOLDER / "../ctf-cloud/cloud/cloud_master/files/api_srv/do_vulnimages.json"


def update_vulnimages_config(service_name: str, image_id: int):
    config = json.loads(VULNIMAGES_CONFIG_PATH.read_text())
    config[service_name] = image_id
    VULNIMAGES_CONFIG_PATH.write_text(json.dumps(config, indent=4))


def get_environment_for_shell_commands(config: DeployConfig):
    return {
        "SERVICE": config.service,
        "USERNAME": config.username,
    }


def build_image(config_path: pathlib.Path, config: DeployConfig, save_packer_config: bool, packer_debug: bool):
    config_folder = config_path.parent

    # Step 1 — build_outside_vm
    if config.scripts.build_outside_vm:
        typer.echo(typer.style("Step 1", fg=typer.colors.GREEN, bold=True) + f". Running {config.scripts.build_outside_vm!r}")
        process = subprocess.Popen(
            config.scripts.build_outside_vm, shell=True, env=get_environment_for_shell_commands(config),
            cwd=config_folder.as_posix()
        )
        process.wait()
        if process.returncode != 0:
            typer.echo(typer.style(f"Command failed with exit code {process.returncode}", fg=typer.colors.RED, bold=True))
            raise typer.Exit(process.returncode)
    else:
        typer.echo(
            typer.style("Step 1", fg=typer.colors.YELLOW, bold=True) +
            " was ignored, because scripts.build_outside_vm not specified."
        )

    # Step 2 — build packer configuration
    typer.echo(typer.style("Step 2", fg=typer.colors.GREEN, bold=True) + f". Preparing configuration for the packer tool")
    files = []
    for file in config.files:
        files += [prepared_file.dict() for prepared_file in file.prepare_for_upload(config, config_folder)]
    jinja2_variables = {
        "api_token": settings.DO_API_TOKEN,
        "files_path": pathlib.Path("packer").absolute().as_posix(),
        "vm_size": "c-2",
        "region": "ams3",
        "service": config.service,
        "username": config.username,
        "files": files,
        "build_inside_vm": substitute_variables(config.scripts.build_inside_vm, config).splitlines(),
        "start_once": substitute_variables(config.scripts.start_once, config),
    }
    template = jinja2.Template((CURRENT_FOLDER / "packer/image.pkr.hcl.jinja2").read_text())
    filename = tempfile.mktemp(prefix=f"packer-{config.service}-", suffix=".pkr.hcl", dir=config_folder)
    try:
        with open(filename, "w") as f:
            f.write(template.render(**jinja2_variables))

        typer.echo(f"Built configuration for the packer tool: {filename}")

        # Step 3 — run packer and build the image
        typer.echo(typer.style("Step 3", fg=typer.colors.GREEN, bold=True) + f". Run packer tool and build the image!")

        process = subprocess.Popen(
            [PACKER_TOOL, "init", "-upgrade", pathlib.Path(filename).name],
            cwd=config_folder.as_posix(),
        )
        process.wait()

        packer_env = None
        debug_options = []
        if packer_debug:
            packer_env = {
                **os.environ,
                "PACKER_LOG": "1",
                "PACKER_LOG_PATH": "packer.log",
            }
            debug_options = ["-debug"]

        process = subprocess.Popen(
            [PACKER_TOOL, "build", *debug_options, pathlib.Path(filename).name],
            cwd=config_folder.as_posix(),
            env=packer_env,
        )
        process.wait()
        if process.returncode != 0:
            typer.echo(typer.style(f"Packer failed with exit code {process.returncode}", fg=typer.colors.RED, bold=True))
            raise typer.Exit(process.returncode)
    finally:
        if not save_packer_config:
            os.unlink(filename)

    # Step 4 — read manifest file
    typer.echo(typer.style("Step 4", fg=typer.colors.GREEN, bold=True) + f". Get image id")
    manifest_path = config_folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    snapshot_id = manifest["builds"][0]["artifact_id"]
    typer.echo(f"Snapshot ID is {snapshot_id}")

    if ":" in snapshot_id:
        snapshot_id = int(snapshot_id.split(":")[-1])
    else:
        snapshot_id = int(snapshot_id)
    update_vulnimages_config(config.service, snapshot_id)
    typer.echo(
        typer.style("Updated config", fg=typer.colors.GREEN, bold=True) +
        f" at {VULNIMAGES_CONFIG_PATH} , don't forget to commit and deploy it."
    )

    manifest_path.unlink()


def main(
    config_path: typer.FileText,
    check: bool = typer.Option(False, "--check", help="Only check the config, don't deploy anything"),
    save_packer_config: bool = typer.Option(False, "--save-packer-config", help="Don't remove packer configuration file"),
    packer_debug: bool = typer.Option(False, "--packer-debug", help="Enable -debug option in packer"),
):
    config = DeployConfigV1.parse_file(config_path.name)
    if check:
        raise typer.Exit()

    config_path = pathlib.Path(config_path.name)
    build_image(config_path, config, save_packer_config, packer_debug)


if __name__ == "__main__":
    typer.run(main)

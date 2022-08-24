import docker
import os

DOCKER_API = docker.from_env()
IMAGE = "sh:latest"
NETWORK = "sh_s3"
ULIMITS = [
    docker.types.Ulimit(name="CPU", soft=10, hard=10),
    docker.types.Ulimit(name="FSIZE", soft=50 * 1024, hard=50 * 1024),
    docker.types.Ulimit(name="NPROC", soft=50, hard=50),
    docker.types.Ulimit(name="NOFILE", soft=15, hard=15)
]


def run(archive, bucket):
    volumes = {os.getenv("INPUT_PATH"): {"bind": "/data/input", "mode": "ro"}}
    env = {
        "MINIO_SH_USER": os.getenv("MINIO_SH_USER"),
        "MINIO_SH_PASSWORD": os.getenv("MINIO_SH_PASSWORD")
    }

    container = DOCKER_API.containers.create(
        IMAGE,
        command=["python3", "make_site.py", archive, bucket],
        volumes=volumes,
        ulimits=ULIMITS,
        network=NETWORK,
        mem_limit="128m",
        memswap_limit="128m",
        environment=env
    )
    container.start()
    container.wait(timeout=10)
    container.remove()

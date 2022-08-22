import pathlib
from typing import List, Union, Optional, Literal, Iterable

from pydantic import validator, conint, NonNegativeInt, constr, PositiveInt, root_validator, ValidationError
from pydantic_yaml import YamlModel, YamlStrEnum

import settings


class ScriptsConfigV1(YamlModel):
    build_outside_vm: str = ""
    build_inside_vm: str
    start_once: str


class FileDeployConfigV1(YamlModel):
    source: str = ""
    sources: List[str] = []
    destination: str = "/home/$SERVICE"

    def prepare_for_upload(self, config: "DeployConfig", config_folder: pathlib.Path) -> Iterable["FileDeployConfigV1"]:
        # Packer's file provisioner works with "sources" option very bad: i.e., doesn't support directories there,
        # so we convert "sources" into multiple Files with "source"
        if self.sources:
            files = [
                FileDeployConfigV1(source=source, destination=self.destination) for source in self._unfold_globs(self.sources, config_folder)
            ]
            for file in files:
                yield from file.prepare_for_upload(config, config_folder)
            return

        # Support for glob in "source": interpreter them as "sources"
        if len(list(config_folder.glob(self.source))) > 1:
            yield from FileDeployConfigV1(
                sources=[self.source],
                destination=self.destination,
            ).prepare_for_upload(config, config_folder)
            return

        destination = substitute_variables(self.destination, config)
        if config_folder / self.source and not destination.endswith("/"):
            destination += "/"
        yield FileDeployConfigV1(
            source=self.source,
            destination=destination,
        )

    @staticmethod
    def _unfold_globs(sources: List[str], folder: pathlib.Path) -> List[str]:
        result = []
        for source in sources:
            trailing_slash = "/" if source.endswith("/") else ""
            result += [p.relative_to(folder).as_posix() + trailing_slash for p in folder.glob(source)]
        return result


class ListenerProtocol(YamlStrEnum):
    TCP = "tcp"
    HTTP = "http"


class ProxySource(YamlStrEnum):
    TEAM = "team"


class ProxyLimit(YamlModel):
    source: ProxySource
    location: Optional[str] = None
    limit: str
    burst: NonNegativeInt = 0


class UpstreamProtocol(YamlStrEnum):
    TCP = "tcp"
    HTTP = "http"
    HTTPS = "https"


class UpstreamConfigV1(YamlModel):
    host_index: PositiveInt
    port: conint(gt=0, le=65535)
    protocol: UpstreamProtocol = UpstreamProtocol.HTTP
    client_certificate: Optional[str]


class ListenerConfigV1(YamlModel):
    protocol: ListenerProtocol
    port: Optional[conint(gt=0, le=65535)] = None
    hostname: Optional[str] = None
    certificate: Optional[str] = None
    client_certificate: Optional[str] = None
    tcp_simultaneous_connections: Optional[int] = None
    default: bool = False

    @validator("certificate", "client_certificate")
    def _validate_certificate(cls, certificate: Optional[str]) -> Optional[str]:
        if certificate is not None:
            assert certificate in settings.PROXY_CERTIFICATES, f"unknown certificate name: {certificate}"

        return certificate

    @validator("port", always=True)
    def _validate_port(cls, port: Optional[int], values) -> int:
        if port is not None:
            return port

        if values["protocol"] == "http":
            if "certificate" not in values or values["certificate"] is None:
                return 80
            if values["certificate"] is not None:
                return 443

        raise ValidationError(f"Port should be specified for proxy of type {values['protocol']}")

    @validator("tcp_simultaneous_connections")
    def _validate_tcp_simultaneous_connections(cls, tcp_simultaneous_connections: Optional[int], values) -> Optional[int]:
        if values.get("protocol") == "http":
            raise ValidationError("HTTP Proxy can not have listener.tcp_simultaneous_connections parameter")

        return tcp_simultaneous_connections


class ProxyConfigV1(YamlModel):
    name: constr(min_length=1)
    listener: ListenerConfigV1
    upstream: UpstreamConfigV1
    limits: List[ProxyLimit] = []
    dns_records: List[str] = []

    @root_validator
    def validate_object(cls, values):
        if "listener" in values and values["listener"].protocol == "tcp":
            for limit in values.get("limits", []):
                if limit.location:
                    raise ValidationError("Limit in TCP proxy can not have a location parameter")

            if values["listener"].port is None:
                raise ValidationError("TCP proxy must have listener.port parameter")

        elif "listener" in values and values["listener"].protocol == "tcp":
            for limit in values.get("limits", []):
                if not limit.location:
                    raise ValidationError("Limit in HTTP proxy must have a location parameter")

        return values

    @validator("limits")
    def validate_limits(cls, limits: List[ProxyLimit], values) -> List[ProxyLimit]:
        if "listener" in values and values["listener"].protocol == "tcp":
            if len(limits) > 1:
                raise ValidationError(f"TCP proxy can have at most one limit, but you specified {len(limits)}")

        return limits


class DeployConfigV1(YamlModel):
    version: Literal[1]

    service: constr(regex='^[a-z0-9_-]{1,30}$')
    username: Optional[constr(regex='^[a-z0-9_-]{1,30}$')] = None
    scripts: ScriptsConfigV1
    files: List[FileDeployConfigV1]
    proxies: List[ProxyConfigV1] = []


DeployConfig = Union[DeployConfigV1]


def substitute_variables(data: str, config: DeployConfig) -> str:
    return data.replace("$SERVICE", config.service if config.service else "").replace("$USERNAME", config.username if config.username else "")

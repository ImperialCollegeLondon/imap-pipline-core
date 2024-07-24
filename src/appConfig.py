"""App configuration module."""

from enum import Enum
from pathlib import Path

from pydantic import BaseModel


class Source(BaseModel):
    folder: Path


class DestinationType(Enum):
    LOCAL = "local"
    SFTP = "sftp"


class Destination(BaseModel):
    folder: Path = Path(".")
    filename: str


class PacketDefinition(BaseModel):
    hk: Path = Path("src/xtce/tlm_20240724.xml")


class AppConfig(BaseModel):
    source: Source
    work_folder: Path = Path(".work")
    destination: Destination
    packet_definition: PacketDefinition = PacketDefinition()

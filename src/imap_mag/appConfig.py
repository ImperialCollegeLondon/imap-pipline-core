"""App configuration module."""

from pathlib import Path

from pydantic import BaseModel
from pydantic.config import ConfigDict


def hyphenize(field: str):
    return field.replace("_", "-")


class Source(BaseModel):
    folder: Path


class Destination(BaseModel):
    folder: Path = Path(".")
    filename: str


class PacketDefinition(BaseModel):
    hk: Path


class AppConfig(BaseModel):
    source: Source
    work_folder: Path = Path(".work")
    destination: Destination
    packet_definition: PacketDefinition

    # pydantic configuration to allow hyphenated fields
    model_config = ConfigDict(alias_generator=hyphenize)

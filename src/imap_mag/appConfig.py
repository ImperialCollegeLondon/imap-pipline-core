"""App configuration module."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from pydantic.aliases import AliasGenerator
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
    packet_definition: Optional[PacketDefinition] = None
    webpoda_url: str = "https://lasp.colorado.edu/ops/imap/poda/dap2/"

    def __init__(self, **kwargs):
        kwargs = dict((key.replace("_", "-"), value) for (key, value) in kwargs.items())
        super().__init__(**kwargs)

    # pydantic configuration to allow hyphenated fields
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=hyphenize, serialization_alias=hyphenize
        )
    )

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class Source(BaseModel):
    folder: Path


class DestinationType(Enum):
    LOCAL = "local"
    SFTP = "sftp"


class Destination(BaseModel):
    folder: Path = Path(".")
    filename: str


class AppConfig(BaseModel):
    source: Source
    work_folder: Path = Path(".work")
    destination: Destination

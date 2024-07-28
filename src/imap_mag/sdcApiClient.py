"""Interact with SDC APIs to get MAG data via imap-data-access."""

import abc
import logging
import pathlib
import typing
from datetime import datetime

import imap_data_access
from typing_extensions import Unpack


class FileOptions(typing.TypedDict):
    """Options for generating file name."""

    level: str | None
    descriptor: str | None
    start_date: datetime | None
    version: str | None


class VersionOptions(typing.TypedDict):
    """Options for determining unique version."""

    level: str | None
    start_date: datetime | None


class QueryOptions(typing.TypedDict):
    """Options for query."""

    level: str | None
    descriptor: str | None
    start_date: datetime | None
    end_date: datetime | None
    version: str | None
    extension: str | None


class ISDCApiClient(abc.ABC):
    """Interface for interacting with imap-data-access."""

    @staticmethod
    @abc.abstractmethod
    def get_file_path(**options: Unpack[FileOptions]) -> tuple[str, str]:
        """Get file path for data from imap-data-access."""
        pass

    @abc.abstractmethod
    def upload(self, file_name: str) -> None:
        """Upload data to imap-data-access."""
        pass

    @abc.abstractmethod
    def unique_version(
        self, **options: Unpack[VersionOptions]
    ) -> tuple[str, str | None]:
        """Determine a unique version for the data by querying imap_data_access."""
        pass

    @abc.abstractmethod
    def query(self, **options: Unpack[QueryOptions]) -> list[dict[str, str]]:
        """Download data from imap-data-access."""
        pass

    @abc.abstractmethod
    def get_filename(
        self, **options: Unpack[FileOptions]
    ) -> list[dict[str, str]] | None:
        """Wait for file to be available in imap-data-access."""
        pass

    @abc.abstractmethod
    def download(self, file_name: str) -> pathlib.Path:
        """Download data from imap-data-access."""
        pass


class SDCApiClient(ISDCApiClient):
    """Class for uploading and downloading MAG data via imap-data-access."""

    def __init__(self, data_dir: str) -> None:
        imap_data_access.config["DATA_DIR"] = pathlib.Path(data_dir)

    @staticmethod
    def get_file_path(**options: Unpack[FileOptions]) -> tuple[str, str]:
        """Get file path for data from imap-data-access."""

        science_file = imap_data_access.ScienceFilePath.generate_from_inputs(
            instrument="mag",
            data_level=options["level"],
            descriptor=options["descriptor"],
            start_time=options["start_date"].strftime("%Y%m%d"),
            version=options["version"],
        )

        return (science_file.filename, science_file.construct_path())

    def upload(self, file_name: str) -> None:
        """Upload data to imap-data-access."""

        logging.debug(f"Uploading {file_name} to imap-data-access.")

        try:
            imap_data_access.upload(file_name)
        except imap_data_access.io.IMAPDataAccessError as e:
            logging.warn(f"Upload failed: {e}")

    def unique_version(
        self, **options: Unpack[VersionOptions]
    ) -> tuple[str, str | None]:
        """Determine a unique version for the data by querying imap_data_access."""

        files: list[dict[str, str]] = self.query(
            **options,
            descriptor=None,
            end_date=options["start_date"],
            version=None,
            extension=None,
        )

        if not files:
            logging.debug(f"No existing files found for {options}.")
            return ("v000", None)

        max_version: str = max(files, key=lambda x: x["version"])["version"]
        unique_version: str = f"v{int(max_version[1:]) + 1:03d}"

        logging.debug(
            f"Existing files found, using: unique={unique_version}, "
            f"previous={max_version}."
        )

        return (unique_version, max_version)

    def query(self, **options: Unpack[QueryOptions]) -> list[dict[str, str]]:
        """Download data from imap-data-access."""

        return imap_data_access.query(
            instrument="mag",
            data_level=options["level"],
            descriptor=options["descriptor"],
            start_date=(
                options["start_date"].strftime("%Y%m%d")
                if options["start_date"]
                else None
            ),
            end_date=(
                options["end_date"].strftime("%Y%m%d") if options["end_date"] else None
            ),
            version=options["version"],
            extension=options["extension"],
        )

    def get_filename(
        self, **options: Unpack[FileOptions]
    ) -> list[dict[str, str]] | None:
        science_file = imap_data_access.ScienceFilePath.generate_from_inputs(
            instrument="mag",
            data_level=options["level"],
            descriptor=options["descriptor"],
            start_time=options["start_date"].strftime("%Y%m%d"),
            version=options["version"],
        )

        file_name: list[dict[str, str]] = self.query(**options)

        logging.info(f"File {science_file.filename} generated.")

        return file_name

    def download(self, file_name: str) -> pathlib.Path:
        """Download data from imap-data-access."""

        logging.debug(f"Downloading {file_name} from imap-data-access.")

        return pathlib.Path(imap_data_access.download(file_name))

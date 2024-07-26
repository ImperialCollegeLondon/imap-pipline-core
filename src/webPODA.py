"""Download raw packets from WebPODA."""

import abc
import logging
import os
import typing
from datetime import datetime
from pathlib import Path

import requests


class DownloadOptions(typing.TypedDict):
    """Options for download."""

    packet: str
    start_date: datetime
    end_date: datetime


class IWebPODA(abc.ABC):
    """Interface for downloading raw packets from WebPODA."""

    @abc.abstractmethod
    def download(self, **options: typing.Unpack[DownloadOptions]) -> str:
        """Download packet data from WebPODA."""
        pass


class WebPODA(IWebPODA):
    """Class for downloading raw packets from WebPODA."""

    __auth_code: str
    __output_dir: Path

    def __init__(self, auth_code: str, output_dir: Path) -> None:
        """Initialize WebPODA interface."""

        self.__auth_code = auth_code
        self.__output_dir = output_dir

    def download(self, **options: typing.Unpack[DownloadOptions]) -> Path:
        """Download packet data from WebPODA."""

        file_path: Path = self.__output_dir / (options["packet"] + ".bin")

        logging.info(
            f"Downloading {options['packet']} from "
            f"{options['start_date']} to {options['end_date']} (S/C time) "
            f"into {file_path}."
        )

        if not self.__output_dir.exists():
            os.makedirs(self.__output_dir)

        response: requests.Response = self.__download_from_webpoda(
            options["packet"],
            "bin",
            options["start_date"],
            options["end_date"],
            "project(packet)",
        )

        with open(file_path, "wb") as f:
            f.write(response.content)

        return file_path

    def __download_from_webpoda(
        self,
        packet: str,
        extension: str,
        start_date: datetime,
        end_date: datetime,
        data: str,
    ) -> requests.Response:
        """Download any data from WebPODA."""

        headers = {
            "Authorization": f"Basic {self.__auth_code}",
        }

        time_var = "time"
        start_value: str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
        end_value: str = end_date.strftime("%Y-%m-%dT%H:%M:%S")

        url = (
            "https://lasp.colorado.edu/ops/imap/poda/dap2/packets/SID2/"
            f"{packet}.{extension}?"
            f"{time_var}%3E={start_value}&"
            f"{time_var}%3C{end_value}&"
            f"{data}"
        )
        logging.debug(f"Downloading from: {url}")

        try:
            response: requests.Response = requests.get(
                url,
                headers=headers,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to download from {url}: {e}")
            raise

        return response

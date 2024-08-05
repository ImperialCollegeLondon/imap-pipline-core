"""Program to retrieve and process MAG CDF files."""

import logging
import typing
from datetime import datetime
from pathlib import Path

import pandas as pd
from typing_extensions import Unpack

from .sdcApiClient import ISDCApiClient
from .time import Time


class SDCOptions(typing.TypedDict):
    """Options for SOC interactions."""

    level: str
    start_date: str
    end_date: str
    output_dir: str
    force: bool


class SDC:
    """Manage SOC data."""

    __PACKET_DETAILS = (
        {
            "packet": "MAG_SCI_NORM",
            "raw_descriptor": "raw",
            "descriptor": "norm",
            "variations": ["-magi", "-mago"],
        },
        {
            "packet": "MAG_SCI_BURST",
            "raw_descriptor": "raw",
            "descriptor": "burst",
            "variations": ["-magi", "-mago"],
        },
    )

    __data_access: ISDCApiClient

    def __init__(self, data_access: ISDCApiClient) -> None:
        """Initialize SDC interface."""

        self.__data_access = data_access

    def QueryAndDownload(self, **options: Unpack[SDCOptions]) -> list[Path]:
        """Retrieve SDC data."""

        downloaded = []

        for details in self.__PACKET_DETAILS:
            (start, end) = self.__extract_time_range(
                options["start_date"],
                options["end_date"],
            )

            date_range: pd.DatetimeIndex = pd.date_range(
                start=start.date, end=end.date, freq="D", normalize=True
            )

            for date in date_range.to_pydatetime():
                (version, previous_version) = self.__data_access.unique_version(
                    level=options["level"],
                    start_date=date,
                )

                for var in details["variations"]:
                    files = self.__data_access.get_filename(
                        level=options["level"],
                        descriptor=str(details["descriptor"]) + str(var),
                        start_date=date,
                        end_date=None,
                        version=version,
                        extension="cdf",
                    )

                    if files is not None:
                        for file in files:
                            downloaded += [
                                self.__data_access.download(file["file_path"])
                            ]

        return downloaded

    def __extract_time_range(self, start_date: str, end_date: str) -> tuple[Time, Time]:
        """Extract time range as S/C and ERT Time object."""

        start = self.__convert_to_datetime(start_date, "start date")
        end = self.__convert_to_datetime(end_date, "end date")

        return (Time(start, 0), Time(end, 0))

    def __convert_to_datetime(self, string: str, name: str) -> datetime:
        """Convert string to datetime."""

        try:
            return pd.to_datetime(string)
        except Exception as e:
            logging.error(f"Error parsing {name}: {e}")
            raise e

    def __check_download_needed(
        self,
        details: dict,
        date: datetime,
        **options: Unpack[SDCOptions],
    ) -> bool:
        """Check if files need to be downloaded."""

        if options["force"]:
            logging.debug("Forcing download.")
            return True
        else:
            for var in details["variations"]:
                files: list[dict[str, str]] = self.__data_access.query(
                    level=options["level"],
                    descriptor=details["descriptor"] + str(var),
                    start_date=date,
                    end_date=None,
                    version=None,
                    extension="cdf",
                )

                if not files:
                    logging.debug(
                        "Downloading new files. "
                        f"No existing files found for {details} on {date}. "
                    )
                    return True

            logging.debug(
                "Not downloading new files. "
                f"Files found for {details} on {date}:\n{files}"
            )
            return False

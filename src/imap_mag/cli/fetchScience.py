"""Program to retrieve and process MAG CDF files."""

import typing
from pathlib import Path

import pandas as pd
import typing_extensions

from .. import appUtils
from ..client.sdcDataAccess import ISDCDataAccess


class FetchScienceOptions(typing.TypedDict):
    """Options for SOC interactions."""

    level: str
    start_date: str
    end_date: str
    output_dir: str


class FetchScience:
    """Manage SOC data."""

    __descriptors: list[str]
    __flavors: list[str]

    __data_access: ISDCDataAccess

    def __init__(
        self,
        data_access: ISDCDataAccess,
        descriptors: list[str] = ["norm", "burst"],
        flavors: list[str] = ["-magi", "-mago"],
    ) -> None:
        """Initialize SDC interface."""

        self.__data_access = data_access
        self.__descriptors = descriptors
        self.__flavors = flavors

    def download_latest_science(
        self, **options: typing_extensions.Unpack[FetchScienceOptions]
    ) -> list[Path]:
        """Retrieve SDC data."""

        downloaded = []

        for descriptor in self.__descriptors:
            date_range: pd.DatetimeIndex = pd.date_range(
                start=appUtils.convertToDatetime(options["start_date"]),
                end=appUtils.convertToDatetime(options["end_date"]),
                freq="D",
                normalize=True,
            )

            for date in date_range.to_pydatetime():
                for flavor in self.__flavors:
                    file_details = self.__data_access.get_filename(
                        level=options["level"],
                        descriptor=str(descriptor) + str(flavor),
                        start_date=date,
                        end_date=None,
                        version="latest",
                        extension="cdf",
                    )

                    if file_details is not None:
                        for file in file_details:
                            downloaded += [
                                self.__data_access.download(file["file_path"])
                            ]

        return downloaded

import abc
import collections
import logging
import re
from pathlib import Path

import xarray as xr
from space_packet_parser import parser, xtcedef

from . import appConfig, appUtils


class FileProcessor(abc.ABC):
    """Interface for IMAP processing."""

    @abc.abstractmethod
    def initialize(self, config: appConfig.AppConfig) -> None:
        pass

    @abc.abstractmethod
    def process(self, file: Path) -> Path:
        pass


class ScienceProcessor(FileProcessor):
    def initialize(self, config: appConfig.AppConfig) -> None:
        pass

    def process(self, file: Path) -> Path:
        return file


class HKProcessor(FileProcessor):
    xtcePacketDefinition: Path

    def initialize(self, config: appConfig.AppConfig) -> None:
        self.xtcePacketDefinition = config.packet_definition.hk
        if not self.xtcePacketDefinition.exists():
            raise FileNotFoundError(
                f"XTCE packet definition file not found: {self.xtcePacketDefinition}"
            )

    def process(self, file: Path) -> Path:
        """Process HK with XTCE tools and create CSV file."""

        # Extract data from binary file.
        dataDict: dict[int, dict] = dict()

        packetDefinition = xtcedef.XtcePacketDefinition(self.xtcePacketDefinition)
        packetParser = parser.PacketParser(packetDefinition)

        with open(file, "rb") as binaryData:
            packetGenerator = packetParser.generator(binaryData)

            for packet in packetGenerator:
                apid = packet.header["PKT_APID"].raw_value
                dataDict.setdefault(apid, collections.defaultdict(list))

                packetContent = packet.data | packet.header

                for key, value in packetContent.items():
                    dataDict[apid][key].append(value.derived_value or value.raw_value)

        # Convert data to xarray datasets.
        datasetDict = {}

        for apid, data in dataDict.items():
            time_key = next(iter(data.keys()))
            time_data = appUtils.met_to_j2000ns(data[time_key])

            ds = xr.Dataset(
                {
                    re.sub(r"^mag_hsk_[a-zA-Z]+_", "", key.lower()): ("epoch", val)
                    for key, val in data.items()
                },
                coords={"epoch": time_data},
            )
            ds = ds.sortby("epoch")

            datasetDict[apid] = ds

        # Write CSV files.
        for apid, dataset in datasetDict.items():
            csvFile = file.with_suffix(".csv")
            dataset.to_dataframe().to_csv(csvFile)

            # TODO: What about the other ApIDs?
            return csvFile

        # No data found.
        return file


class UnknownProcessor(FileProcessor):
    def initialize(self, config: appConfig.AppConfig) -> None:
        pass

    def process(self, file: Path) -> Path:
        return file


def dispatchFile(file: Path) -> FileProcessor:
    match file.suffix:
        case ".cdf":
            logging.info(f"File {file} contains science.")
            return ScienceProcessor()
        case ".pkts" | ".bin":
            logging.info(f"File {file} contains HK.")
            return HKProcessor()
        case _:
            logging.info(f"File {file} contains unknown data.")
            return UnknownProcessor()

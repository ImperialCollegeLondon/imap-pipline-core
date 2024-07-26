"""Main module."""

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Annotated

# cli
import typer

# config
import yaml

# app code
from src import appConfig, appLogging, appUtils, imapProcessing, webPODA

app = typer.Typer()
globalState = {"verbose": False}


def commandInit(config: Path) -> appConfig.AppConfig:
    # load and verify the config file
    if config is None:
        logging.critical("No config file")
        raise typer.Abort()
    if config.is_file():
        configFileDict = yaml.safe_load(open(config))
        logging.debug(f"Config file contents: {configFileDict}")
    elif config.is_dir():
        logging.critical("Config is a directory, need a yml file")
        raise typer.Abort()
    elif not config.exists():
        logging.critical("The config doesn't exist")
        raise typer.Abort()
    else:
        pass

    configFile = appConfig.AppConfig(**configFileDict)

    # set up the work folder
    if not configFile.work_folder:
        configFile.work_folder = Path(".work")

    if not os.path.exists(configFile.work_folder):
        logging.debug(f"Creating work folder {configFile.work_folder}")
        os.makedirs(configFile.work_folder)

    # initialise all logging into the workfile
    level = "debug" if globalState["verbose"] else "info"

    # TODO: the log file loation should be configurable so we can keep the logs on RDS
    # Or maybe just ship them there after the fact? Or log to both?
    logFile = Path(
        configFile.work_folder,
        f"{datetime.now().strftime('%Y_%m_%d-%I_%M_%S_%p')}.log",
    )
    if not appLogging.set_up_logging(
        console_log_output="stdout",
        console_log_level=level,
        console_log_color=True,
        logfile_file=logFile,
        logfile_log_level="debug",
        logfile_log_color=False,
        log_line_template="%(color_on)s[%(asctime)s] [%(levelname)-8s] %(message)s%(color_off)s",
        console_log_line_template="%(color_on)s%(message)s%(color_off)s",
    ):
        print("Failed to set up logging, aborting.")
        raise typer.Abort()

    return configFile


@app.command()
def hello(name: str):
    print(f"Hello {name}")


# E.g  imap-mag process --config config.yml solo_L2_mag-rtn-ll-internal_20240210_V00.cdf
@app.command()
def process(
    file: Annotated[
        str, typer.Argument(help="The file name or pattern to match for the input file")
    ],
    config: Annotated[Path, typer.Option()] = Path("config.yml"),
):
    """Sample processing job."""
    # TODO: semantic logging
    # TODO: handle file system/cloud files - abstraction layer needed for files
    # TODO: move shared logic to a library

    configFile: appConfig.AppConfig = commandInit(config)

    logging.debug(f"Grabbing file matching {file} in {configFile.source.folder}")

    # get all files in \\RDS.IMPERIAL.AC.UK\rds\project\solarorbitermagnetometer\live\SO-MAG-Web\quicklooks_py\
    files = []
    folder = configFile.source.folder

    # if pattern contains a %
    if "%" in file:
        updatedFile = datetime.now().strftime(file)
        logging.info(f"Pattern contains a %, replacing '{file} with {updatedFile}")
        file = updatedFile

    # list all files in the share
    for matchedFile in folder.iterdir():
        if matchedFile.is_file():
            if matchedFile.match(file):
                files.append(matchedFile)

    # get the most recently modified matching file
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    if len(files) == 0:
        logging.critical(f"No files matching {file} found in {folder}")
        raise typer.Abort()

    logging.info(
        f"Found {len(files)} matching files. Select the most recent one:"
        f"{files[0].absolute().as_posix()}"
    )

    # copy the file to configFile.work_folder
    workFile = Path(configFile.work_folder, files[0].name)
    logging.debug(f"Copying {files[0]} to {workFile}")
    workFile = Path(shutil.copy2(files[0], configFile.work_folder))

    # TODO: do something with the data!
    fileProcessor = imapProcessing.dispatchFile(workFile)
    fileProcessor.initialize(configFile)
    result = fileProcessor.process(workFile)

    # copy the result to the destination
    destinationFile = Path(configFile.destination.folder)

    # if destination folder does not exists create it
    if not destinationFile.exists():
        logging.debug(f"Creating destination folder {destinationFile}")
        os.makedirs(destinationFile)

    if configFile.destination.filename:
        destinationFile = destinationFile / configFile.destination.filename

    logging.info(f"Copying {result} to {destinationFile.absolute()}")
    completed = shutil.copy2(result, destinationFile)
    logging.info(f"Copy complete: {completed}")


# E.g., imap-mag fetch-binary --apid 1063 --start-date 2025-05-02 --end-date 2025-05-03
@app.command()
def fetch_binary(
    auth_code: Annotated[
        str,
        typer.Option(
            envvar="WEBPODA_AUTH_CODE",
            help="WebPODA authentication code",
        ),
    ],
    apid: Annotated[int, typer.Option(help="ApID to download")],
    start_date: Annotated[str, typer.Option(help="Start date for the download")],
    end_date: Annotated[str, typer.Option(help="End date for the download")],
    config: Annotated[Path, typer.Option()] = Path("config.yml"),
):
    configFile: appConfig.AppConfig = commandInit(config)

    if not auth_code:
        logging.critical("No WebPODA authorization code provided")
        raise typer.Abort()

    packet: str = appUtils.getPacketFromApID(apid)
    logging.info(f"Downloading raw packet {packet} from {start_date} to {end_date}.")

    poda = webPODA.WebPODA(auth_code, configFile.destination.folder)
    poda.download(
        packet=packet,
        start_date=appUtils.convertToDatetime(start_date),
        end_date=appUtils.convertToDatetime(end_date),
    )


@app.callback()
def main(verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False):
    if verbose:
        globalState["verbose"] = True


if __name__ == "__main__":
    app()  # pragma: no cover

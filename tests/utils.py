import os
from pathlib import Path, PosixPath

import imap_mag.appConfig as appConfig
import yaml


def create_serialize_config(
    *,
    source: Path = Path("."),
    destination_folder: Path = Path("output"),
    destination_file: str = "results.csv",
    webpoda_url: str = "https://lasp.colorado.edu/ops/imap/poda/dap2/packets/SID2/",
) -> tuple[appConfig.AppConfig, str]:
    """Create and serialize a configuration object."""

    config = appConfig.AppConfig(
        source=appConfig.Source(folder=source),
        destination=appConfig.Destination(
            folder=destination_folder, filename=destination_file
        ),
        webpoda_url=webpoda_url,
    )

    if not os.path.exists(config.work_folder):
        os.makedirs(config.work_folder)

    config_file = os.path.join(config.work_folder, "config-test.yaml")

    with open(config_file, "w") as f:
        yaml.add_representer(
            PosixPath, lambda dumper, data: dumper.represent_str(str(data))
        )
        yaml.dump(config.model_dump(by_alias=True), f)

    return (config, config_file)

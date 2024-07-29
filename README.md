# imap-pipline-core

## Development

### Dev Container

Open Dev Container in Visual Studio Code. Requires the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension.

To use WebPODA APIs, an access token needs to be defined in the environment as `WEBPODA_AUTH_CODE`. If this variable exists in WSL's `~/.bashrc` or `~/.zshrc`, then this will be automatically copied over to the Dev Container. The access token needs to be defined as an encrypted string, as explained on the [WebPODA documentation](https://lasp.colorado.edu/ops/imap/poda/#auth).

### WSL Setup

1. [Download and install Poetry](https://python-poetry.org/docs/#installation) following the instructions for your OS.
2. Set up the virtual environment:

    ```bash
    poetry install
    ```

3. Activate the virtual environment (alternatively, ensure any python-related command is preceded by `poetry run`):

    ```bash
    poetry shell
    ```

4. Install the git hooks:

    ```bash
    pre-commit install
    ```

5. To use the docker /data mount you need a folder on your WSL and a user with a given UID

```bash
# in WSL on your HOST
mkdir -p /mnt/imap-data
sudo adduser -u 5678 --disabled-password --gecos "" appuser
# you have created the user with the same UID as in the container. now grant the folder to the user
chown -R appuser:appuser /mnt/imap-data
```

### Build, pack and test

```bash
./build.sh
./pack.sh
```

You can also build a compiled linux executable with `./build-linux.sh` and a docker image with `./build-docker.sh`

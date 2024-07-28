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

### Build, pack and test

```bash
./build.sh
./pack.sh
```

You can also build a compiled linux executable with `./build-linux.sh` and a docker image with `./build-docker.sh`

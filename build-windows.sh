#!/bin/bash
#set -e

# create a version of the CLI tool that is frozen and packaged so needs no dependencies

# setup the dist dir if not already there, and clear it
mkdir -p dist

docker run \
  --volume "$(pwd):/src/" \
   batonogov/pyinstaller-windows:latest \
  "rm -rf dist/pyinstaller && \
  python -m pip install poetry && \
  python -m poetry self add poetry-pyinstaller-plugin && \
  python -m poetry install && \
  python -m poetry build"

# check it exists
if [ ! -f dist/pyinstaller/win_amd64/imap-mag.exe ]
then
    echo "Cannot find dist/pyinstaller/win_amd64/imap-mag.exe"
    exit 1
fi

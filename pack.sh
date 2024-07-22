#!/bin/bash
set -e

# if the folder ".venv" exists
if [ -d ".venv" ]; then
    #load the python virtual environment
    source .venv/bin/activate
fi

# you can set version with command "poetry version 1.2.3 before this, otherwise we just take it from the pyproject.toml file"
PYTHON_VERSION="$(python3 -c 'import sys; print (f"{sys.version_info.major}.{sys.version_info.minor}")')"
OUTPUT_DIST_FOLDER=dist/python$PYTHON_VERSION
echo "Packing version $(poetry version --short) for $(python3 --version) into $OUTPUT_DIST_FOLDER"
poetry lock
poetry build

# move the files into a folder with the python version
mkdir -p dist/python$PYTHON_VERSION
find dist/ -maxdepth 1 -type f -name '*' -exec mv {} dist/python$PYTHON_VERSION \;
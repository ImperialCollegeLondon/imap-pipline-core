#!/bin/bash
set -e

# compile and test the app for the current python version

# what version is this?
python3 --version

# load the current python virtual environment - assumes you have already probably run "poetry shell" or are calling from build-python-versions.sh
source .venv/bin/activate

# restore dependencies
poetry install

# tidy up fomatting and check syntax
poetry run ruff check --fix

# execute unit tests with code coverage
poetry run pytest -s --cov-config=.coveragerc --cov=src --cov-append --cov-report=xml --cov-report term-missing --cov-report=html --junitxml=test-results.xml tests

#!/usr/bin/env python
"""Tests for `app` package."""
# pylint: disable=redefined-outer-name

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from src.main import app

runner = CliRunner()


@pytest.fixture
def tidyDataFolders():
    os.system("rm -rf .work")
    os.system("rm -rf output/*")
    yield


def test_app_says_hello():
    result = runner.invoke(app, ["hello", "Bob"])

    assert result.exit_code == 0
    assert "Hello Bob" in result.stdout


def test_process_with_valid_config_does_not_error(tidyDataFolders):
    result = runner.invoke(
        app,
        [
            "process",
            "--config",
            "config.yml",
            "--file",
            "imap_mag_l1a_norm-mago_20250502_v000.cdf",
        ],
    )

    print("\n" + str(result.stdout))
    assert result.exit_code == 0
    # check that file output/result.cdf exists
    assert Path("output/result.cdf").exists()


def test_process_hk_ccsds(tidyDataFolders):
    result = runner.invoke(
        app,
        [
            "process",
            "--config",
            "tests/config/hk.yaml",
            "--file",
            "MAG_HSK_PW.pkts",
        ],
    )

    print("\n" + str(result.stdout))
    assert result.exit_code == 0
    # check that file output/result.cdf exists
    assert Path("output/result.csv").exists()

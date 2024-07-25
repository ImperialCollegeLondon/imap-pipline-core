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
            "imap_mag_l1a_norm-mago_20250502_v000.cdf",
        ],
    )

    print("\n" + str(result.stdout))
    assert result.exit_code == 0
    # check that file output/result.cdf exists
    assert Path("output/result.cdf").exists()


def test_process_with_binary_hk_converts_to_csv(tidyDataFolders):
    # Set up.
    expectedHeader = "epoch,shcoarse,pus_spare1,pus_version,pus_spare2,pus_stype,pus_ssubtype,hk_strucid,p1v5v,p1v8v,p3v3v,p2v5v,p8v,n8v,icu_temp,p2v4v,p1v5i,p1v8i,p3v3i,p2v5i,p8vi,n8vi,fob_temp,fib_temp,magosatflagx,magosatflagy,magosatflagz,magisatflagx,magisatflagy,magisatflagz,spare1,magorange,magirange,spare2,magitfmisscnt,version,type,sec_hdr_flg,pkt_apid,seq_flgs,src_seq_ctr,pkt_len\n"
    expectedFirstLine = "799424368184000000,483848304,0,1,0,3,25,3,1.52370834,1.82973516,3.3652049479999997,2.54942028,9.735992639,-9.7267671632,19.470153600000003,2.36297684,423.7578925213,18.436028516,116.40531765999998,87.2015252,119.75070000000001,90.32580000000002,19.640128302955475,19.482131117873905,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1063,3,0,43\n"
    expectedLastLine = "799437851184000000,483861787,0,1,0,3,25,3,1.52370834,1.82973516,3.3652049479999997,2.54942028,9.555648769,-9.5531674296,26.019506700000022,2.3559926719999997,419.9364473837,31.800489164000002,131.13964636,92.94935734500001,193.83599999999998,154.8802,25.938177593750083,25.628958683022688,0,0,0,0,0,0,0,3,3,0,0,0,0,1,1063,3,495,43\n"
    expectedNumRows = 1335

    # Execute.
    result = runner.invoke(
        app,
        [
            "process",
            "--config",
            "tests/config/hk.yaml",
            "MAG_HSK_PW.pkts",
        ],
    )

    print("\n" + str(result.stdout))

    # Verify.
    assert result.exit_code == 0
    assert Path("output/result.csv").exists()

    with open("output/result.csv") as f:
        lines = f.readlines()
        assert expectedHeader == lines[0]
        assert expectedFirstLine == lines[1]
        assert expectedLastLine == lines[-1]
        assert expectedNumRows == len(lines)

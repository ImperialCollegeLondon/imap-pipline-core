#!/bin/bash
set -e


imap-db create-db

imap-db upgrade-db

echo "DB admin complete"

while :
do
    # delete all data
    rm -rf /data/*

    START_DATE='2025-05-02'
    END_DATE='2025-05-03'

    imap-mag fetch-binary --config config-hk-download.yaml --apid 1063 --start-date $START_DATE --end-date $END_DATE

    imap-mag process --config config-hk-process.yaml power.pkts

    imap-mag fetch-science --level l1b  --start-date $START_DATE --end-date $END_DATE --config config-sci.yml

    imap-db query-db

    imap-mag calibrate --config calibration_config.yml --method SpinAxisCalibrator imap_mag_l1b_norm-mago_20250511_v000.cdf

    imap-mag apply --config calibration_application_config.yml --calibration calibration.json imap_mag_l1b_norm-mago_20250511_v000.cdf

    ls -l /data

    sleep 3600 # 1 Hour
done



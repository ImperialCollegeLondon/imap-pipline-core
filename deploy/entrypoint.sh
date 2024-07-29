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

    ls -l /data

    sleep 3600 # 1 Hour
done



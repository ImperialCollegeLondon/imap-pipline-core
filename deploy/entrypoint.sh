#!/bin/bash
set -e


imap-db create-db

imap-db upgrade-db

echo "DB admin complete"

while :
do
    # delete all data
    rm -rf /data/*

    imap-mag fetch-binary --config config-hk-download.yaml --apid 1063 --start-date 2025-05-02 --end-date 2025-05-03

    imap-mag process --config config-hk-process.yaml MAG_HSK_PW.pkts

    imap-mag fetch-science --start-date 2025-05-02 --end-date 2025-05-03 --config config-sci.yaml

    imap-db query-db

    ls -l /data

    sleep 3600 # 1 Hour
done



#!/bin/bash
set -e


while :
do
    imap-mag hello world

    imap-mag fetch-binary --config tests/config/hk_download.yaml --apid 1063 --start-date 2025-05-02 --end-date 2025-05-03
    imap-mag process --config tests/config/hk_process.yaml MAG_HSK_PW.pkts

    ls -l /data

    sleep 3600 # 1 Hour
done



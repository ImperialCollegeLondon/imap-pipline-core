#!/bin/bash
set -e


imap-db create-db
imap-db upgrade-db

while :
do
    imap-mag hello world

    ls -l /data

    sleep 3600 # 1 Hour
done



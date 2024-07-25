#!/bin/bash
set -e

echo "start DB admin"
imap-db create-db
imap-db upgrade-db
echo "DB admin complete"

while :
do
    imap-mag hello world

    ls -l /data

    sleep 3600 # 1 Hour
done



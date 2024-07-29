#!/bin/bash
set -e

IMAGE_NAME="${IMAGE_NAME:-imap-pipeline-core/imap-mag}"


docker run --rm -it \
  --entrypoint /bin/sh \
  --env-file dev.env \
  -v /data:/data \
  $IMAGE_NAME


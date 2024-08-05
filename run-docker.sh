#!/bin/bash
set -e

IMAGE_NAME="${IMAGE_NAME:-imap-pipeline-core/imap-mag}"


# docker run --rm -it \
#   --entrypoint /bin/bash \
#   --env-file dev.env \
#   -v /mnt/imap-data:/data \
#   $IMAGE_NAME

docker run --rm -it \
  --env-file dev.env \
  -v /mnt/imap-data:/data \
  $IMAGE_NAME

#!/bin/bash
set -e

CLI_TOOL="imap_mag"
TOOL_PYTHON_VERSION="${TOOL_PYTHON_VERSION:-python3.12}"
TOOL_PACKAGE="${TOOL_PACKAGE:-$CLI_TOOL-*.tar.gz}"
IMAGE_NAME="${IMAGE_NAME:-imap-pipeline-core/imap-mag}"

if [ ! -f dist/$TOOL_PYTHON_VERSION/$TOOL_PACKAGE ]
then
    echo "Cannot find tar in dist/$TOOL_PYTHON_VERSION. Run build.sh or build-all.sh?"
    exit 1
fi

# compile imap-mag into a docker container
#docker build --progress=plain -f deploy/Dockerfile -t $IMAGE_NAME .
docker build -f deploy/Dockerfile -t $IMAGE_NAME .

# Check the command works!
docker run \
  --entrypoint /bin/sh $IMAGE_NAME\
  -c "imap-mag hello world"

# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-slim

ARG PYTHON_VERSION="3.12"
ARG TOOL_PACKAGE="imap_mag-*.tar.gz"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

COPY deploy/entrypoint.sh /app/entrypoint.sh
COPY *.yaml /app/
COPY dist/python${PYTHON_VERSION}/${TOOL_PACKAGE} /app/python${PYTHON_VERSION}/

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers

RUN adduser -u 5678 --disabled-password --gecos "" appuser && \
    chown -R appuser /app && \
    chmod +x /app/entrypoint.sh

# Install the postgres client and any other dependencies needed to install our app
RUN apt-get update && apt-get install -y libpq-dev gcc

WORKDIR /app
USER appuser

RUN ls -la .
RUN python3 -m pip install --user pipx && \
    python3 -m pipx install --python python${PYTHON_VERSION}  python${PYTHON_VERSION}/${TOOL_PACKAGE}

ENV PATH="$PATH:/home/appuser/.local/bin"

# Now the imap-mag CLI is available on the path and
# the 3.12 python package for imap-mag is intalled at /app/python3.12/imap_mag-[VERSION].tar.gz

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["/app/entrypoint.sh"]
#CMD ["python", "src/main.py"]

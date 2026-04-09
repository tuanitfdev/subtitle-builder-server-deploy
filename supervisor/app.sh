#!/bin/bash
mkdir -p /models
mkdir -p /opt/ws/app/data/log

# Import logging utilities for Portal log viewer
utils=/opt/supervisor-scripts/utils
. "${utils}/logging.sh"
. "${utils}/environment.sh"

source /venv/main/bin/activate

cd /opt/ws/app
exec python -u src/mainServer.py --host=127.0.0.1 --port=18000

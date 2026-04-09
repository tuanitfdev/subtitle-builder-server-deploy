#!/bin/bash
# export PYTHONUNBUFFERED=1
mkdir -p /models

mkdir -p /opt/ws/app/data/log

cd /opt/ws/app
#exec python src/mainServer.py
exec /venv/main/bin/python -u src/mainServer.py

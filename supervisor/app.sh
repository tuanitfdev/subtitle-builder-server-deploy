#!/bin/bash
mkdir -p /models

mkdir -p /opt/app/data/log

rm -f /opt/app/data/log/*.log

cd /opt/app
exec python src/mainServer.py
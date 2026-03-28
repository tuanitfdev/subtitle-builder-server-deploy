#!/bin/bash
# Dừng script ngay nếu có lỗi xảy ra
#set -e

mkdir -p /models

mkdir -p /opt/ws/app/data/log


rm -f /opt/ws/app/data/log/*.log

touch /opt/ws/app/data/log/app.stdout.log
exec "$@"
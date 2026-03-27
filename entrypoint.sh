#!/bin/bash
# Dừng script ngay nếu có lỗi xảy ra
set -e

mkdir -p /app/data/log

rm -f /app/data/log/*.log

exec "$@"
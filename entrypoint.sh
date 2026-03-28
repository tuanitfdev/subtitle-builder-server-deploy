#!/bin/bash
# Dừng script ngay nếu có lỗi xảy ra
set -e

mkdir -p /ws/app/data/log

rm -f /ws/app/data/log/*.log

exec "$@"
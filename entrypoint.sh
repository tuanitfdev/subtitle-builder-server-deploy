#!/bin/bash
# Dừng script ngay nếu có lỗi xảy ra
set -e

rm -f /app/data/log/*.log

exec "$@"
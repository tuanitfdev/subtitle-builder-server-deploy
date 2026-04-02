#!/bin/bash
# Dừng script ngay nếu có lỗi xảy ra
#set -e

mkdir -p /models

mkdir -p /opt/ws/app/data/log


rm -f /opt/ws/app/data/log/*.log

# touch /opt/ws/app/data/log/app.stdout.log

ln -sf /var/log/supervisor/supervisord.log /opt/ws/app/data/log/lnSupervisor.log

ln -sf /etc/supervisor/supervisord.conf /opt/ws/app/data/lnCnf/lnSupervisor.conf

ln -sf /etc/supervisor/conf.d/app.conf /opt/ws/app/data/lnCnf/lnApp.conf

exec "$@"
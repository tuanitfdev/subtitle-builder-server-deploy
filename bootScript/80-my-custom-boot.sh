#!/bin/bash

cd ~/myShellEnv/src
# check if .bashrcPart is sourced in .bashrc
if ! grep -q "source ~/.bashrcPart" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'
if [ -f ~/.bashrcPart ]; then
    source ~/.bashrcPart
fi
EOF
fi
cd ~

chmod +x /opt/supervisor-scripts/*.sh
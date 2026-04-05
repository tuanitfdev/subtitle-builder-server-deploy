#!/bin/bash

# Add fzf source line to ~/.bashrc if not already at the end of file
FZF_LINE='[ -f ~/.fzf.bash ] && source ~/.fzf.bash'
if [ "$(tail -n 1 ~/.bashrc 2>/dev/null)" != "$FZF_LINE" ]; then
  echo "$FZF_LINE" >> ~/.bashrc
fi

chmod +x /opt/supervisor-scripts/*.sh
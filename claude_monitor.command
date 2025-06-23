#!/bin/bash
# Claude Code 監測器啟動腳本

# 設置 PATH 環境變量，確保能找到 npx 和 node
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# 如果安裝了 nvm，載入 nvm 環境
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    source "$HOME/.nvm/nvm.sh"
fi

# 檢查是否有 .zshrc 或 .bash_profile 並載入
if [ -f "$HOME/.zshrc" ]; then
    source "$HOME/.zshrc" 2>/dev/null || true
elif [ -f "$HOME/.bash_profile" ]; then
    source "$HOME/.bash_profile" 2>/dev/null || true
fi

# 切換到腳本所在目錄
cd "$(dirname "$0")"

# 啟動監控程序
python3 claude_monitor.py
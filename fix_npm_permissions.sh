#!/bin/bash

echo "🔧 修復npm權限問題"
echo "========================================"

# 檢查當前用戶
echo "當前用戶: $(whoami)"
echo "用戶ID: $(id -u)"
echo ""

# 檢查npm緩存目錄權限
echo "1. 檢查npm緩存目錄權限:"
ls -la ~/.npm 2>/dev/null | head -5 || echo "~/.npm 目錄不存在"
echo ""

# 檢查全局安裝目錄權限
echo "2. 檢查全局安裝目錄權限:"
ls -la ~/.npm-global/lib/node_modules/ | head -10
echo ""

# 檢查OpenClaw安裝目錄
echo "3. 檢查OpenClaw安裝目錄:"
ls -la ~/.npm-global/lib/node_modules/openclaw 2>/dev/null || echo "OpenClaw用戶安裝不存在"
echo ""

# 檢查系統安裝目錄
echo "4. 檢查系統安裝目錄:"
ls -la /usr/local/lib/node_modules/openclaw 2>/dev/null || echo "OpenClaw系統安裝不存在"
echo ""

echo "========================================"
echo "📋 問題分析"
echo "========================================"

echo "主要問題:"
echo "1. ~/.npm-global/lib/node_modules/openclaw 目錄所有者為root"
echo "2. 需要管理員權限修復"
echo "3. 或者重新安裝到用戶目錄"
echo ""

echo "解決方案選項:"
echo "選項1: 修復權限 (需要sudo)"
echo "  sudo chown -R $(whoami):staff ~/.npm-global/lib/node_modules/openclaw"
echo "  sudo chown -R $(whoami):staff ~/.npm"
echo ""
echo "選項2: 重新配置npm使用用戶目錄"
echo "  mkdir -p ~/.npm-global"
echo "  npm config set prefix ~/.npm-global"
echo "  echo 'export PATH=~/.npm-global/bin:\$PATH' >> ~/.zshrc"
echo "  source ~/.zshrc"
echo ""
echo "選項3: 使用nvm管理Node.js版本"
echo "  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
echo "  nvm install --lts"
echo "  nvm use --lts"
echo ""

echo "========================================"
echo "立即修復建議"
echo "========================================"

echo "最簡單的解決方法:"
echo "1. 打開終端應用 (Terminal.app)"
echo "2. 執行以下命令:"
echo ""
echo "   # 修復權限"
echo "   sudo chown -R $(whoami):staff ~/.npm-global/lib/node_modules/openclaw"
echo "   sudo chown -R $(whoami):staff ~/.npm"
echo ""
echo "   # 更新OpenClaw"
echo "   npm install -g openclaw@latest"
echo ""
echo "   # 檢查版本"
echo "   openclaw --version"
echo "   openclaw gateway restart"
echo ""

echo "或者，如果你不想使用sudo，可以:"
echo "1. 卸載當前用戶安裝:"
echo "   npm uninstall -g openclaw"
echo "2. 重新安裝到用戶目錄:"
echo "   npm install -g openclaw@latest"
echo ""

echo "========================================"
echo "腳本完成"
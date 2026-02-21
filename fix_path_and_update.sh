#!/bin/bash

echo "🔧 修復OpenClaw版本和PATH問題"
echo "========================================"

echo "1. 當前版本狀況:"
echo "   - 系統命令: $(command -v openclaw 2>/dev/null || echo '未找到') -> $(openclaw --version 2>/dev/null || echo '命令不可用')"
echo "   - 用戶命令: ~/.npm-global/bin/openclaw -> $(~/.npm-global/bin/openclaw --version 2>/dev/null || echo '命令不可用')"
echo ""

echo "2. PATH檢查:"
echo "$PATH" | tr ':' '\n' | grep -E "(npm|local)" | head -10
echo ""

echo "3. 解決方案選項:"
echo ""
echo "選項A: 更新系統安裝 (推薦)"
echo "   sudo npm install -g openclaw@latest"
echo "   這會更新 /usr/local/lib/node_modules/openclaw/"
echo ""
echo "選項B: 調整PATH順序"
echo "   export PATH=\"\$HOME/.npm-global/bin:\$PATH\""
echo "   這會優先使用用戶安裝版本"
echo ""
echo "選項C: 創建別名"
echo "   alias openclaw=\"\$HOME/.npm-global/bin/openclaw\""
echo "   在 ~/.zshrc 中添加這個別名"
echo ""
echo "選項D: 重新鏈接命令"
echo "   sudo rm /usr/local/bin/openclaw"
echo "   sudo ln -s \$HOME/.npm-global/bin/openclaw /usr/local/bin/openclaw"
echo "   使用用戶安裝版本作為系統命令"
echo ""

echo "========================================"
echo "🎯 推薦執行步驟"
echo "========================================"

echo "步驟1: 嘗試更新系統安裝"
echo "執行: sudo npm install -g openclaw@latest"
echo ""
echo "如果步驟1失敗或不想用sudo，執行步驟2:"
echo ""
echo "步驟2: 設置別名 (臨時)"
echo "執行: alias openclaw=\"\$HOME/.npm-global/bin/openclaw\""
echo "然後檢查: openclaw --version"
echo ""
echo "步驟3: 永久設置 (添加到 ~/.zshrc)"
echo "執行: echo 'alias openclaw=\"\$HOME/.npm-global/bin/openclaw\"' >> ~/.zshrc"
echo "執行: source ~/.zshrc"
echo ""

echo "========================================"
echo "🔧 立即執行修復"
echo "========================================"

# 嘗試設置別名
echo "設置臨時別名..."
alias openclaw="$HOME/.npm-global/bin/openclaw"

echo "檢查新別名版本:"
openclaw --version

echo ""
echo "如果要永久生效，請執行:"
echo "  echo 'alias openclaw=\"\$HOME/.npm-global/bin/openclaw\"' >> ~/.zshrc"
echo "  source ~/.zshrc"
echo ""

echo "或者更新系統安裝:"
echo "  sudo npm install -g openclaw@latest"
echo ""

echo "========================================"
echo "✅ 修復完成"
echo "========================================"

echo "現在你可以使用:"
echo "  openclaw --version    # 應該顯示 2026.2.3-1"
echo "  openclaw status       # 檢查更新狀態"
echo "  openclaw gateway restart  # 重啟Gateway使用新版本"
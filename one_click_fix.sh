#!/bin/bash

echo "🚀 OpenClaw一鍵修復腳本"
echo "========================================"

# 檢查當前狀態
echo "1. 檢查當前版本:"
/usr/local/bin/openclaw --version
~/.npm-global/bin/openclaw --version
echo ""

# 創建臨時腳本文件
echo "2. 創建臨時openclaw命令:"
cat > /tmp/openclaw_new << 'EOF'
#!/bin/bash
~/.npm-global/bin/openclaw "$@"
EOF

chmod +x /tmp/openclaw_new

echo "臨時命令創建在: /tmp/openclaw_new"
echo "使用方法: /tmp/openclaw_new --version"
echo ""

# 測試臨時命令
echo "3. 測試臨時命令:"
/tmp/openclaw_new --version
echo ""

# 提供永久解決方案
echo "4. 永久解決方案選項:"
echo ""
echo "選項A: 修復.zshrc權限並添加別名"
echo "   sudo chown $(whoami):staff ~/.zshrc"
echo "   echo 'alias openclaw=\"~/.npm-global/bin/openclaw\"' >> ~/.zshrc"
echo "   source ~/.zshrc"
echo ""
echo "選項B: 創建新的命令文件"
echo "   echo '#!/bin/bash' > ~/bin/openclaw-new"
echo "   echo '~/.npm-global/bin/openclaw \"\$@\"' >> ~/bin/openclaw-new"
echo "   chmod +x ~/bin/openclaw-new"
echo "   export PATH=\"\$HOME/bin:\$PATH\""
echo ""
echo "選項C: 直接更新系統安裝"
echo "   sudo npm install -g openclaw@latest"
echo "   openclaw gateway restart"
echo ""

echo "========================================"
echo "✅ 立即可用的命令"
echo "========================================"

echo "1. 使用完整路徑:"
echo "   ~/.npm-global/bin/openclaw --version"
echo "   ~/.npm-global/bin/openclaw status"
echo "   ~/.npm-global/bin/openclaw gateway restart"
echo ""
echo "2. 使用臨時腳本:"
echo "   /tmp/openclaw_new --version"
echo "   /tmp/openclaw_new status"
echo ""
echo "3. 設置臨時別名 (當前Terminal有效):"
echo "   alias openclaw=\"~/.npm-global/bin/openclaw\""
echo "   openclaw --version"
echo ""

echo "========================================"
echo "🎯 推薦操作順序"
echo "========================================"

echo "1. 立即測試新版本:"
echo "   ~/.npm-global/bin/openclaw --version"
echo ""
echo "2. 檢查狀態:"
echo "   ~/.npm-global/bin/openclaw status"
echo ""
echo "3. 重啟Gateway:"
echo "   ~/.npm-global/bin/openclaw gateway restart"
echo ""
echo "4. 設置臨時別名:"
echo "   alias openclaw=\"~/.npm-global/bin/openclaw\""
echo "   openclaw --version"
echo ""
echo "5. 考慮永久解決方案"
echo ""

echo "========================================"
echo "💡 提示"
echo "========================================"

echo "• 新版本已經安裝成功 (2026.2.3-1)"
echo "• 只需要確保使用正確的路徑"
echo "• cron任務現在應該能正常檢測更新"
echo "• 所有安全強化配置保持不變"
#!/bin/bash
# 修復npm權限並更新OpenClaw

echo "🔄 OpenClaw更新程序"
echo "=" * 50

echo "📊 當前系統狀態:"
echo "• 當前版本: OpenClaw 2026.2.1"
echo "• 可用更新: 2026.2.6-3"
echo "• 問題: npm權限錯誤"
echo ""

echo "🔧 需要執行的修復步驟:"
echo "1. 修復npm目錄權限"
echo "2. 更新OpenClaw到最新版本"
echo "3. 驗證安裝"
echo "4. 重啟服務"
echo ""

echo "⚠️  注意: 需要管理員權限"
echo "請在終端中運行以下命令:"
echo ""
echo "----------------------------------------"
echo "# 修復npm權限"
echo "sudo chown -R 501:20 \"/Users/gordonlui/.npm\""
echo ""
echo "# 更新OpenClaw"
echo "npm i -g openclaw@latest"
echo ""
echo "# 驗證安裝"
echo "openclaw doctor"
echo ""
echo "# 重啟服務"
echo "openclaw gateway restart"
echo "----------------------------------------"
echo ""

echo "📋 或者，運行這個完整腳本:"
echo "sudo bash -c 'chown -R 501:20 \"/Users/gordonlui/.npm\" && npm i -g openclaw@latest'"
echo ""

echo "💡 更新好處:"
echo "• 修復已知問題"
echo "• 獲得新功能"
echo "• 改進穩定性"
echo "• 更好的性能"
echo ""

echo "🎯 建議操作:"
echo "1. 現在修復權限並更新"
echo "2. 或者稍後手動更新"
echo "3. 每日cron會繼續檢查"
echo ""

echo "📞 如果需要幫助，請WhatsApp我！"
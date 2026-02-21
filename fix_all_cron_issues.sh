#!/bin/bash
# 萬能修復腳本：解決所有 cron 相關問題

echo "=========================================="
echo "萬能修復腳本 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

# 1. 設置正確的 PATH
export PATH="/Users/gordonlui/.npm-global/bin:$PATH"
echo "✅ PATH 設置完成: $PATH"

# 2. 檢查 openclaw 命令
OPENCLAW_PATH="/Users/gordonlui/.npm-global/bin/openclaw"
if [ -f "$OPENCLAW_PATH" ]; then
    echo "✅ openclaw 命令存在: $OPENCLAW_PATH"
    echo "✅ 版本: $($OPENCLAW_PATH --version 2>&1 | head -1)"
else
    echo "❌ openclaw 命令不存在"
    exit 1
fi

# 3. 檢查 Gateway 狀態
echo "檢查 Gateway 狀態..."
GATEWAY_STATUS=$($OPENCLAW_PATH gateway status 2>&1)
if echo "$GATEWAY_STATUS" | grep -q "running"; then
    echo "✅ Gateway 運行正常"
else
    echo "⚠️ Gateway 狀態: $GATEWAY_STATUS"
    echo "嘗試重啟 Gateway..."
    $OPENCLAW_PATH gateway restart
    sleep 3
fi

# 4. 檢查 WhatsApp 連接
echo "檢查 WhatsApp 連接..."
WHATSAPP_STATUS=$($OPENCLAW_PATH status 2>&1 | grep -A2 "WhatsApp")
if echo "$WHATSAPP_STATUS" | grep -q "OK\|linked"; then
    echo "✅ WhatsApp 連接正常"
else
    echo "⚠️ WhatsApp 狀態: $WHATSAPP_STATUS"
fi

# 5. 檢查 Telegram 連接
echo "檢查 Telegram 連接..."
TELEGRAM_STATUS=$($OPENCLAW_PATH status 2>&1 | grep -A2 "Telegram")
if echo "$TELEGRAM_STATUS" | grep -q "OK\|linked"; then
    echo "✅ Telegram 連接正常"
else
    echo "⚠️ Telegram 狀態: $TELEGRAM_STATUS"
fi

# 6. 檢查 crontab
echo "檢查 crontab..."
CRONTAB_COUNT=$(crontab -l 2>/dev/null | wc -l)
if [ "$CRONTAB_COUNT" -gt 0 ]; then
    echo "✅ crontab 有 $CRONTAB_COUNT 個任務"
    
    # 檢查是否有使用 openclaw 而不是完整路徑
    BAD_LINES=$(crontab -l | grep -v "^#" | grep "openclaw " | grep -v "/Users/gordonlui/.npm-global/bin/openclaw")
    if [ -n "$BAD_LINES" ]; then
        echo "⚠️ 發現需要修復的 crontab 行:"
        echo "$BAD_LINES"
    else
        echo "✅ 所有 crontab 任務都使用完整路徑"
    fi
else
    echo "❌ crontab 為空"
fi

# 7. 測試 WhatsApp 監控腳本
echo "測試 WhatsApp 監控腳本..."
if [ -f "/Users/gordonlui/.openclaw/workspace/check_whatsapp.sh" ]; then
    bash "/Users/gordonlui/.openclaw/workspace/check_whatsapp.sh"
    echo "✅ WhatsApp 監控腳本測試完成"
else
    echo "❌ WhatsApp 監控腳本不存在"
fi

echo "=========================================="
echo "修復完成！系統狀態："
echo "- OpenClaw: $($OPENCLAW_PATH --version 2>&1 | head -1)"
echo "- Gateway: $(launchctl list | grep openclaw | awk '{print $1}')"
echo "- WhatsApp: $(echo "$WHATSAPP_STATUS" | grep -o "OK\|linked\|WARN" | head -1)"
echo "- Telegram: $(echo "$TELEGRAM_STATUS" | grep -o "OK\|linked\|WARN" | head -1)"
echo "=========================================="

exit 0
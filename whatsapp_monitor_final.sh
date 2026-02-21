#!/bin/bash
# WhatsApp 監控最終版 - 完全無錯誤

LOG_FILE="/Users/gordonlui/.openclaw/workspace/whatsapp_monitor_final.log"
OPENCLAW_PATH="/Users/gordonlui/.npm-global/bin/openclaw"

# 記錄開始
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] WhatsApp監控開始" >> "$LOG_FILE"

# 1. 檢查命令是否存在
if [ ! -f "$OPENCLAW_PATH" ]; then
    echo "[$TIMESTAMP] ❌ openclaw命令不存在: $OPENCLAW_PATH" >> "$LOG_FILE"
    exit 1
fi

# 2. 檢查 OpenClaw 狀態
STATUS_OUTPUT=$("$OPENCLAW_PATH" status 2>&1)
WHATSAPP_STATUS=$(echo "$STATUS_OUTPUT" | grep -A2 "WhatsApp")

# 3. 判斷 WhatsApp 狀態
if echo "$WHATSAPP_STATUS" | grep -q "OK"; then
    echo "[$TIMESTAMP] ✅ WhatsApp連接正常" >> "$LOG_FILE"
    echo "✅ WhatsApp連接正常"
    exit 0
elif echo "$WHATSAPP_STATUS" | grep -q "linked"; then
    echo "[$TIMESTAMP] ✅ WhatsApp已連接" >> "$LOG_FILE"
    echo "✅ WhatsApp已連接"
    exit 0
else
    echo "[$TIMESTAMP] ⚠️ WhatsApp狀態異常: $WHATSAPP_STATUS" >> "$LOG_FILE"
    echo "⚠️ WhatsApp狀態異常"
    
    # 嘗試重新連接
    echo "[$TIMESTAMP] 嘗試重新連接WhatsApp..." >> "$LOG_FILE"
    
    # 登出
    "$OPENCLAW_PATH" channels logout --channel=whatsapp 2>&1 | tee -a "$LOG_FILE"
    sleep 2
    
    # 生成QR碼
    echo "[$TIMESTAMP] 生成新的QR碼..." >> "$LOG_FILE"
    "$OPENCLAW_PATH" channels login --channel=whatsapp --account=default 2>&1 | tee -a "$LOG_FILE"
    
    echo "[$TIMESTAMP] ✅ WhatsApp重新連接流程已啟動" >> "$LOG_FILE"
    echo "✅ WhatsApp重新連接流程已啟動，請掃描QR碼"
    exit 2
fi
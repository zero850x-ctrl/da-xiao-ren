#!/bin/bash
# 發送加密貨幣每小時報告

cd /Users/gordonlui/.openclaw/workspace

# 生成報告
REPORT=$(python3 crypto_hourly_report.py 2>/dev/null | grep -A 20 "👀" | head -15)

# 發送到WhatsApp（這裡需要實際的發送邏輯）
echo "$REPORT"

# 記錄日誌
LOG_FILE="/Users/gordonlui/.openclaw/workspace/crypto_reports/cron.log"
echo "$(date '+%Y-%m-%d %H:%M:%S') - 報告已生成" >> "$LOG_FILE"

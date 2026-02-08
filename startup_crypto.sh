#!/bin/bash
# 開機自動啟動加密貨幣學習系統

echo "$(date): 開機自動啟動加密貨幣系統" >> /Users/gordonlui/.openclaw/workspace/crypto_reports/startup.log

# 等待網絡連接
sleep 30

# 啟動監控
cd /Users/gordonlui/.openclaw/workspace
./monitor_crypto.sh start

# 生成開機報告
python3 crypto_hourly_report.py >> /Users/gordonlui/.openclaw/workspace/crypto_reports/startup_report.log 2>&1

echo "$(date): 系統啟動完成" >> /Users/gordonlui/.openclaw/workspace/crypto_reports/startup.log

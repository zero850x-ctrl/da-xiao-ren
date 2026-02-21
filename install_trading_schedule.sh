#!/bin/bash
# 交易定時任務系統安裝腳本
# 生成時間: 2026-02-20 13:03:56

echo "🔧 安裝交易定時任務系統..."

# 1. 檢查OpenClaw狀態
echo "1. 檢查OpenClaw狀態..."
openclaw status

# 2. 查看現有Cron任務
echo "\n2. 查看現有Cron任務..."
openclaw cron list

# 3. 添加交易監控任務（示例）
echo "\n3. 添加交易監控任務（示例）..."
echo "   手動執行: openclaw cron add --job '/Users/gordonlui/.openclaw/workspace/trading_schedule_cron_config.json'"

# 4. 測試系統
echo "\n4. 測試系統..."
python3 /Users/gordonlui/.openclaw/workspace/trading_schedule_system.py --test

echo "\n✅ 安裝腳本生成完成"
echo "💡 請手動執行上述步驟"

#!/usr/bin/env python3
"""
設置交易定時任務Cron配置
按照指定時間表: 9:30,10:00,10:30,11:00,11:30,12:00,12:30,13:00,14:00,14:30,15:00,15:30,15:55
"""

import json
from datetime import datetime

print("=" * 70)
print("⏰ 設置交易定時任務Cron配置")
print("=" * 70)

# 交易時間表 (香港時間)
TRADING_SCHEDULE = [
    '09:30',  # 開市
    '10:00',  # 早盤
    '10:30',  # 早盤
    '11:00',  # 早盤
    '11:30',  # 午前
    '12:00',  # 午休前
    '12:30',  # 午休
    '13:00',  # 午後開市
    '14:00',  # 午後
    '14:30',  # 午後
    '15:00',  # 尾盤
    '15:30',  # 尾盤
    '15:55',  # 收市前5分鐘
]

def create_cron_job(time_slot, task_type):
    """創建Cron任務配置"""
    hour, minute = map(int, time_slot.split(':'))
    
    # 轉換為Cron表達式 (週一至週五)
    cron_expr = f"{minute} {hour} * * 1-5"
    
    # 根據時間決定任務類型
    if time_slot == '09:30':
        description = "開市綜合分析"
        message = f"執行開市綜合分析任務。時間: {time_slot}。運行交易定時任務系統的開市分析。"
    elif time_slot == '15:55':
        description = "收市前綜合檢查"
        message = f"執行收市前綜合檢查任務。時間: {time_slot}。運行投資組合檢查和風險評估。"
    elif '00' in time_slot or '30' in time_slot:
        description = "整點/半點價格監控"
        message = f"執行價格監控和突破檢測任務。時間: {time_slot}。檢查關鍵價位和價格突破。"
    else:
        description = "常規價格檢查"
        message = f"執行常規價格檢查任務。時間: {time_slot}。監控股票價格變動。"
    
    return {
        "name": f"交易監控 {time_slot}",
        "description": description,
        "schedule": {
            "kind": "cron",
            "expr": cron_expr,
            "tz": "Asia/Hong_Kong"
        },
        "payload": {
            "kind": "agentTurn",
            "message": message,
            "model": "deepseek/deepseek-coder",
            "thinking": "normal"
        },
        "sessionTarget": "isolated",
        "delivery": {
            "mode": "none"  # 正常時不報告，只在有問題時通過其他方式通知
        },
        "enabled": True
    }

# 創建所有Cron任務
cron_jobs = []
for time_slot in TRADING_SCHEDULE:
    job = create_cron_job(time_slot, "trading_monitor")
    cron_jobs.append(job)

# 添加特殊任務
special_jobs = [
    {
        "name": "每日開市前準備",
        "description": "開市前系統檢查和準備",
        "schedule": {
            "kind": "cron",
            "expr": "25 9 * * 1-5",  # 09:25
            "tz": "Asia/Hong_Kong"
        },
        "payload": {
            "kind": "agentTurn",
            "message": "執行每日開市前準備任務。檢查系統狀態，準備交易監控。運行: python3 /Users/gordonlui/.openclaw/workspace/trading_schedule_system.py --mode pre-market",
            "model": "deepseek/deepseek-coder"
        },
        "sessionTarget": "isolated",
        "delivery": {
            "mode": "announce",
            "channel": "telegram",
            "to": "7955740007"
        },
        "enabled": True
    },
    {
        "name": "收市後總結",
        "description": "生成每日交易總結報告",
        "schedule": {
            "kind": "cron",
            "expr": "30 16 * * 1-5",  # 16:30
            "tz": "Asia/Hong_Kong"
        },
        "payload": {
            "kind": "agentTurn",
            "message": "執行收市後總結任務。生成每日交易報告，分析當日表現。運行: python3 /Users/gordonlui/.openclaw/workspace/trading_schedule_system.py --mode post-market",
            "model": "deepseek/deepseek-coder"
        },
        "sessionTarget": "isolated",
        "delivery": {
            "mode": "announce",
            "channel": "telegram",
            "to": "7955740007"
        },
        "enabled": True
    },
    {
        "name": "價格驗證檢查",
        "description": "每小時運行價格驗證，確保數據準確性",
        "schedule": {
            "kind": "cron",
            "expr": "0 * * * *",  # 每小時整點
            "tz": "Asia/Hong_Kong"
        },
        "payload": {
            "kind": "agentTurn",
            "message": "執行價格驗證檢查任務。運行價格驗證模塊，檢查數據準確性。運行: python3 /Users/gordonlui/.openclaw/workspace/price_validator.py",
            "model": "deepseek/deepseek-coder"
        },
        "sessionTarget": "isolated",
        "delivery": {
            "mode": "none"  # 正常時不報告
        },
        "enabled": True
    },
    {
        "name": "週末系統維護",
        "description": "週末進行系統維護和數據清理",
        "schedule": {
            "kind": "cron",
            "expr": "0 10 * * 6",  # 週六10:00
            "tz": "Asia/Hong_Kong"
        },
        "payload": {
            "kind": "agentTurn",
            "message": "執行週末系統維護任務。清理舊數據，備份重要文件，檢查系統健康。",
            "model": "deepseek/deepseek-coder"
        },
        "sessionTarget": "isolated",
        "delivery": {
            "mode": "announce",
            "channel": "telegram",
            "to": "7955740007"
        },
        "enabled": True
    }
]

# 合併所有任務
all_jobs = cron_jobs + special_jobs

# 保存配置
config_file = "/Users/gordonlui/.openclaw/workspace/trading_schedule_cron_config.json"
with open(config_file, 'w') as f:
    json.dump(all_jobs, f, indent=2, ensure_ascii=False)

print(f"✅ Cron任務配置已保存: {config_file}")
print(f"\n📋 配置的任務 ({len(all_jobs)} 個):")

# 分組顯示
print(f"\n📈 交易時間監控任務 ({len(cron_jobs)} 個):")
for i, job in enumerate(cron_jobs, 1):
    time_slot = job['name'].split()[-1]
    print(f"  {i:2d}. {time_slot} - {job['description']}")

print(f"\n🔧 特殊任務 ({len(special_jobs)} 個):")
for i, job in enumerate(special_jobs, 1):
    schedule = job['schedule']['expr']
    print(f"  {i:2d}. {schedule} - {job['description']}")

print(f"\n💡 使用說明:")
print(f"   1. 查看現有Cron任務:")
print(f"      openclaw cron list")
print(f"   2. 添加所有任務 (需要逐個添加):")
print(f"      openclaw cron add --job '{config_file}'")
print(f"   3. 測試單個任務:")
print(f"      openclaw cron run <jobId>")
print(f"   4. 手動測試系統:")
print(f"      python3 /Users/gordonlui/.openclaw/workspace/trading_schedule_system.py")

print(f"\n⚡ 立即測試:")
print(f"   1. 測試價格驗證: python3 /Users/gordonlui/.openclaw/workspace/price_validator.py")
print(f"   2. 測試交易系統: python3 /Users/gordonlui/.openclaw/workspace/trading_schedule_system.py --test")
print(f"   3. 測試突破檢測: python3 /Users/gordonlui/.openclaw/workspace/check_price_breakout.py")

print(f"\n📊 系統文件結構:")
print(f"  主系統:")
print(f"    • trading_schedule_system.py - 定時任務主系統")
print(f"    • price_validator.py - 價格驗證模塊")
print(f"    • validated_xgboost_predictor.py - 驗證版預測系統")
print(f"    • check_price_breakout.py - 價格突破檢測")
print(f"  配置文件:")
print(f"    • trading_schedule_config.json - 系統配置")
print(f"    • trading_schedule_cron_config.json - Cron任務配置")
print(f"  結果目錄:")
print(f"    • /Users/gordonlui/.openclaw/workspace/schedule_results/ - 任務結果")
print(f"    • /Users/gordonlui/.openclaw/workspace/validation_results/ - 驗證結果")
print(f"    • /Users/gordonlui/.openclaw/workspace/validation_logs/ - 驗證日誌")

print(f"\n⚠️  注意事項:")
print(f"   1. 系統使用模擬數據，需要連接富途API獲取真實數據")
print(f"   2. 實際交易前請進行充分測試")
print(f"   3. 投資有風險，請謹慎決策")
print(f"   4. 建議先添加1-2個任務測試，確認正常後再添加全部")

print(f"\n✅ 配置完成！")
print("=" * 70)

# 生成安裝腳本
install_script = f"""#!/bin/bash
# 交易定時任務系統安裝腳本
# 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo "🔧 安裝交易定時任務系統..."

# 1. 檢查OpenClaw狀態
echo "1. 檢查OpenClaw狀態..."
openclaw status

# 2. 查看現有Cron任務
echo "\\n2. 查看現有Cron任務..."
openclaw cron list

# 3. 添加交易監控任務（示例）
echo "\\n3. 添加交易監控任務（示例）..."
echo "   手動執行: openclaw cron add --job '{config_file}'"

# 4. 測試系統
echo "\\n4. 測試系統..."
python3 /Users/gordonlui/.openclaw/workspace/trading_schedule_system.py --test

echo "\\n✅ 安裝腳本生成完成"
echo "💡 請手動執行上述步驟"
"""

install_file = "/Users/gordonlui/.openclaw/workspace/install_trading_schedule.sh"
with open(install_file, 'w') as f:
    f.write(install_script)

import os
import stat
os.chmod(install_file, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

print(f"\n📝 安裝腳本已創建: {install_file}")
print(f"💡 使用方法: bash {install_file}")

print(f"\n🎯 下一步行動:")
print(f"   1. 運行安裝腳本: bash {install_file}")
print(f"   2. 手動添加Cron任務")
print(f"   3. 測試系統運行")
print(f"   4. 監控執行結果")

print(f"\n🚀 準備明日開市自動監控！")
print("=" * 70)
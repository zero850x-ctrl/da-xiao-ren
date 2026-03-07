#!/usr/bin/env python3
"""
設置交易系統Cron任務
"""

import json
from datetime import datetime

print("=" * 70)
print("⏰ 設置交易系統Cron任務")
print("=" * 70)

# Cron任務配置
cron_jobs = [
    {
        "name": "每日開市分析",
        "description": "開市後運行XGBoost預測，生成交易信號",
        "schedule": {
            "kind": "cron",
            "expr": "31 9 * * 1-5",  # 週一至週五 09:31
            "tz": "Asia/Hong_Kong"
        },
        "payload": {
            "kind": "agentTurn",
            "message": "運行每日開市分析任務。執行以下命令：python3 /Users/gordonlui/.openclaw/workspace/auto_trading_system.py --mode daily-open",
            "model": "deepseek/deepseek-coder",
            "thinking": "verbose"
        },
        "sessionTarget": "isolated",
        "delivery": {
            "mode": "announce",
            "channel": "telegram",
            "to": "7955740007"
        }
    },
    {
        "name": "盤中價格監控",
        "description": "每30分鐘檢查股票價格，監控關鍵價位",
        "schedule": {
            "kind": "every",
            "everyMs": 30 * 60 * 1000,  # 30分鐘
            "anchorMs": 9 * 60 * 60 * 1000  # 09:00開始
        },
        "payload": {
            "kind": "agentTurn",
            "message": "運行盤中價格監控任務。執行以下命令：python3 /Users/gordonlui/.openclaw/workspace/auto_trading_system.py --mode intraday",
            "model": "deepseek/deepseek-coder"
        },
        "sessionTarget": "isolated",
        "delivery": {
            "mode": "none"  # 正常時不報告
        }
    },
    {
        "name": "每日收市總結",
        "description": "收市後生成每日交易報告",
        "schedule": {
            "kind": "cron",
            "expr": "31 16 * * 1-5",  # 週一至週五 16:31
            "tz": "Asia/Hong_Kong"
        },
        "payload": {
            "kind": "agentTurn",
            "message": "運行每日收市總結任務。執行以下命令：python3 /Users/gordonlui/.openclaw/workspace/auto_trading_system.py --mode daily-close",
            "model": "deepseek/deepseek-coder"
        },
        "sessionTarget": "isolated",
        "delivery": {
            "mode": "announce",
            "channel": "telegram",
            "to": "7955740007"
        }
    },
    {
        "name": "聯想集團專用監控",
        "description": "專門監控HK.00992聯想集團，設置價格提醒",
        "schedule": {
            "kind": "every",
            "everyMs": 15 * 60 * 1000,  # 15分鐘
            "anchorMs": 9 * 60 * 60 * 1000  # 09:00開始
        },
        "payload": {
            "kind": "agentTurn",
            "message": "運行聯想集團監控任務。執行以下命令：python3 /Users/gordonlui/.openclaw/workspace/execute_992_updated.py",
            "model": "deepseek/deepseek-coder"
        },
        "sessionTarget": "isolated",
        "delivery": {
            "mode": "none"  # 正常時不報告
        }
    },
    {
        "name": "價格突破緊急通知",
        "description": "監控關鍵價位突破，發送緊急通知",
        "schedule": {
            "kind": "every",
            "everyMs": 5 * 60 * 1000,  # 5分鐘
            "anchorMs": 9 * 60 * 60 * 1000  # 09:00開始
        },
        "payload": {
            "kind": "agentTurn",
            "message": "檢查聯想集團價格突破情況。如果價格突破關鍵價位($9.12, $9.00, $8.88)，立即發送通知。執行：python3 /Users/gordonlui/.openclaw/workspace/check_price_breakout.py",
            "model": "deepseek/deepseek-coder"
        },
        "sessionTarget": "isolated",
        "delivery": {
            "mode": "announce",
            "channel": "telegram",
            "to": "7955740007"
        }
    }
]

# 保存配置
config_file = "/Users/gordonlui/.openclaw/workspace/trading_cron_config.json"
with open(config_file, 'w') as f:
    json.dump(cron_jobs, f, indent=2, ensure_ascii=False)

print(f"✅ Cron任務配置已保存: {config_file}")
print(f"\n📋 配置的任務:")

for i, job in enumerate(cron_jobs, 1):
    print(f"\n{i}. {job['name']}")
    print(f"   描述: {job['description']}")
    
    if job['schedule']['kind'] == 'cron':
        print(f"   時間: {job['schedule']['expr']} ({job['schedule']['tz']})")
    else:
        minutes = job['schedule']['everyMs'] / (60 * 1000)
        print(f"   頻率: 每{minutes}分鐘")
    
    if job['delivery']['mode'] == 'announce':
        print(f"   通知: Telegram")
    else:
        print(f"   通知: 靜默")

print(f"\n💡 使用說明:")
print(f"   1. 手動添加Cron任務:")
print(f"      openclaw cron add --job '{config_file}'")
print(f"   2. 查看現有任務:")
print(f"      openclaw cron list")
print(f"   3. 測試任務:")
print(f"      openclaw cron run <jobId>")

print(f"\n⚡ 立即測試:")
print(f"   1. 測試開市分析: python3 auto_trading_system.py --mode daily-open")
print(f"   2. 測試聯想監控: python3 execute_992_updated.py")
print(f"   3. 測試價格突破: 需要創建 check_price_breakout.py")

print(f"\n🔧 需要創建的文件:")
print(f"   1. check_price_breakout.py - 價格突破檢測")
print(f"   2. 完善 auto_trading_system.py 的各模式")

print(f"\n✅ 配置完成！")
print("=" * 70)
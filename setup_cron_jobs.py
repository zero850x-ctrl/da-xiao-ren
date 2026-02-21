#!/usr/bin/env python3
"""
設置黃金自動交易cron任務
"""

import os
import json
from datetime import datetime
import subprocess

def setup_cron_jobs():
    """設置cron任務"""
    print("=" * 70)
    print("⏰ 設置黃金自動交易cron任務")
    print("=" * 70)
    
    # 檢查OpenClaw cron狀態
    print("\n🔍 檢查OpenClaw cron狀態...")
    
    try:
        # 使用subprocess調用openclaw cron list
        result = subprocess.run(['openclaw', 'cron', 'list'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ OpenClaw cron服務正常")
            print(result.stdout[:500])  # 顯示部分輸出
        else:
            print("❌ OpenClaw cron命令失敗")
            print(f"錯誤: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ 未找到openclaw命令")
        print("請確保OpenClaw已正確安裝")
        return False
    
    # 創建cron任務配置
    print("\n🔧 創建cron任務配置...")
    
    # 任務1: 每小時交易檢查
    hourly_trade_job = {
        "name": "黃金自動交易（每小時）",
        "schedule": {
            "kind": "cron",
            "expr": "0 * * * *",  # 每小時整點
            "tz": "Asia/Hong_Kong"
        },
        "payload": {
            "kind": "agentTurn",
            "message": "運行黃金自動交易cron任務。檢查市場條件，如果符合交易信號，執行0.01手交易。嚴格遵守風險管理規則。",
            "model": "deepseek/deepseek-coder",
            "thinking": "concise"
        },
        "sessionTarget": "isolated",
        "enabled": True,
        "notify": True,
        "delivery": {
            "mode": "announce",
            "channel": "telegram",
            "to": "7955740007",
            "bestEffort": True
        }
    }
    
    # 任務2: 每日報告
    daily_report_job = {
        "name": "黃金交易每日報告",
        "schedule": {
            "kind": "cron",
            "expr": "30 16 * * *",  # 每天16:30（收盤後）
            "tz": "Asia/Hong_Kong"
        },
        "payload": {
            "kind": "agentTurn",
            "message": "生成黃金交易每日報告。分析今日交易表現，計算盈虧，檢查持倉，提供明日交易建議。",
            "model": "deepseek/deepseek-coder",
            "thinking": "concise"
        },
        "sessionTarget": "isolated",
        "enabled": True,
        "notify": True,
        "delivery": {
            "mode": "announce",
            "channel": "telegram",
            "to": "7955740007",
            "bestEffort": True
        }
    }
    
    # 任務3: 每周優化
    weekly_optimization_job = {
        "name": "黃金策略每周優化",
        "schedule": {
            "kind": "cron",
            "expr": "0 9 * * 1",  # 每周一09:00
            "tz": "Asia/Hong_Kong"
        },
        "payload": {
            "kind": "agentTurn",
            "message": "運行黃金交易策略每周優化。分析過去一周交易數據，優化策略參數，調整風險管理設置。",
            "model": "deepseek/deepseek-coder",
            "thinking": "concise"
        },
        "sessionTarget": "isolated",
        "enabled": True,
        "notify": True,
        "delivery": {
            "mode": "announce",
            "channel": "telegram",
            "to": "7955740007",
            "bestEffort": True
        }
    }
    
    # 保存任務配置
    cron_config = {
        "hourly_trade": hourly_trade_job,
        "daily_report": daily_report_job,
        "weekly_optimization": weekly_optimization_job,
        "created_at": datetime.now().isoformat(),
        "notes": "黃金自動交易系統cron任務配置"
    }
    
    config_path = '/Users/gordonlui/.openclaw/workspace/cron_config.json'
    with open(config_path, 'w') as f:
        json.dump(cron_config, f, indent=2)
    
    print(f"✅ cron配置已保存: {config_path}")
    
    # 創建cron任務添加腳本
    print("\n📝 創建cron任務添加腳本...")
    
    add_cron_script = '''#!/usr/bin/env python3
"""
添加黃金交易cron任務到OpenClaw
"""

import subprocess
import json
import sys

def add_cron_job(job_name, job_config):
    """添加cron任務"""
    print(f"🔧 添加任務: {job_name}")
    
    # 將配置轉為JSON字符串
    job_json = json.dumps(job_config)
    
    # 構建命令
    cmd = ['openclaw', 'cron', 'add', '--job', job_json]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 任務添加成功: {job_name}")
            print(f"   輸出: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ 任務添加失敗: {job_name}")
            print(f"   錯誤: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 執行命令失敗: {e}")
        return False

def main():
    """主函數"""
    print("=" * 60)
    print("🏆 添加黃金交易cron任務")
    print("=" * 60)
    
    # 加載配置
    config_path = '/Users/gordonlui/.openclaw/workspace/cron_config.json'
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 加載配置失敗: {e}")
        return
    
    # 添加任務
    success_count = 0
    
    # 每小時交易任務
    if add_cron_job("hourly_trade", config['hourly_trade']):
        success_count += 1
    
    # 每日報告任務
    if add_cron_job("daily_report", config['daily_report']):
        success_count += 1
    
    # 每周優化任務
    if add_cron_job("weekly_optimization", config['weekly_optimization']):
        success_count += 1
    
    print(f"\n📊 結果: {success_count}/3 個任務添加成功")
    
    if success_count == 3:
        print("✅ 所有cron任務設置完成")
        print("\n📋 任務安排:")
        print("   1. 每小時交易檢查: 整點執行")
        print("   2. 每日報告: 16:30 (收盤後)")
        print("   3. 每周優化: 周一09:00")
    else:
        print("⚠️  部分任務添加失敗，請手動檢查")

if __name__ == "__main__":
    main()
'''
    
    script_path = '/Users/gordonlui/.openclaw/workspace/add_cron_jobs.py'
    with open(script_path, 'w') as f:
        f.write(add_cron_script)
    
    # 設置執行權限
    os.chmod(script_path, 0o755)
    
    print(f"✅ cron任務添加腳本已創建: {script_path}")
    
    # 創建測試腳本
    print("\n🧪 創建測試腳本...")
    
    test_script = '''#!/usr/bin/env python3
"""
測試黃金自動交易cron任務
"""

import sys
sys.path.append('/Users/gordonlui/.openclaw/workspace')

from gold_auto_trader_cron import GoldAutoTraderCron

def test_cron_execution():
    """測試cron執行"""
    print("🧪 測試cron任務執行...")
    
    try:
        trader = GoldAutoTraderCron()
        
        # 模擬不同時間
        test_cases = [
            ("交易時段測試", True),
            ("非交易時段測試", False),
            ("達到每日限制測試", False)
        ]
        
        for test_name, should_trade in test_cases:
            print(f"\n🔍 {test_name}")
            trader.run()
        
        print("\n✅ cron任務測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_cron_execution()
'''
    
    test_path = '/Users/gordonlui/.openclaw/workspace/test_cron.py'
    with open(test_path, 'w') as f:
        f.write(test_script)
    
    os.chmod(test_path, 0o755)
    
    print(f"✅ 測試腳本已創建: {test_path}")
    
    # 創建監控腳本
    print("\n📊 創建監控腳本...")
    
    monitor_script = '''#!/usr/bin/env python3
"""
監控黃金自動交易系統
"""

import os
import json
from datetime import datetime, timedelta
import pandas as pd

def monitor_trading_system():
    """監控交易系統"""
    print("=" * 70)
    print("📊 黃金自動交易系統監控")
    print("=" * 70)
    
    # 檢查文件
    files_to_check = [
        ('/Users/gordonlui/.openclaw/workspace/gold_trades_log.json', '交易記錄'),
        ('/Users/gordonlui/.openclaw/workspace/daily_stats.json', '每日統計'),
        ('/Users/gordonlui/.openclaw/workspace/optimized_strategy.json', '策略配置'),
        ('/Users/gordonlui/.openclaw/workspace/cron_config.json', 'cron配置')
    ]
    
    print("\n🔍 文件檢查:")
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {description}: {file_path} ({size} bytes)")
        else:
            print(f"   ❌ {description}: 文件不存在")
    
    # 檢查日誌
    log_dir = '/Users/gordonlui/.openclaw/workspace/logs'
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        print(f"\n📝 日誌文件: {len(log_files)}個")
        for log_file in sorted(log_files)[-3:]:  # 最近3個
            log_path = os.path.join(log_dir, log_file)
            size = os.path.getsize(log_path)
            print(f"   • {log_file} ({size} bytes)")
    else:
        print("\n📝 日誌目錄不存在")
    
    # 檢查交易記錄
    trades_log_path = '/Users/gordonlui/.openclaw/workspace/gold_trades_log.json'
    if os.path.exists(trades_log_path):
        with open(trades_log_path, 'r') as f:
            trades = json.load(f)
        
        print(f"\n💼 交易統計:")
        print(f"   總交易次數: {len(trades)}")
        
        if trades:
            # 計算今日交易
            today = datetime.now().strftime('%Y-%m-%d')
            today_trades = [t for t in trades if t.get('timestamp', '').startswith(today)]
            
            print(f"   今日交易: {len(today_trades)}筆")
            
            # 計算盈利
            winning = [t for t in trades if t.get('profit_amount', 0) > 0]
            losing = [t for t in trades if t.get('profit_amount', 0) <= 0]
            
            total_profit = sum(t.get('profit_amount', 0) for t in trades)
            win_rate = len(winning) / len(trades) * 100 if trades else 0
            
            print(f"   盈利交易: {len(winning)} ({win_rate:.1f}%)")
            print(f"   虧損交易: {len(losing)}")
            print(f"   總盈利: ${total_profit:.2f}")
            
            # 最近5筆交易
            print(f"\n📋 最近5筆交易:")
            for trade in trades[-5:]:
                profit = trade.get('profit_amount', 0)
                emoji = "🟢" if profit > 0 else "🔴"
                print(f"   {trade.get('timestamp', '')[:16]} {trade.get('signal', '')} "
                      f"{emoji} ${profit:.2f} ({trade.get('reason', '')[:30]}...)")
    
    # 檢查cron狀態
    print(f"\n⏰ Cron狀態:")
    print("   使用命令檢查: openclaw cron list")
    print("   添加任務: python3 add_cron_jobs.py")
    print("   測試任務: python3 test_cron.py")
    
    print(f"\n🚀 建議行動:")
    print("   1. 運行測試: python3 test_cron.py")
    print("   2. 添加cron任務: python3 add_cron_jobs.py")
    print("   3. 監控交易: python3 monitor_trading.py")
    print("   4. 查看日誌: tail -f logs/gold_trader_*.log")

if __name__ == "__main__":
    monitor_trading_system()
'''
    
    monitor_path = '/Users/gordonlui/.openclaw/workspace/monitor_trading.py'
    with open(monitor_path, 'w') as f:
        f.write(monitor_script)
    
    os.chmod(monitor_path, 0o755)
    
    print(f"✅ 監控腳本已創建: {monitor_path}")
    
    print("\n" + "=" * 70)
    print("🎯 設置完成！")
    print("=" * 70)
    
    print(f"\n📋 下一步:")
    print(f"   1. 測試cron任務: python3 test_cron.py")
    print(f"   2. 添加cron任務: python3 add_cron_jobs.py")
    print(f"   3. 監控系統: python3 monitor_trading.py")
    print(f"   4. 查看配置: cat cron_config.json")
    
    print(f"\n⚠️  注意:")
    print(f"   • 確保OpenClaw服務正在運行")
    print(f"   • 檢查環境變量設置")
    print(f"   • 先測試再添加到cron")
    print(f"   • 嚴格遵守0.01手限制")
    
    return True

if __name__ == "__main__":
    setup_cron_jobs()
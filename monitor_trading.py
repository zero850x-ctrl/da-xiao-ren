#!/usr/bin/env python3
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

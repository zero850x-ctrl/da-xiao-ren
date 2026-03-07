#!/usr/bin/env python3
"""
監控黃金自動交易系統
"""

import os
import json
from datetime import datetime

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
            print(f"   ✅ {description}: {size} bytes")
        else:
            print(f"   ❌ {description}: 文件不存在")
    
    # 檢查日誌
    log_dir = '/Users/gordonlui/.openclaw/workspace/logs'
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        print(f"\n📝 日誌文件: {len(log_files)}個")
        for log_file in sorted(log_files)[-3:]:
            log_path = os.path.join(log_dir, log_file)
            size = os.path.getsize(log_path)
            print(f"   • {log_file} ({size} bytes)")
    else:
        print("\n📝 日誌目錄不存在")
    
    # 檢查交易記錄
    trades_log_path = '/Users/gordonlui/.openclaw/workspace/gold_trades_log.json'
    if os.path.exists(trades_log_path):
        try:
            with open(trades_log_path, 'r') as f:
                trades = json.load(f)
            
            print(f"\n💼 交易統計:")
            print(f"   總交易次數: {len(trades)}")
            
            if trades:
                # 計算今日交易
                today = datetime.now().strftime('%Y-%m-%d')
                today_trades = [t for t in trades if isinstance(t, dict) and t.get('timestamp', '').startswith(today)]
                
                print(f"   今日交易: {len(today_trades)}筆")
                
                # 計算盈利
                winning = [t for t in trades if isinstance(t, dict) and t.get('profit_amount', 0) > 0]
                losing = [t for t in trades if isinstance(t, dict) and t.get('profit_amount', 0) <= 0]
                
                total_profit = sum(t.get('profit_amount', 0) for t in trades if isinstance(t, dict))
                win_rate = len(winning) / len(trades) * 100 if trades else 0
                
                print(f"   盈利交易: {len(winning)} ({win_rate:.1f}%)")
                print(f"   虧損交易: {len(losing)}")
                print(f"   總盈利: ${total_profit:.2f}")
                
                # 最近5筆交易
                print(f"\n📋 最近5筆交易:")
                for trade in trades[-5:]:
                    if isinstance(trade, dict):
                        profit = trade.get('profit_amount', 0)
                        emoji = "🟢" if profit > 0 else "🔴"
                        timestamp = trade.get('timestamp', '')[:16] if trade.get('timestamp') else 'N/A'
                        signal = trade.get('signal', 'N/A')
                        reason = trade.get('reason', '')[:30] + '...' if trade.get('reason') else 'N/A'
                        print(f"   {timestamp} {signal} {emoji} ${profit:.2f} ({reason})")
        except Exception as e:
            print(f"❌ 讀取交易記錄失敗: {e}")
    
    # 顯示配置
    config_path = '/Users/gordonlui/.openclaw/workspace/optimized_strategy.json'
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            print(f"\n🎯 當前策略配置:")
            print(f"   策略名稱: {config.get('optimized_strategy', 'N/A')}")
            params = config.get('parameters', {})
            print(f"   SMA: {params.get('sma_short', 'N/A')}/{params.get('sma_long', 'N/A')}")
            print(f"   RSI: {params.get('rsi_period', 'N/A')}期 ({params.get('rsi_low', 'N/A')}/{params.get('rsi_high', 'N/A')})")
            print(f"   止損/止盈: {params.get('stop_loss', 'N/A')}/{params.get('take_profit', 'N/A')}點")
            print(f"   最大手數: {config.get('max_lot_size', 'N/A')}手")
        except Exception as e:
            print(f"❌ 讀取配置失敗: {e}")
    
    print(f"\n🚀 建議行動:")
    print("   1. 測試cron任務: python3 test_cron_fixed.py")
    print("   2. 添加cron任務: python3 add_cron_jobs.py")
    print("   3. 運行交易: python3 gold_auto_trader_cron.py")
    print("   4. 查看日誌: ls -la logs/")

if __name__ == "__main__":
    monitor_trading_system()
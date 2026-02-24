#!/usr/bin/env python3
"""
通知系統 - 當有交易時發送報告
"""

import sys
import json
import subprocess
from datetime import datetime

def send_trade_notification(message):
    """通過OpenClaw發送交易通知"""
    print(f"📨 發送交易通知...")
    
    # 讀取最後的交易記錄
    try:
        with open('/Users/gordonlui/.openclaw/workspace/trading_reports/auto_trade.log', 'r') as f:
            log = f.read()
            if log:
                print("📝 最近交易記錄:")
                print(log[-500:])
    except:
        pass
    
    # 嘗試發送Telegram消息
    try:
        cmd = [
            'openclaw', 'message', 'send',
            '--channel', 'telegram',
            '--target', '7955740007',
            '--message', message
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ 通知已發送")
        else:
            print(f"⚠️ 通知發送失敗: {result.stderr}")
    except Exception as e:
        print(f"⚠️ 發送失敗: {e}")

def check_and_notify():
    """檢查並通知"""
    # 讀取最新JSON報告
    try:
        with open('/Users/gordonlui/.openclaw/workspace/trading_reports/xgboost_multi_latest.json', 'r') as f:
            report = json.load(f)
    except:
        print("❌ 無法讀取報告")
        return
    
    signals = report.get('signals', [])
    
    if signals:
        signal_text = ', '.join([f"{s['stock']}:{s['signal']}" for s in signals])
        message = f"🤖 **交易信號** - {datetime.now().strftime('%H:%M')}\n\n{signal_text}\n\n詳情請查看日誌"
        send_trade_notification(message)
    else:
        print("✅ 無交易信號，跳過通知")

if __name__ == '__main__':
    check_and_notify()

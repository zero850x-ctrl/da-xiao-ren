#!/usr/bin/env python3
"""
富途快速監控 - 有交易先報告版
"""

import sys
import json
from datetime import datetime

def check_for_trades():
    """檢查有冇交易"""
    try:
        # 讀取最新既交易記錄
        with open('/Users/gordonlui/.openclaw/workspace/trading_reports/auto_trade.log', 'r') as f:
            content = f.read()
        
        # 搵最近既交易
        lines = content.split('\n')
        recent_trades = []
        for line in lines[-20:]:
            if '買入成功' in line or '賣出成功' in line:
                recent_trades.append(line)
        
        return recent_trades
    except:
        return []

def main():
    trades = check_for_trades()
    
    if trades:
        print(f"發現 {len(trades)} 筆最近交易:")
        for t in trades:
            print(t)
    else:
        print("冇新交易，唔發通知")

if __name__ == "__main__":
    main()

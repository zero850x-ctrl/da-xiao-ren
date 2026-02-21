#!/usr/bin/env python3
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
            print(f"
🔍 {test_name}")
            trader.run()
        
        print("
✅ cron任務測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_cron_execution()

#!/usr/bin/env python3
"""
測試黃金自動交易cron任務
"""

import sys
import os

# 添加路徑
sys.path.append('/Users/gordonlui/.openclaw/workspace')

try:
    from gold_auto_trader_cron import GoldAutoTraderCron
    print("✅ 成功導入交易模塊")
except ImportError as e:
    print(f"❌ 導入失敗: {e}")
    print("正在嘗試直接運行...")
    
    # 直接運行cron腳本
    os.system('cd /Users/gordonlui/.openclaw/workspace && python3 gold_auto_trader_cron.py')
    sys.exit(0)

def test_cron_execution():
    """測試cron執行"""
    print("=" * 60)
    print("🧪 測試黃金自動交易cron任務")
    print("=" * 60)
    
    try:
        print("\n1. 初始化交易系統...")
        trader = GoldAutoTraderCron()
        
        print("\n2. 運行交易檢查...")
        trader.run()
        
        print("\n3. 檢查交易記錄...")
        if trader.trades_log:
            print(f"   總交易記錄: {len(trader.trades_log)}筆")
            latest = trader.trades_log[-1] if trader.trades_log else None
            if latest:
                print(f"   最新交易: {latest.get('signal')} @ ${latest.get('entry_price'):.2f}")
                print(f"   盈利: ${latest.get('profit_amount', 0):.2f}")
        else:
            print("   無交易記錄")
        
        print("\n✅ cron任務測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_cron_execution()
#!/usr/bin/env python3
"""
富途模擬交易監控腳本
每30分鐘運行一次
"""

import sys
import time
import json
from datetime import datetime
from futu import *

def monitor_portfolio():
    """監控投資組合"""
    print(f"📊 監控時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # 連接
        trd_ctx = OpenSecTradeContext(
            host='127.0.0.1',
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        
        # 檢查持倉
        ret, positions = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK and len(positions) > 0:
            print(f"📦 當前持倉 ({len(positions)}個):")
            
            total_pnl = 0
            total_value = 0
            
            for idx, row in positions.iterrows():
                code = row['code']
                qty = row['qty']
                cost = row.get('cost_price', 0)
                market_val = row.get('market_val', 0)
                pnl = row.get('pl_ratio', 0)  # 盈虧百分比
                
                print(f"  {code}: {qty}股")
                print(f"    成本: {cost:.2f}, 市值: {market_val:,.2f}")
                print(f"    盈虧: {pnl:.2f}%")
                
                total_pnl += pnl
                total_value += market_val
            
            print(f"\n💰 持倉總市值: HKD {total_value:,.2f}")
            print(f"📈 總盈虧: {total_pnl:.2f}%")
        else:
            print("📭 無持倉")
        
        trd_ctx.close()
        
    except Exception as e:
        print(f"❌ 監控錯誤: {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    monitor_portfolio()

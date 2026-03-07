#!/usr/bin/env python3
"""
富途模擬交易賣出腳本
"""

import sys
import time
from futu import OpenSecTradeContext, TrdSide, TrdEnv, RET_OK, OrderType, SecurityFirm

def sell_stocks():
    """賣出信號股票"""
    
    # 賣出清單
    sell_orders = [
        {'code': 'HK.00992', 'qty': 26000, 'price': 9.48},  # 聯想
        {'code': 'HK.09868', 'qty': 400, 'price': 69.45},   # 小鵬
        {'code': 'HK.09618', 'qty': 250, 'price': 107.50},  # 京東
    ]
    
    trd_ctx = OpenSecTradeContext(
        host='127.0.0.1',
        port=11111,
        security_firm=SecurityFirm.FUTUSECURITIES
    )
    
    print("📊 模擬交易賣出執行")
    print("=" * 50)
    
    for order in sell_orders:
        code = order['code']
        qty = order['qty']
        price = order['price']
        
        print(f"\n🔴 賣出 {code} {qty}股 @ {price}")
        
        ret, data = trd_ctx.place_order(
            price=price,
            qty=qty,
            code=code,
            trd_side=TrdSide.SELL,
            order_type=OrderType.NORMAL,
            trd_env=TrdEnv.SIMULATE
        )
        
        if ret == RET_OK:
            print(f"   ✅ 訂單成功: {data}")
        else:
            print(f"   ❌ 錯誤: {data}")
        
        time.sleep(0.5)
    
    trd_ctx.close()
    print("\n" + "=" * 50)
    print("✅ 賣出執行完成")
    
    # 顯示更新後的持倉
    print("\n📊 更新後持倉:")
    trd_ctx2 = OpenSecTradeContext(
        host='127.0.0.1',
        port=11111,
        security_firm=SecurityFirm.FUTUSECURITIES
    )
    
    ret, positions = trd_ctx2.position_list_query(trd_env=TrdEnv.SIMULATE)
    if ret == RET_OK and len(positions) > 0:
        for idx, row in positions.iterrows():
            print(f"   {row['code']}: {row['qty']}股")
    else:
        print("   無持倉")
    
    trd_ctx2.close()

if __name__ == '__main__':
    sell_stocks()

#!/usr/bin/env python3
"""手動減倉脚本"""
from futu import *

# Config
total_assets = 968957
target_pct = 0.20

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
trade_ctx = OpenSecTradeContext(host='127.0.0.1', port=11111)

# Get prices
codes = ['HK.01810', 'HK.01211']
ret, data = quote_ctx.get_stock_quote(code_list=codes)
print(f"Prices: {data[['code', 'last_price']].to_string()}")

target_value = total_assets * target_pct

# Calculate
for _, row in data.iterrows():
    code = row['code']
    price = row['last_price']
    
    if code == 'HK.01810':
        qty = 13200
        sell_val = qty * price - target_value
        sell_qty = int(sell_val / price / 100) * 100
        if sell_qty > 0:
            print(f"小米 {code}: 賣 {sell_qty}股 @ ${price}")
            ret, res = trade_ctx.place_order(price=price*0.99, qty=sell_qty, code=code, trd_side=TrdSide.SELL, order_type=OrderType.NORMAL, trd_env=TrdEnv.SIMULATE)
            print(f"結果: {'✅' if ret==0 else '❌'}")
    
    elif code == 'HK.01211':
        qty = 3400
        sell_val = qty * price - target_value
        sell_qty = int(sell_val / price / 100) * 100
        if sell_qty > 0:
            print(f"比亞迪 {code}: 賣 {sell_qty}股 @ ${price}")
            ret, res = trade_ctx.place_order(price=price*0.99, qty=sell_qty, code=code, trd_side=TrdSide.SELL, order_type=OrderType.NORMAL, trd_env=TrdEnv.SIMULATE)
            print(f"結果: {'✅' if ret==0 else '❌'}")

quote_ctx.close()
trade_ctx.close()
print("完成")

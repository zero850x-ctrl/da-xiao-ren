#!/usr/bin/env python3
"""
久留美模擬倉全自動交易系統
根據XGBoost信號自動執行買賣（無需確認）
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, '/Users/gordonlui/.openclaw/workspace')

# 久留美模擬倉持倉
SIM_PORTFOLIO = {
    'HK.07500': {'name': '兩倍看空', 'qty': 30000, 'cost': 1.63},
    'HK.02800': {'name': '盈富基金', 'qty': 4500, 'cost': 26.78},
    'HK.01211': {'name': '比亞迪', 'qty': 600, 'cost': 98.45},
    'HK.09618': {'name': '京東集團', 'qty': 500, 'cost': 120.00},
}

# 持倉股票代碼集合（用於判斷是否賣出）
HELD_STOCKS = set(SIM_PORTFOLIO.keys())

def get_xgboost_signals():
    """運行XGBoost獲取信號"""
    import subprocess
    result = subprocess.run(
        ['python3', '/Users/gordonlui/.openclaw/workspace/xgboost_multi_stock.py'],
        capture_output=True, text=True, timeout=60
    )
    return result.stdout + result.stderr

def parse_signals(output):
    """解析XGBoost輸出既信號"""
    signals = {}
    lines = output.split('\n')
    for code in SIM_PORTFOLIO.keys():
        stock_code = code.replace('HK.', '')
        for i, line in enumerate(lines):
            if f'HK.{stock_code}' in line or f'{stock_code}' in line:
                if 'BUY' in line:
                    signals[code] = 'BUY'
                elif 'SELL' in line:
                    signals[code] = 'SELL'
    return signals

def execute_trade(code, action, qty=None):
    """執行模擬倉交易"""
    import futu as ft
    
    quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
    trade_ctx = ft.OpenTradeContext(host='127.0.0.1', port=11111)
    
    stock_code = code.replace('HK.', '')
    name = SIM_PORTFOLIO[code]['name'] if code in SIM_PORTFOLIO else code
    
    try:
        # 獲取當前價格
        ret, data = quote_ctx.get_stock_quote([code])
        if ret != 0:
            print(f"❌ 獲取價格失敗: {data}")
            return False
        
        current_price = data['cur_price'].iloc[0]
        print(f"📈 {code} {name} 現價: ${current_price}")
        
        if action == 'BUY':
            # 買入時用限價單，現價+1%
            buy_price = round(current_price * 1.01, 2)
            buy_qty = qty or 1000
            ret, data = trade_ctx.place_order(
                price=buy_price,
                qty=buy_qty,
                code=code,
                order_type=ft.OrderType.NORMAL,
                trd_side=ft.TrdSide.BUY
            )
            action_text = f"買入 {buy_qty}股 @ ${buy_price}"
        elif action == 'SELL':
            # 賣出時用限價單，現價-1%
            sell_qty = qty or SIM_PORTFOLIO[code]['qty']
            sell_price = round(current_price * 0.99, 2)
            ret, data = trade_ctx.place_order(
                price=sell_price,
                qty=sell_qty,
                code=code,
                order_type=ft.OrderType.NORMAL,
                trd_side=ft.TrdSide.SELL
            )
            action_text = f"賣出 {sell_qty}股 @ ${sell_price}"
        
        if ret == 0:
            order_id = data['order_id'].iloc[0] if 'order_id' in data.columns else 'N/A'
            print(f"✅ {action} {code} {name} 成功! 訂單ID: {order_id}")
            
            # 發送WhatsApp通知
            notify_trade(code, name, action, action_text)
            return True
        else:
            print(f"❌ {action} {code} {name} 失敗: {data}")
            return False
    except Exception as e:
        print(f"❌ 交易錯誤: {e}")
        return False
    finally:
        quote_ctx.close()
        trade_ctx.close()

def notify_trade(code, name, action, details):
    """發送交易通知"""
    import requests
    
    msg = f"🦊 久留美自動交易\n"
    msg += f"================\n"
    msg += f"股票: {code} {name}\n"
    msg += f"操作: {details}\n"
    msg += f"時間: {datetime.now().strftime('%H:%M:%S')}"
    
    try:
        requests.post('http://127.0.0.1:18789/v1/message', json={
            'channel': 'whatsapp',
            'to': '+85298104938',
            'message': msg
        }, timeout=5)
    except Exception as e:
        print(f"通知失敗: {e}")

def main():
    print(f"=== 久留美模擬倉全自動交易 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    # 獲取XGBoost信號
    print("🔍 獲取XGBoost信號...")
    output = get_xgboost_signals()
    
    # 解析信號
    signals = parse_signals(output)
    print(f"📊 檢測到信號: {signals}")
    
    # 執行交易
    executed = []
    for code, action in signals.items():
        # BUY信號：如果未持有就買入
        if action == 'BUY':
            if code not in HELD_STOCKS:
                if execute_trade(code, 'BUY', 1000):
                    executed.append(f"{code} BUY")
            else:
                print(f"📊 {code} 已有持倉，跳過買入")
        
        # SELL信號：如果持有就賣出
        elif action == 'SELL':
            if code in HELD_STOCKS:
                if execute_trade(code, 'SELL'):
                    executed.append(f"{code} SELL")
            else:
                print(f"📊 {code} 未持有，跳過賣出")
    
    if executed:
        print(f"✅ 已執行: {executed}")
    else:
        print("📊 冇新交易")

if __name__ == '__main__':
    main()

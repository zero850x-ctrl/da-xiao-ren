#!/usr/bin/env python3
"""
每日加密貨幣交易報告
"""
import os
import json
from datetime import datetime
from binance.client import Client

# 配置
API_KEY = "05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV"
API_SECRET = "YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj"

def generate_daily_report():
    """生成每日報告"""
    print(f"📊 加密貨幣每日報告 - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 50)
    
    try:
        # 連接
        client = Client(API_KEY, API_SECRET, testnet=True)
        
        # 獲取賬戶信息
        account = client.get_account()
        
        # 計算總資產
        total_value = 0
        positions = []
        
        for balance in account['balances']:
            free = float(balance['free'])
            locked = float(balance['locked'])
            total = free + locked
            
            if total > 0 and balance['asset'] != 'USDT':
                symbol = f"{balance['asset']}USDT"
                try:
                    ticker = client.get_symbol_ticker(symbol=symbol)
                    price = float(ticker['price'])
                    value = total * price
                    total_value += value
                    
                    positions.append({
                        'asset': balance['asset'],
                        'quantity': total,
                        'price': price,
                        'value': value
                    })
                except:
                    pass
        
        # 添加USDT
        usdt_balance = next((b for b in account['balances'] if b['asset'] == 'USDT'), None)
        if usdt_balance:
            usdt_value = float(usdt_balance['free']) + float(usdt_balance['locked'])
            total_value += usdt_value
        
        # 生成報告
        print(f"💰 總資產: ${total_value:.2f}")
        
        if positions:
            print(f"📦 持倉 ({len(positions)}個):")
            for pos in positions:
                print(f"  {pos['asset']}: {pos['quantity']:.6f} @ ${pos['price']:.2f} (${pos['value']:.2f})")
        
        # 市場狀況
        print(f"🌐 主要幣種:")
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        for symbol in symbols:
            try:
                ticker = client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])
                print(f"  {symbol}: ${price:.2f}")
            except:
                print(f"  {symbol}: 無法獲取")
        
        print(f"\n🎯 今日學習重點:")
        print("  1. 觀察加密貨幣波動")
        print("  2. 實踐2%風險管理")
        print("  3. 記錄交易決策")
        
        # 保存報告
        report_data = {
            'date': datetime.now().isoformat(),
            'total_value': total_value,
            'positions': positions,
            'usdt_balance': usdt_value if usdt_balance else 0
        }
        
        report_file = f"/Users/gordonlui/.openclaw/workspace/crypto_data/daily_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"✅ 報告已保存: {report_file}")
        
    except Exception as e:
        print(f"❌ 生成報告失敗: {e}")

if __name__ == "__main__":
    generate_daily_report()

#!/usr/bin/env python3
"""
修復精度問題的測試交易
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException

def main():
    # API密鑰
    api_key = "05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV"
    api_secret = "YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj"
    
    print("🚀 修復精度測試交易")
    print("=" * 50)
    
    try:
        # 連接
        client = Client(api_key, api_secret, testnet=True)
        
        # 測試交易對
        symbol = 'BTCUSDT'
        
        # 獲取交易對信息
        symbol_info = client.get_symbol_info(symbol)
        print(f"📋 {symbol} 交易規則:")
        
        # 解析過濾器
        min_qty = None
        step_size = None
        min_notional = None
        
        for filter in symbol_info['filters']:
            if filter['filterType'] == 'LOT_SIZE':
                min_qty = float(filter['minQty'])
                step_size = float(filter['stepSize'])
                print(f"  最小數量: {min_qty}")
                print(f"  步長: {step_size}")
            elif filter['filterType'] == 'MIN_NOTIONAL':
                min_notional = float(filter['minNotional'])
                print(f"  最小名義價值: {min_notional}")
        
        # 獲取當前價格
        ticker = client.get_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
        print(f"  當前價格: ${current_price:.2f}")
        
        # 計算正確的數量
        amount_usdt = 10  # 10 USDT
        raw_quantity = amount_usdt / current_price
        
        # 調整到正確精度
        if step_size:
            # 計算步數
            steps = raw_quantity / step_size
            # 向下取整到整數步數
            steps = int(steps)
            # 計算最終數量
            quantity = steps * step_size
            # 確保不小於最小數量
            quantity = max(quantity, min_qty)
        else:
            quantity = raw_quantity
        
        print(f"\n🧮 計算交易數量:")
        print(f"  目標金額: ${amount_usdt:.2f}")
        print(f"  原始數量: {raw_quantity:.8f}")
        print(f"  調整後數量: {quantity:.8f}")
        
        # 檢查最小名義價值
        notional_value = quantity * current_price
        if min_notional and notional_value < min_notional:
            print(f"⚠️  名義價值 ${notional_value:.2f} 低於最小要求 ${min_notional:.2f}")
            # 調整到最小名義價值
            quantity = min_notional / current_price
            if step_size:
                steps = quantity / step_size
                steps = int(steps)
                quantity = steps * step_size
            quantity = max(quantity, min_qty)
            notional_value = quantity * current_price
            print(f"  調整到: {quantity:.8f} (${notional_value:.2f})")
        
        print(f"\n🎯 最終交易參數:")
        print(f"  數量: {quantity:.8f} BTC")
        print(f"  價值: ${quantity * current_price:.2f}")
        
        # 執行測試交易
        print(f"\n🛒 執行測試交易...")
        
        order = client.order_market_buy(
            symbol=symbol,
            quantity=quantity
        )
        
        print(f"✅ 測試交易成功！")
        print(f"  訂單ID: {order['orderId']}")
        print(f"  狀態: {order['status']}")
        print(f"  成交數量: {order['executedQty']}")
        print(f"  成交金額: ${order['cummulativeQuoteQty']}")
        
        # 立即賣出（完成測試循環）
        print(f"\n🔄 立即賣出完成測試...")
        
        sell_order = client.order_market_sell(
            symbol=symbol,
            quantity=quantity
        )
        
        print(f"✅ 賣出成功！")
        print(f"  訂單ID: {sell_order['orderId']}")
        print(f"  狀態: {sell_order['status']}")
        
        # 計算測試結果
        buy_amount = float(order['cummulativeQuoteQty'])
        sell_amount = float(sell_order['cummulativeQuoteQty'])
        pnl = sell_amount - buy_amount
        
        print(f"\n📊 測試結果:")
        print(f"  買入金額: ${buy_amount:.2f}")
        print(f"  賣出金額: ${sell_amount:.2f}")
        print(f"  盈虧: ${pnl:.4f}")
        
        if pnl > 0:
            print(f"  🎉 測試盈利!")
        else:
            print(f"  📉 測試虧損 (正常，因為有價差)")
        
        return True
        
    except BinanceAPIException as e:
        print(f"❌ API錯誤: {e.code} - {e.message}")
        return False
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 測試交易完成！系統準備就緒")
        print("現在可以開始真正的加密貨幣交易學習")
    else:
        print("❌ 測試交易失敗，但系統仍可運行")
        print("可以跳過測試，直接開始學習觀察")
    
    print("\n💡 下一步:")
    print("1. 觀察市場24小時波動")
    print("2. 實踐2%風險管理")
    print("3. 每日總結學習成果")
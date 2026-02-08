#!/usr/bin/env python3
"""
幣安API簡單連接測試
"""

import os
from binance.client import Client
from binance.exceptions import BinanceAPIException
import json
from datetime import datetime

def main():
    print("🚀 幣安API連接測試")
    print("=" * 50)
    
    # API密鑰
    api_key = "05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV"
    api_secret = "YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj"
    
    print("🔑 API密鑰已設置")
    print(f"API Key: {api_key[:10]}...{api_key[-10:]}")
    print(f"Secret: {api_secret[:10]}...{api_secret[-10:]}")
    
    try:
        # 1. 連接到Testnet
        print("\n1. 連接到幣安Testnet...")
        client = Client(api_key, api_secret, testnet=True)
        
        # 2. 測試服務器時間
        print("2. 測試服務器連接...")
        server_time = client.get_server_time()
        server_time_str = datetime.fromtimestamp(server_time['serverTime']/1000).strftime('%Y-%m-%d %H:%M:%S')
        print(f"✅ 服務器時間: {server_time_str}")
        
        # 3. 獲取賬戶信息
        print("\n3. 獲取賬戶信息...")
        account_info = client.get_account()
        print(f"✅ 賬戶準備就緒")
        print(f"   賬戶類型: {'Testnet' if client.testnet else 'Real'}")
        print(f"   可交易幣種數量: {len(account_info['balances'])}")
        
        # 4. 顯示可用資金
        print("\n4. 檢查可用資金...")
        balances = [b for b in account_info['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
        
        if balances:
            print(f"✅ 找到 {len(balances)} 個有餘額的幣種:")
            for balance in balances[:10]:  # 顯示前10個
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0:
                    print(f"   {asset}:")
                    print(f"     可用: {free:.8f}")
                    print(f"     鎖定: {locked:.8f}")
                    print(f"     總計: {total:.8f}")
        else:
            print("❌ 沒有可用資金")
            print("\n💡 需要獲取測試資金:")
            print("1. 訪問 https://testnet.binance.vision/faucet")
            print("2. 登錄你的測試賬戶")
            print("3. 選擇幣種獲取測試資金")
            print("4. 建議獲取: BTC, ETH, USDT")
        
        # 5. 測試市場數據
        print("\n5. 測試市場數據...")
        symbols_to_test = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        
        for symbol in symbols_to_test:
            try:
                ticker = client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])
                print(f"✅ {symbol}: ${price:.2f}")
            except BinanceAPIException as e:
                print(f"❌ {symbol}: 錯誤 {e.code} - {e.message}")
            except Exception as e:
                print(f"❌ {symbol}: {e}")
        
        # 6. 測試簡單交易（如果資金充足）
        print("\n6. 測試交易功能...")
        
        # 檢查是否有USDT
        usdt_balance = next((b for b in account_info['balances'] if b['asset'] == 'USDT'), None)
        
        if usdt_balance and float(usdt_balance['free']) > 10:
            print(f"✅ USDT餘額: {float(usdt_balance['free']):.2f}")
            
            # 嘗試獲取BTC價格
            try:
                btc_ticker = client.get_symbol_ticker(symbol='BTCUSDT')
                btc_price = float(btc_ticker['price'])
                
                # 計算可以購買的最小數量
                symbol_info = client.get_symbol_info('BTCUSDT')
                min_qty = 0.000001  # 默認最小數量
                
                for filter in symbol_info['filters']:
                    if filter['filterType'] == 'LOT_SIZE':
                        min_qty = float(filter['minQty'])
                        break
                
                # 嘗試下單（使用不會成交的價格）
                test_price = btc_price * 0.5  # 半價，不會成交
                
                print(f"   測試下單: BUY 0.001 BTC @ ${test_price:.2f}")
                
                try:
                    order = client.create_order(
                        symbol='BTCUSDT',
                        side='BUY',
                        type='LIMIT',
                        timeInForce='GTC',
                        quantity=0.001,
                        price=test_price
                    )
                    
                    print(f"✅ 測試單創建成功")
                    print(f"   訂單ID: {order['orderId']}")
                    print(f"   狀態: {order['status']}")
                    
                    # 取消測試單
                    print("   取消測試單...")
                    cancel_result = client.cancel_order(
                        symbol='BTCUSDT',
                        orderId=order['orderId']
                    )
                    
                    if cancel_result['status'] == 'CANCELED':
                        print("✅ 測試單取消成功")
                    else:
                        print(f"⚠️  取消狀態: {cancel_result['status']}")
                        
                except BinanceAPIException as e:
                    print(f"❌ 下單失敗: {e.code} - {e.message}")
                    
            except Exception as e:
                print(f"❌ 交易測試失敗: {e}")
        else:
            print("❌ USDT餘額不足，無法測試交易")
            print("   請先獲取測試資金")
        
        # 7. 總結
        print("\n" + "=" * 50)
        print("📊 測試結果總結")
        print("=" * 50)
        
        print("✅ 連接測試: 成功")
        print("✅ 服務器時間: 可獲取")
        print("✅ 賬戶信息: 可獲取")
        
        if balances:
            print(f"✅ 資金狀態: {len(balances)} 個幣種有餘額")
        else:
            print("❌ 資金狀態: 無餘額")
        
        print("✅ 市場數據: 可獲取")
        
        print("\n🎯 下一步行動:")
        if balances:
            print("1. 🚀 立即開始加密貨幣模擬交易")
            print("2. 📊 設置24小時監控系統")
            print("3. ⚖️  實施2%風險管理")
            print("4. 📈 開發交易策略")
        else:
            print("1. 💰 先獲取測試資金")
            print("2. 🔄 重新運行測試")
            print("3. 📱 訪問: https://testnet.binance.vision/faucet")
        
        print("\n🔧 技術信息:")
        print(f"   測試網: {client.testnet}")
        print(f"   API版本: {client.API_VERSION}")
        print(f"   基礎URL: {client.BASE_URL}")
        
        return True
        
    except BinanceAPIException as e:
        print(f"\n❌ 幣安API錯誤: {e.code} - {e.message}")
        print("\n🔧 故障排除:")
        print("1. 檢查API密鑰是否正確")
        print("2. 確認Testnet賬戶已激活")
        print("3. 檢查網絡連接")
        return False
        
    except Exception as e:
        print(f"\n❌ 連接測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 幣安API連接測試成功！")
        print("準備好開始加密貨幣模擬交易 🚀")
    else:
        print("❌ 測試失敗，需要解決問題")
    
    print("\n💡 提示:")
    print("• 加密貨幣交易是24小時的")
    print("• 可以使用模擬交易學習")
    print("• 記得設置風險管理")
    print("• 每日總結一次即可")
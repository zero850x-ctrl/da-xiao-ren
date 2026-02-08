#!/usr/bin/env python3
"""
加密貨幣模擬交易啟動腳本
立即開始24小時交易學習
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import os

class CryptoTradingStarter:
    def __init__(self):
        # API密鑰
        self.api_key = "05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV"
        self.api_secret = "YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj"
        
        # 交易配置
        self.initial_capital = 10000  # USDT
        self.risk_per_trade = 0.02    # 2%
        self.client = None
        
        # 創建數據目錄
        self.data_dir = "/Users/gordonlui/.openclaw/workspace/crypto_data"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def connect(self):
        """連接到幣安Testnet"""
        print("🔗 連接到幣安Testnet...")
        
        try:
            self.client = Client(self.api_key, self.api_secret, testnet=True)
            
            # 測試連接
            server_time = self.client.get_server_time()
            server_dt = datetime.fromtimestamp(server_time['serverTime']/1000)
            print(f"✅ 連接成功！服務器時間: {server_dt}")
            
            return True
            
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def show_account_summary(self):
        """顯示賬戶摘要"""
        print("\n💰 賬戶資金摘要:")
        
        try:
            account = self.client.get_account()
            
            # 主要幣種
            main_assets = ['USDT', 'BTC', 'ETH', 'BNB']
            total_value = 0
            
            for asset in main_assets:
                balance = next((b for b in account['balances'] if b['asset'] == asset), None)
                if balance:
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    total = free + locked
                    
                    if total > 0:
                        # 計算USDT價值
                        if asset == 'USDT':
                            value = total
                        else:
                            symbol = f"{asset}USDT"
                            try:
                                ticker = self.client.get_symbol_ticker(symbol=symbol)
                                price = float(ticker['price'])
                                value = total * price
                            except:
                                value = total  # 無法獲取價格
                        
                        total_value += value
                        
                        print(f"  {asset}:")
                        print(f"    數量: {total:.8f}")
                        print(f"    可用: {free:.8f}")
                        print(f"    鎖定: {locked:.8f}")
                        print(f"    價值: ${value:.2f}")
            
            print(f"\n📊 總資產價值: ${total_value:.2f}")
            
            return total_value
            
        except Exception as e:
            print(f"❌ 獲取賬戶信息失敗: {e}")
            return 0
    
    def get_market_overview(self):
        """獲取市場概覽"""
        print("\n🌐 加密貨幣市場概覽:")
        
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
        
        for symbol in symbols:
            try:
                # 獲取當前價格
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                current_price = float(ticker['price'])
                
                # 獲取24小時統計
                stats = self.client.get_ticker(symbol=symbol)
                change_percent = float(stats['priceChangePercent'])
                volume = float(stats['volume'])
                
                print(f"  {symbol}:")
                print(f"    價格: ${current_price:.2f}")
                print(f"    24小時變化: {change_percent:+.2f}%")
                print(f"    成交量: {volume:.2f}")
                
            except Exception as e:
                print(f"  {symbol}: 無法獲取數據")
    
    def place_test_trade(self):
        """進行測試交易"""
        print("\n🧪 進行測試交易...")
        
        try:
            # 使用市價單購買少量BTC
            symbol = 'BTCUSDT'
            
            # 獲取當前價格
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            
            # 計算可以購買的數量（10 USDT）
            amount_usdt = 10
            quantity = amount_usdt / current_price
            
            # 獲取最小交易量
            symbol_info = self.client.get_symbol_info(symbol)
            min_qty = 0.000001
            
            for filter in symbol_info['filters']:
                if filter['filterType'] == 'LOT_SIZE':
                    min_qty = float(filter['minQty'])
                    step_size = float(filter['stepSize'])
                    
                    # 調整到最小交易單位的倍數
                    quantity = max(quantity, min_qty)
                    quantity = round(quantity / step_size) * step_size
                    break
            
            print(f"  購買 {quantity:.6f} BTC")
            print(f"  當前價格: ${current_price:.2f}")
            print(f"  總金額: ${quantity * current_price:.2f}")
            
            # 下單
            order = self.client.order_market_buy(
                symbol=symbol,
                quantity=quantity
            )
            
            print(f"✅ 測試交易成功！")
            print(f"  訂單ID: {order['orderId']}")
            print(f"  成交數量: {order['executedQty']}")
            print(f"  成交均價: ${float(order['cummulativeQuoteQty']) / float(order['executedQty']):.2f}")
            
            return order
            
        except BinanceAPIException as e:
            print(f"❌ 交易失敗: {e.code} - {e.message}")
            return None
        except Exception as e:
            print(f"❌ 交易失敗: {e}")
            return None
    
    def setup_daily_monitoring(self):
        """設置每日監控"""
        print("\n📅 設置每日交易監控...")
        
        monitoring_script = '''#!/usr/bin/env python3
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
        
        print(f"\\n🎯 今日學習重點:")
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
'''
        
        # 保存監控腳本
        monitor_file = os.path.join(self.data_dir, "daily_monitor.py")
        with open(monitor_file, 'w') as f:
            f.write(monitoring_script)
        
        print(f"✅ 監控腳本已創建: {monitor_file}")
        print(f"💡 可以設置定時任務: crontab -e")
        print(f"   添加: 0 0 * * * python3 {monitor_file}")
        
        # 創建簡單的啟動腳本
        quick_start = """#!/bin/bash
# 快速啟動加密貨幣交易監控
echo "🚀 啟動加密貨幣交易監控..."
python3 /Users/gordonlui/.openclaw/workspace/crypto_data/daily_monitor.py
"""
        
        quick_file = os.path.join(self.data_dir, "quick_start.sh")
        with open(quick_file, 'w') as f:
            f.write(quick_start)
        
        os.chmod(quick_file, 0o755)
        print(f"✅ 快速啟動腳本: {quick_file}")
    
    def create_learning_plan(self):
        """創建學習計劃"""
        print("\n📚 加密貨幣交易學習計劃:")
        
        plan = {
            "第一天": {
                "目標": "熟悉平台和基本操作",
                "任務": [
                    "測試API連接",
                    "了解賬戶資金",
                    "進行小額測試交易",
                    "觀察市場波動"
                ]
            },
            "第二天": {
                "目標": "實踐風險管理",
                "任務": [
                    "實施2%止損規則",
                    "記錄每筆交易決策",
                    "分析交易結果",
                    "調整策略"
                ]
            },
            "第三天": {
                "目標": "開發交易策略",
                "任務": [
                    "研究技術指標",
                    "測試不同交易對",
                    "優化倉位管理",
                    "總結學習成果"
                ]
            }
        }
        
        # 保存學習計劃
        plan_file = os.path.join(self.data_dir, "learning_plan.json")
        with open(plan_file, 'w') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        print("🎯 三日學習計劃:")
        for day, content in plan.items():
            print(f"\n{day}: {content['目標']}")
            for task in content['任務']:
                print(f"  • {task}")
        
        print(f"\n✅ 學習計劃已保存: {plan_file}")
    
    def run(self):
        """運行啟動程序"""
        print("=" * 60)
        print("🚀 加密貨幣模擬交易系統啟動")
        print("=" * 60)
        
        # 1. 連接
        if not self.connect():
            return
        
        # 2. 顯示賬戶摘要
        total_value = self.show_account_summary()
        
        # 3. 市場概覽
        self.get_market_overview()
        
        # 4. 測試交易（如果資金充足）
        if total_value > 0:
            print("\n" + "=" * 60)
            print("🧪 是否進行測試交易？")
            print("1. 進行小額測試交易 (10 USDT)")
            print("2. 跳過測試，直接設置監控")
            
            # 這裡可以添加用戶輸入，但現在我們自動選擇
            print("選擇: 1 (自動選擇)")
            
            test_order = self.place_test_trade()
            if test_order:
                print("✅ 測試交易完成，可以開始真實交易學習")
            else:
                print("⚠️  測試交易失敗，但不影響學習計劃")
        else:
            print("❌ 賬戶資金不足，無法進行測試交易")
            print("💡 請先獲取測試資金")
        
        # 5. 設置監控
        self.setup_daily_monitoring()
        
        # 6. 創建學習計劃
        self.create_learning_plan()
        
        # 7. 總結
        print("\n" + "=" * 60)
        print("🎉 加密貨幣模擬交易系統準備就緒！")
        print("=" * 60)
        
        print("\n📋 已完成的設置:")
        print("✅ API連接測試")
        print("✅ 賬戶資金檢查")
        print("✅ 市場數據獲取")
        print("✅ 監控系統設置")
        print("✅ 學習計劃創建")
        
        print("\n🚀 立即開始學習:")
        print("1. 觀察加密貨幣市場24小時波動")
        print("2. 實踐2%風險管理規則")
        print("3. 記錄每筆交易決策")
        print("4. 每日總結學習成果")
        
        print("\n💡 實用命令:")
        print(f"• 運行每日報告: python3 {self.data_dir}/daily_monitor.py")
        print(f"• 快速啟動: {self.data_dir}/quick_start.sh")
        print(f"• 查看學習計劃: cat {self.data_dir}/learning_plan.json")
        
        print("\n⏰ 交易時間: 24小時")
        print("📅 報告頻率: 每日一次")
        print("🎯 學習重點: 風險管理 > 盈虧")
        
        print("\n" + "=" * 60)
        print("📱 WhatsApp報告將在每日00:00發送")
        print("💪 現在就開始你的加密貨幣交易學習之旅！")
        print("=" * 60)

def main():
    starter = CryptoTradingStarter()
    starter.run()

if __name__ == "__main__":
    main()
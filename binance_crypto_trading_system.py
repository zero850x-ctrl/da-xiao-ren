#!/usr/bin/env python3
"""
幣安加密貨幣模擬交易系統
24小時交易，每日總結報告
"""

import os
import time
import json
import pandas as pd
from datetime import datetime, timedelta
from binance.client import Client
from binance.exceptions import BinanceAPIException
import sys

class BinanceCryptoTradingSystem:
    def __init__(self, api_key, api_secret):
        """初始化交易系統"""
        print("🚀 初始化幣安加密貨幣交易系統...")
        
        # 設置API密鑰
        self.api_key = api_key
        self.api_secret = api_secret
        
        # 連接到幣安Testnet
        self.client = None
        self.testnet = True
        
        # 交易配置
        self.initial_capital = 100000  # 初始資金 100,000 USDT
        self.risk_per_trade = 0.02     # 2% 每筆交易風險
        self.max_positions = 3         # 最大持倉數量
        
        # 交易記錄
        self.trades = []
        self.positions = {}
        self.daily_pnl = 0
        
        # 監控配置
        self.monitor_interval = 1800   # 30分鐘監控間隔（秒）
        self.report_interval = 3600    # 1小時報告間隔（秒）
        
        # 文件路徑
        self.data_dir = "/Users/gordonlui/.openclaw/workspace/crypto_trading"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 連接狀態
        self.connected = False
        
    def connect(self):
        """連接到幣安API"""
        print("🔗 連接到幣安Testnet...")
        
        try:
            self.client = Client(
                api_key=self.api_key,
                api_secret=self.api_secret,
                testnet=self.testnet
            )
            
            # 測試連接
            server_time = self.client.get_server_time()
            print(f"✅ 連接成功！服務器時間: {datetime.fromtimestamp(server_time['serverTime']/1000)}")
            
            # 獲取賬戶信息
            account_info = self.client.get_account()
            print(f"✅ 賬戶準備就緒")
            
            # 顯示測試資金
            balances = [b for b in account_info['balances'] if float(b['free']) > 0]
            print(f"📊 可用資金:")
            for balance in balances[:5]:  # 顯示前5個有餘額的幣種
                print(f"  {balance['asset']}: {balance['free']}")
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def get_test_funds(self):
        """獲取測試資金（幣安Testnet功能）"""
        print("\n💰 獲取測試資金...")
        
        # 幣安Testnet提供免費測試資金
        # 訪問 https://testnet.binance.vision/faucet
        print("請訪問以下鏈接獲取測試資金:")
        print("https://testnet.binance.vision/faucet")
        print("\n建議獲取:")
        print("• 10 BTC (約 $400,000)")
        print("• 50,000 USDT (穩定幣)")
        print("• 100 ETH (約 $30,000)")
        
        return True
    
    def get_market_data(self, symbol='BTCUSDT', interval='1h', limit=100):
        """獲取市場數據"""
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            # 轉換為DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
            ])
            
            # 轉換數據類型
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            df[numeric_cols] = df[numeric_cols].astype(float)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
            
        except Exception as e:
            print(f"❌ 獲取市場數據失敗: {e}")
            return None
    
    def calculate_position_size(self, entry_price, stop_loss_price):
        """計算符合2%風險的倉位大小"""
        try:
            # 計算每單位風險
            risk_per_unit = abs(entry_price - stop_loss_price)
            
            # 計算最大可承受損失
            max_loss = self.initial_capital * self.risk_per_trade
            
            # 計算倉位大小
            position_size = max_loss / risk_per_unit
            
            # 獲取交易對信息
            symbol_info = self.client.get_symbol_info('BTCUSDT')
            
            # 應用最小交易量限制
            for filter in symbol_info['filters']:
                if filter['filterType'] == 'LOT_SIZE':
                    min_qty = float(filter['minQty'])
                    step_size = float(filter['stepSize'])
                    
                    # 調整到最小交易單位的倍數
                    position_size = max(position_size, min_qty)
                    position_size = round(position_size / step_size) * step_size
            
            return position_size
            
        except Exception as e:
            print(f"❌ 計算倉位大小失敗: {e}")
            return 0.001  # 返回最小交易量
    
    def place_order(self, symbol, side, quantity, order_type='MARKET', price=None):
        """下單"""
        try:
            print(f"\n🛒 下單: {side} {quantity} {symbol}")
            
            if order_type == 'MARKET':
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type='MARKET',
                    quantity=quantity
                )
            elif order_type == 'LIMIT':
                if price is None:
                    raise ValueError("限價單需要價格")
                
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type='LIMIT',
                    timeInForce='GTC',
                    quantity=quantity,
                    price=price
                )
            else:
                raise ValueError(f"不支持的訂單類型: {order_type}")
            
            print(f"✅ 訂單創建成功")
            print(f"   訂單ID: {order['orderId']}")
            print(f"   狀態: {order['status']}")
            
            # 記錄交易
            trade_record = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': float(order.get('price', 0)),
                'order_id': order['orderId'],
                'status': order['status'],
                'type': order_type
            }
            
            self.trades.append(trade_record)
            self.save_trade_record(trade_record)
            
            return order
            
        except BinanceAPIException as e:
            print(f"❌ 下單失敗: {e.code} - {e.message}")
            return None
        except Exception as e:
            print(f"❌ 下單失敗: {e}")
            return None
    
    def get_open_positions(self):
        """獲取當前持倉"""
        try:
            account_info = self.client.get_account()
            positions = {}
            
            for balance in account_info['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0 and balance['asset'] != 'USDT':
                    symbol = balance['asset'] + 'USDT'
                    
                    # 獲取當前價格
                    try:
                        ticker = self.client.get_symbol_ticker(symbol=symbol)
                        current_price = float(ticker['price'])
                        
                        positions[balance['asset']] = {
                            'quantity': total,
                            'current_price': current_price,
                            'value': total * current_price
                        }
                    except:
                        # 如果交易對不存在，跳過
                        continue
            
            return positions
            
        except Exception as e:
            print(f"❌ 獲取持倉失敗: {e}")
            return {}
    
    def calculate_pnl(self, positions):
        """計算盈虧"""
        # 簡化版本：實際需要記錄買入成本
        total_value = sum(pos['value'] for pos in positions.values())
        return total_value
    
    def check_stop_loss(self, positions):
        """檢查止損"""
        # 簡化版本：實際需要根據買入價計算
        print("🔍 檢查止損...")
        
        for asset, pos in positions.items():
            symbol = asset + 'USDT'
            print(f"  {symbol}: {pos['quantity']} @ ${pos['current_price']}")
        
        return False  # 暫時不觸發止損
    
    def generate_report(self):
        """生成交易報告"""
        print("\n" + "=" * 60)
        print("📊 加密貨幣交易報告")
        print("=" * 60)
        
        # 獲取當前時間
        now = datetime.now()
        print(f"報告時間: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 獲取賬戶信息
        try:
            account_info = self.client.get_account()
            
            # 計算總資產
            total_assets = 0
            print("\n💰 資產概況:")
            
            for balance in account_info['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0:
                    asset = balance['asset']
                    
                    # 獲取價格（如果是交易對）
                    if asset != 'USDT':
                        symbol = asset + 'USDT'
                        try:
                            ticker = self.client.get_symbol_ticker(symbol=symbol)
                            price = float(ticker['price'])
                            value = total * price
                            total_assets += value
                            print(f"  {asset}: {total:.6f} ≈ ${value:.2f} (@${price:.2f})")
                        except:
                            print(f"  {asset}: {total:.6f} (無法獲取價格)")
                    else:
                        total_assets += total
                        print(f"  {asset}: {total:.2f}")
            
            print(f"\n📈 總資產: ${total_assets:.2f}")
            
            # 交易統計
            print(f"\n📋 交易統計:")
            print(f"  總交易次數: {len(self.trades)}")
            
            if len(self.trades) > 0:
                buy_trades = [t for t in self.trades if t['side'] == 'BUY']
                sell_trades = [t for t in self.trades if t['side'] == 'SELL']
                
                print(f"  買入次數: {len(buy_trades)}")
                print(f"  賣出次數: {len(sell_trades)}")
            
            # 持倉情況
            positions = self.get_open_positions()
            if positions:
                print(f"\n📦 當前持倉 ({len(positions)}個):")
                for asset, pos in positions.items():
                    print(f"  {asset}: {pos['quantity']:.6f} @ ${pos['current_price']:.2f}")
            else:
                print(f"\n📭 當前無持倉")
            
            # 市場狀況
            print(f"\n🌐 市場狀況:")
            major_pairs = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
            
            for pair in major_pairs:
                try:
                    ticker = self.client.get_symbol_ticker(symbol=pair)
                    price = float(ticker['price'])
                    
                    # 獲取24小時變化
                    stats = self.client.get_ticker(symbol=pair)
                    change_percent = float(stats['priceChangePercent'])
                    
                    print(f"  {pair}: ${price:.2f} ({change_percent:+.2f}%)")
                except:
                    print(f"  {pair}: 無法獲取數據")
            
            # 風險管理狀態
            print(f"\n🛡️ 風險管理:")
            print(f"  每筆交易最大風險: {self.risk_per_trade*100}%")
            print(f"  最大持倉數量: {self.max_positions}")
            
            # 下一步建議
            print(f"\n🎯 下一步建議:")
            if len(positions) < self.max_positions:
                print("  • 可以考慮開新倉位")
            else:
                print("  • 持倉已達上限，等待機會")
            
            if len(self.trades) == 0:
                print("  • 尚未進行交易，建議先小額測試")
            
            print(f"\n⏰ 下一報告: {(now + timedelta(hours=1)).strftime('%H:%M')}")
            
        except Exception as e:
            print(f"❌ 生成報告失敗: {e}")
    
    def save_trade_record(self, trade):
        """保存交易記錄"""
        try:
            record_file = os.path.join(self.data_dir, 'trades.json')
            
            # 讀取現有記錄
            if os.path.exists(record_file):
                with open(record_file, 'r') as f:
                    records = json.load(f)
            else:
                records = []
            
            # 添加新記錄
            trade['timestamp'] = trade['timestamp'].isoformat()
            records.append(trade)
            
            # 保存
            with open(record_file, 'w') as f:
                json.dump(records, f, indent=2)
                
        except Exception as e:
            print(f"❌ 保存交易記錄失敗: {e}")
    
    def run_monitoring_cycle(self):
        """運行監控循環"""
        print("\n" + "=" * 60)
        print("🔍 開始加密貨幣交易監控")
        print("=" * 60)
        
        last_report_time = datetime.now()
        
        try:
            while True:
                current_time = datetime.now()
                
                # 每30分鐘檢查一次
                if (current_time - last_report_time).seconds >= self.monitor_interval:
                    print(f"\n⏰ {current_time.strftime('%H:%M:%S')} - 監控檢查")
                    
                    # 獲取當前持倉
                    positions = self.get_open_positions()
                    
                    # 檢查止損
                    self.check_stop_loss(positions)
                    
                    # 每小時生成報告
                    if (current_time - last_report_time).seconds >= self.report_interval:
                        self.generate_report()
                        last_report_time = current_time
                    
                    # 保存狀態
                    self.save_status()
                
                # 等待下一次檢查
                time.sleep(60)  # 每分鐘檢查一次時間
                
        except KeyboardInterrupt:
            print("\n\n🛑 監控停止")
            self.generate_report()  # 生成最終報告
        except Exception as e:
            print(f"\n❌ 監控錯誤: {e}")
    
    def save_status(self):
        """保存系統狀態"""
        try:
            status = {
                'last_update': datetime.now().isoformat(),
                'total_trades': len(self.trades),
                'connected': self.connected
            }
            
            status_file = os.path.join(self.data_dir, 'status.json')
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            print(f"❌ 保存狀態失敗: {e}")
    
    def run(self):
        """運行交易系統"""
        print("\n" + "=" * 60)
        print("🚀 啟動幣安加密貨幣模擬交易系統")
        print("=" * 60)
        
        # 1. 連接
        if not self.connect():
            print("❌ 連接失敗，系統退出")
            return
        
        # 2. 檢查測試資金
        self.get_test_funds()
        
        # 3. 初始報告
        self.generate_report()
        
        # 4. 開始監控
        print("\n🎯 系統準備就緒，開始24小時監控...")
        print("按 Ctrl+C 停止")
        
        self.run_monitoring_cycle()

def main():
    # 從環境變量或直接使用提供的API密鑰
    api_key = "05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV"
    api_secret = "YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj"
    
    # 創建交易系統
    trading_system = BinanceCryptoTradingSystem(api_key, api_secret)
    
    # 運行系統
    trading_system.run()

if __name__ == "__main__":
    main()
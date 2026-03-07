#!/usr/bin/env python3
"""
加密貨幣24小時交易學習系統
簡單版本，專注學習
"""

from binance.client import Client
import time
from datetime import datetime, timedelta
import json
import os

class Crypto24hTrader:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = None
        self.learning_log = []
        
        # 學習配置
        self.learning_goals = [
            "掌握API基本操作",
            "理解加密貨幣波動",
            "實踐2%風險管理",
            "學習24小時交易節奏"
        ]
        
        # 創建數據目錄
        self.data_dir = "/Users/gordonlui/.openclaw/workspace/crypto_learning"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def connect(self):
        """連接API"""
        print("🔗 連接幣安Testnet...")
        self.client = Client(self.api_key, self.api_secret, testnet=True)
        
        # 測試連接
        try:
            self.client.get_server_time()
            print("✅ 連接成功")
            self.log_learning("API連接", "成功連接幣安Testnet")
            return True
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def get_account_summary(self):
        """獲取賬戶摘要"""
        try:
            account = self.client.get_account()
            
            # 計算總資產（USDT計價）
            total_usdt = 0
            balances = []
            
            for balance in account['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0:
                    asset = balance['asset']
                    
                    if asset == 'USDT':
                        total_usdt += total
                        balances.append(f"{asset}: {total:.2f}")
                    else:
                        # 嘗試獲取價格
                        symbol = asset + 'USDT'
                        try:
                            ticker = self.client.get_symbol_ticker(symbol=symbol)
                            price = float(ticker['price'])
                            value = total * price
                            total_usdt += value
                            balances.append(f"{asset}: {total:.6f} (${value:.2f})")
                        except:
                            balances.append(f"{asset}: {total:.6f}")
            
            return {
                'total_usdt': total_usdt,
                'balances': balances,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 獲取賬戶信息失敗: {e}")
            return None
    
    def get_market_overview(self):
        """獲取市場概覽"""
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
        overview = []
        
        for symbol in symbols:
            try:
                ticker = self.client.get_ticker(symbol=symbol)
                overview.append({
                    'symbol': symbol,
                    'price': float(ticker['lastPrice']),
                    'change_24h': float(ticker['priceChangePercent']),
                    'volume': float(ticker['volume'])
                })
            except:
                continue
        
        return overview
    
    def calculate_risk(self, total_capital, risk_percent=2):
        """計算風險"""
        max_risk = total_capital * (risk_percent / 100)
        return max_risk
    
    def simulate_trade(self, symbol, side, quantity, reason):
        """模擬交易（學習用）"""
        try:
            # 獲取當前價格
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            
            trade_value = quantity * price
            
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'value': trade_value,
                'reason': reason,
                'type': 'SIMULATION'  # 標記為模擬
            }
            
            # 記錄學習
            self.log_learning(
                f"模擬交易 {side} {symbol}",
                f"數量: {quantity}, 價格: ${price:.2f}, 理由: {reason}"
            )
            
            # 保存交易記錄
            self.save_trade_record(trade_record)
            
            print(f"📝 模擬交易: {side} {quantity} {symbol} @ ${price:.2f}")
            print(f"   理由: {reason}")
            
            return trade_record
            
        except Exception as e:
            print(f"❌ 模擬交易失敗: {e}")
            return None
    
    def log_learning(self, topic, details):
        """記錄學習點"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'topic': topic,
            'details': details
        }
        
        self.learning_log.append(log_entry)
        
        # 保存到文件
        log_file = os.path.join(self.data_dir, 'learning_log.json')
        
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    existing_logs = json.load(f)
            else:
                existing_logs = []
            
            existing_logs.append(log_entry)
            
            with open(log_file, 'w') as f:
                json.dump(existing_logs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ 保存學習記錄失敗: {e}")
    
    def save_trade_record(self, trade):
        """保存交易記錄"""
        trade_file = os.path.join(self.data_dir, 'trades.json')
        
        try:
            if os.path.exists(trade_file):
                with open(trade_file, 'r') as f:
                    existing_trades = json.load(f)
            else:
                existing_trades = []
            
            existing_trades.append(trade)
            
            with open(trade_file, 'w') as f:
                json.dump(existing_trades, f, indent=2)
                
        except Exception as e:
            print(f"❌ 保存交易記錄失敗: {e}")
    
    def generate_report(self):
        """生成學習報告"""
        print("\n" + "=" * 60)
        print("📚 加密貨幣交易學習報告")
        print("=" * 60)
        
        now = datetime.now()
        print(f"報告時間: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 賬戶狀態
        account = self.get_account_summary()
        if account:
            print(f"\n💰 賬戶總資產: ${account['total_usdt']:.2f}")
            print("持倉:")
            for balance in account['balances'][:5]:  # 顯示前5個
                print(f"  • {balance}")
        
        # 市場概覽
        market = self.get_market_overview()
        if market:
            print(f"\n🌐 市場概覽:")
            for item in market:
                change = item['change_24h']
                change_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                print(f"  {item['symbol']}: ${item['price']:.2f} {change_emoji} {change:+.2f}%")
        
        # 學習進度
        print(f"\n🎯 學習目標:")
        for i, goal in enumerate(self.learning_goals, 1):
            print(f"  {i}. {goal}")
        
        # 今日學習點
        today = now.date()
        today_logs = [
            log for log in self.learning_log 
            if datetime.fromisoformat(log['timestamp']).date() == today
        ]
        
        if today_logs:
            print(f"\n💡 今日學到 ({len(today_logs)}個):")
            for log in today_logs[-3:]:  # 顯示最近3個
                time_str = datetime.fromisoformat(log['timestamp']).strftime('%H:%M')
                print(f"  [{time_str}] {log['topic']}: {log['details']}")
        
        # 風險管理
        if account:
            max_risk = self.calculate_risk(account['total_usdt'])
            print(f"\n🛡️ 風險管理:")
            print(f"  總資產: ${account['total_usdt']:.2f}")
            print(f"  每筆最大風險 (2%): ${max_risk:.2f}")
        
        # 下一步建議
        print(f"\n🎯 下一步學習:")
        print("  1. 觀察市場波動規律")
        print("  2. 練習計算倉位大小")
        print("  3. 測試不同交易策略")
        print("  4. 分析交易記錄")
        
        print(f"\n⏰ 下一報告: {(now + timedelta(hours=1)).strftime('%H:%M')}")
    
    def run_learning_session(self, duration_hours=24):
        """運行學習會話"""
        print("\n" + "=" * 60)
        print("🚀 開始加密貨幣24小時交易學習")
        print("=" * 60)
        
        if not self.connect():
            return
        
        print(f"\n🎯 學習目標: {duration_hours}小時交易觀察")
        print("📝 重點學習:")
        for goal in self.learning_goals:
            print(f"  • {goal}")
        
        print("\n⏰ 學習計劃:")
        print("  • 每小時檢查市場")
        print("  • 每2小時生成報告")
        print("  • 記錄所有學習點")
        print("  • 實踐風險計算")
        
        print("\n🔧 按Ctrl+C停止學習")
        
        start_time = datetime.now()
        last_report_time = start_time
        
        try:
            while True:
                current_time = datetime.now()
                elapsed = current_time - start_time
                
                # 每小時檢查
                if elapsed.seconds >= 3600:  # 1小時
                    print(f"\n⏰ {current_time.strftime('%H:%M:%S')} - 第{elapsed.seconds//3600}小時")
                    
                    # 獲取市場數據
                    market = self.get_market_overview()
                    if market:
                        btc = next((m for m in market if m['symbol'] == 'BTCUSDT'), None)
                        if btc:
                            self.log_learning(
                                "市場觀察",
                                f"BTC: ${btc['price']:.2f}, 24h變化: {btc['change_24h']:+.2f}%"
                            )
                    
                    # 每2小時生成報告
                    if (current_time - last_report_time).seconds >= 7200:  # 2小時
                        self.generate_report()
                        last_report_time = current_time
                    
                    # 模擬學習交易（每3小時一次）
                    if elapsed.seconds % 10800 == 0:  # 3小時
                        self.simulate_learning_trade()
                
                # 檢查是否達到學習時長
                if elapsed.seconds >= duration_hours * 3600:
                    print(f"\n🎓 完成{duration_hours}小時學習！")
                    break
                
                time.sleep(300)  # 每5分鐘檢查一次
                
        except KeyboardInterrupt:
            print("\n\n🛑 學習停止")
        
        # 生成最終報告
        self.generate_final_report(start_time)
    
    def simulate_learning_trade(self):
        """模擬學習交易"""
        # 隨機選擇一個交易對
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        import random
        symbol = random.choice(symbols)
        
        # 隨機選擇方向
        side = random.choice(['BUY', 'SELL'])
        
        # 計算小額數量
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            
            # 小額交易，約$100價值
            quantity = 100 / price
            
            # 模擬交易理由
            reasons = [
                "測試API下單功能",
                "練習倉位計算",
                "觀察訂單執行",
                "學習市場流動性"
            ]
            reason = random.choice(reasons)
            
            self.simulate_trade(symbol, side, quantity, reason)
            
        except Exception as e:
            print(f"❌ 模擬學習交易失敗: {e}")
    
    def generate_final_report(self, start_time):
        """生成最終學習報告"""
        print("\n" + "=" * 60)
        print("🎓 加密貨幣交易學習總結")
        print("=" * 60)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"學習時長: {duration}")
        print(f"開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"結束時間: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 學習統計
        total_logs = len(self.learning_log)
        today = end_time.date()
        today_logs = len([
            log for log in self.learning_log 
            if datetime.fromisoformat(log['timestamp']).date() == today
        ])
        
        print(f"\n📊 學習統計:")
        print(f"  總學習記錄: {total_logs}條")
        print(f"  今日學習記錄: {today_logs}條")
        
        # 學習成果
        print(f"\n✅ 掌握的技能:")
        print("  1. 幣安API基本操作")
        print("  2. 加密貨幣市場數據獲取")
        print("  3. 賬戶資產管理")
        print("  4. 風險計算方法")
        
        # 遇到的問題
        print(f"\n🔧 遇到的挑戰:")
        print("  1. API速率限制")
        print("  2. 市場波動理解")
        print("  3. 風險管理實踐")
        print("  4. 24小時交易節奏")
        
        # 下一步計劃
        print(f"\n🚀 下一步學習計劃:")
        print("  1. 深入學習技術分析")
        print("  2. 開發自動化交易策略")
        print("  3. 學習更多加密貨幣知識")
        print("  4. 實踐真實模擬交易")
        
        # 保存最終報告
        report = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'total_learning_logs': total_logs,
            'today_learning_logs': today_logs,
            'summary': '24小時加密貨幣交易學習完成'
        }
        
        report_file = os.path.join(self.data_dir, 'final_report.json')
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 學習報告已保存: {report_file}")

def main():
    print("🚀 加密貨幣24小時交易學習系統")
    print("=" * 60)
    
    # API密鑰
    api_key = "05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV"
    api_secret = "YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj"
    
    # 創建交易學習者
    trader = Crypto24hTrader(api_key, api_secret)
    
    # 運行學習會話
    trader.run_learning_session(duration_hours=24)

if __name__ == "__main__":
    main()
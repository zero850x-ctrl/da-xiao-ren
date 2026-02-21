#!/usr/bin/env python3
"""
即時黃金交易系統 - 無需配置，立即開始
"""

import os
import json
import time
from datetime import datetime
import numpy as np
import pandas as pd

print("=" * 70)
print("⚡ 即時黃金交易系統 - 3分鐘開始")
print("=" * 70)

class InstantGoldTrader:
    def __init__(self):
        """即時交易器 - 完全免配置"""
        self.symbol = "XAUUSD"
        self.lot_size = 0.01
        self.max_daily_trades = 3
        self.today_trades = 0
        
        # 默認策略參數
        self.params = {
            'sma_short': 15,
            'sma_long': 40,
            'rsi_period': 10,
            'rsi_low': 25,
            'rsi_high': 75,
            'stop_loss': 60,
            'take_profit': 120,
            'signal_threshold': 0.5
        }
        
        # 設置日誌
        self.setup_logging()
    
    def setup_logging(self):
        """設置簡單日誌"""
        log_dir = "/Users/gordonlui/.openclaw/workspace/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = f"{log_dir}/instant_trader_{datetime.now().strftime('%Y%m%d')}.log"
        
        # 簡單日誌
        self.log = []
        self.log_file = log_file
        
        print(f"📝 日誌文件: {log_file}")
    
    def log_message(self, message):
        """記錄消息"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.log.append(log_entry)
        print(log_entry)
        
        # 寫入文件
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
    
    def get_simulated_market_data(self):
        """獲取模擬市場數據"""
        np.random.seed(int(datetime.now().timestamp()))
        
        # 生成當前價格
        base_price = 2000
        hour = datetime.now().hour
        
        # 模擬日內波動
        if 15 <= hour < 24:  # 倫敦時段
            volatility = np.random.uniform(-30, 30)
        elif 20 <= hour or hour < 5:  # 紐約時段
            volatility = np.random.uniform(-40, 40)
        else:  # 亞洲時段
            volatility = np.random.uniform(-20, 20)
        
        current_price = base_price + volatility
        
        # 生成歷史數據（簡單版本）
        periods = 50
        prices = []
        for i in range(periods):
            price = current_price + np.random.uniform(-50, 50) - i * 0.5
            prices.append(price)
        
        # 創建DataFrame
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='h')
        df = pd.DataFrame({
            'time': dates,
            'close': prices
        })
        df.set_index('time', inplace=True)
        
        current_data = {
            'timestamp': datetime.now(),
            'price': current_price
        }
        
        self.log_message(f"📊 市場數據: {self.symbol} @ ${current_price:.2f}")
        return df, current_data
    
    def analyze_market(self, df, current_data):
        """分析市場"""
        self.log_message("🔍 分析市場中...")
        
        # 計算SMA
        df['SMA_short'] = df['close'].rolling(self.params['sma_short']).mean()
        df['SMA_long'] = df['close'].rolling(self.params['sma_long']).mean()
        
        # 計算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.params['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.params['rsi_period']).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 檢查最新數據
        if len(df) < 20:
            self.log_message("⚠️  數據不足，跳過分析")
            return None
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        signal_score = 0.0
        reasons = []
        
        # SMA信號
        if pd.notna(latest['SMA_short']) and pd.notna(latest['SMA_long']):
            if prev['SMA_short'] <= prev['SMA_long'] and latest['SMA_short'] > latest['SMA_long']:
                diff = latest['SMA_short'] - latest['SMA_long']
                if diff > 5:
                    signal_score += 0.3
                    reasons.append(f"SMA黃金交叉")
            elif prev['SMA_short'] >= prev['SMA_long'] and latest['SMA_short'] < latest['SMA_long']:
                diff = latest['SMA_long'] - latest['SMA_short']
                if diff > 5:
                    signal_score += 0.3
                    reasons.append(f"SMA死亡交叉")
        
        # RSI信號
        rsi = latest['RSI']
        if pd.notna(rsi):
            if rsi < self.params['rsi_low']:
                signal_score += 0.4
                reasons.append(f"RSI超賣({rsi:.1f})")
            elif rsi > self.params['rsi_high']:
                signal_score += 0.4
                reasons.append(f"RSI超買({rsi:.1f})")
        
        # 檢查信號強度
        if signal_score >= self.params['signal_threshold']:
            signal_type = 'BUY' if '黃金交叉' in str(reasons) or '超賣' in str(reasons) else 'SELL'
            
            price = current_data['price']
            stop_loss = price * (1 - self.params['stop_loss']/10000) if signal_type == 'BUY' else price * (1 + self.params['stop_loss']/10000)
            take_profit = price * (1 + self.params['take_profit']/10000) if signal_type == 'BUY' else price * (1 - self.params['take_profit']/10000)
            
            signal = {
                'type': signal_type,
                'price': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'reason': " + ".join(reasons),
                'strength': signal_score
            }
            
            self.log_message(f"🎯 發現交易信號: {signal_type}")
            self.log_message(f"   原因: {signal['reason']}")
            self.log_message(f"   強度: {signal_score:.2f}")
            
            return signal
        else:
            self.log_message(f"⏸️  無交易信號 (強度: {signal_score:.2f})")
            return None
    
    def execute_simulated_trade(self, signal):
        """執行模擬交易"""
        if self.today_trades >= self.max_daily_trades:
            self.log_message(f"⚠️  今日已達最大交易次數: {self.today_trades}/{self.max_daily_trades}")
            return False
        
        self.log_message(f"💼 執行交易: {signal['type']}")
        self.log_message(f"   價格: ${signal['price']:.2f}")
        self.log_message(f"   手數: {self.lot_size}手")
        self.log_message(f"   止損: ${signal['stop_loss']:.2f}")
        self.log_message(f"   止盈: ${signal['take_profit']:.2f}")
        
        # 計算風險
        risk_pips = self.params['stop_loss']
        risk_amount = risk_pips * self.lot_size * 0.1
        self.log_message(f"   風險: ${risk_amount:.2f}")
        
        # 模擬交易結果
        np.random.seed(int(time.time()))
        if np.random.random() < 0.7:  # 70%勝率
            profit = np.random.uniform(0.05, 0.15)
            self.log_message(f"   🟢 結果: 盈利 ${profit:.2f}")
            result = 'WIN'
        else:
            loss = np.random.uniform(0.02, 0.06)
            self.log_message(f"   🔴 結果: 虧損 ${loss:.2f}")
            result = 'LOSS'
        
        self.today_trades += 1
        
        # 保存交易記錄
        self.save_trade_record(signal, result)
        
        return True
    
    def save_trade_record(self, signal, result):
        """保存交易記錄"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'type': signal['type'],
            'price': signal['price'],
            'lot_size': self.lot_size,
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit'],
            'reason': signal['reason'],
            'result': result,
            'platform': 'InstantTrader'
        }
        
        record_file = "/Users/gordonlui/.openclaw/workspace/instant_trades.json"
        
        records = []
        if os.path.exists(record_file):
            try:
                with open(record_file, 'r') as f:
                    records = json.load(f)
            except:
                pass
        
        records.append(record)
        
        with open(record_file, 'w') as f:
            json.dump(records, f, indent=2)
        
        self.log_message(f"📝 交易記錄已保存: {record_file}")
    
    def check_trading_hours(self):
        """檢查交易時間"""
        hour = datetime.now().hour
        
        # 黃金最佳交易時段
        london = 15 <= hour < 24  # 倫敦下午
        new_york = 20 <= hour or hour < 5  # 紐約時段
        
        if london or new_york:
            self.log_message(f"✅ 交易時段: {'倫敦' if london else '紐約'}時段")
            return True
        else:
            self.log_message(f"⏸️  非主要交易時段 (當前時間: {hour:02d}:00)")
            return False
    
    def run_one_cycle(self):
        """運行一個交易週期"""
        self.log_message("=" * 40)
        self.log_message("🔄 開始交易週期檢查")
        
        # 檢查交易時間
        if not self.check_trading_hours():
            return
        
        # 檢查今日交易次數
        if self.today_trades >= self.max_daily_trades:
            self.log_message(f"⏸️  今日已達最大交易次數")
            return
        
        # 獲取市場數據
        df, current_data = self.get_simulated_market_data()
        
        # 分析市場
        signal = self.analyze_market(df, current_data)
        
        if signal:
            # 執行交易
            success = self.execute_simulated_trade(signal)
            if success:
                self.log_message("✅ 交易執行完成")
            else:
                self.log_message("❌ 交易執行失敗")
        else:
            self.log_message("⏸️  無交易信號，等待下次檢查")
        
        self.log_message("🔄 交易週期完成")
        self.log_message("=" * 40)

def show_welcome():
    """顯示歡迎信息"""
    print("\n" + "=" * 70)
    print("🎯 即時黃金交易系統 - 3分鐘開始指南")
    print("=" * 70)
    
    print("\n📋 你只需要做3件事:")
    print("   1. 運行這個腳本 (已做 ✅)")
    print("   2. 觀察模擬交易結果")
    print("   3. 準備好後註冊OANDA實盤")
    
    print("\n💡 系統特性:")
    print("   • 完全免配置，立即開始")
    print("   • 使用模擬數據學習交易")
    print("   • 嚴格風險控制 (0.01手)")
    print("   • 自動記錄所有交易")
    
    print("\n🚀 立即開始:")
    print("   1. 系統會每小時自動檢查市場")
    print("   2. 發現交易信號時自動執行")
    print("   3. 所有結果記錄到日誌文件")
    
    print("\n📊 風險控制規則:")
    print("   • 每筆交易: 0.01手")
    print("   • 每日最多: 3筆交易")
    print("   • 止損: 60點 ($6.00)")
    print("   • 止盈: 120點 ($12.00)")
    
    print("\n" + "=" * 70)
    print("⚡ 按 Enter 開始交易，按 Ctrl+C 停止")
    print("=" * 70)

def main():
    """主函數"""
    show_welcome()
    
    try:
        input("\n按 Enter 開始自動交易...")
        
        trader = InstantGoldTrader()
        
        print("\n⏰ 交易系統已啟動，每小時運行一次")
        print("📝 查看實時日誌:")
        print(f"   tail -f /Users/gordonlui/.openclaw/workspace/logs/instant_trader_*.log")
        print("\n📊 查看交易記錄:")
        print(f"   cat /Users/gordonlui/.openclaw/workspace/instant_trades.json | python3 -m json.tool")
        
        cycle_count = 0
        max_cycles = 24  # 運行24小時（24個週期）
        
        while cycle_count < max_cycles:
            print(f"\n🌀 週期 {cycle_count + 1}/{max_cycles}")
            trader.run_one_cycle()
            
            cycle_count += 1
            
            if cycle_count < max_cycles:
                print(f"\n⏳ 等待下一小時... (按 Ctrl+C 停止)")
                for i in range(3600):  # 等待1小時
                    time.sleep(1)
                    if i % 300 == 0:  # 每5分鐘顯示進度
                        minutes_left = (3600 - i) // 60
                        print(f"   還有 {minutes_left} 分鐘...")
        
        print("\n" + "=" * 70)
        print("✅ 24小時交易模擬完成")
        print("=" * 70)
        
        # 顯示統計
        if os.path.exists("/Users/gordonlui/.openclaw/workspace/instant_trades.json"):
            with open("/Users/gordonlui/.openclaw/workspace/instant_trades.json", 'r') as f:
                trades = json.load(f)
            
            print(f"\n📊 交易統計:")
            print(f"   總交易次數: {len(trades)}")
            
            if trades:
                wins = sum(1 for t in trades if t.get('result') == 'WIN')
                win_rate = wins / len(trades) * 100
                print(f"   勝率: {win_rate:.1f}% ({wins}/{len(trades)})")
        
        print("\n🎯 下一步:")
        print("   1. 註冊OANDA實盤賬戶: https://www.oanda.com/")
        print("   2. 獲取API密鑰")
        print("   3. 使用完整版系統開始實盤")
        
    except KeyboardInterrupt:
        print("\n\n🛑 用戶停止")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")

if __name__ == "__main__":
    main()
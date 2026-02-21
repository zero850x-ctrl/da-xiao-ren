#!/usr/bin/env python3
"""
黃金自動交易系統 - 第二部分
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import os
from typing import Dict, List, Optional, Tuple

class GoldAutoTraderComplete:
    def __init__(self):
        """完整的黃金自動交易系統"""
        self.symbol = "XAUUSD"
        self.max_lot_size = 0.01
        self.account_balance = 1000.0
        
        # 交易記錄
        self.trades = []
        self.performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0
        }
        
        # 策略配置
        self.strategies = {
            'trend_following': True,
            'mean_reversion': True,
            'breakout': True,
            'support_resistance': True
        }
        
    def generate_test_data(self, days: int = 30) -> pd.DataFrame:
        """生成測試數據"""
        print(f"📊 生成 {days} 天測試數據...")
        
        # 創建時間序列（每小時數據）
        periods = days * 24
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='H')
        
        # 模擬黃金價格（帶趨勢、季節性、波動）
        np.random.seed(42)
        
        # 基礎趨勢（緩慢上升）
        base_trend = np.linspace(1800, 2200, periods)
        
        # 每日波動
        daily_cycle = 30 * np.sin(np.linspace(0, days*2*np.pi, periods))
        
        # 隨機波動
        random_noise = 20 * np.random.randn(periods)
        
        # 合成價格
        prices = base_trend + daily_cycle + random_noise
        
        # 生成OHLC數據
        data = []
        for i in range(periods):
            base = prices[i]
            high = base + abs(np.random.randn() * 8)
            low = base - abs(np.random.randn() * 8)
            close = base + np.random.randn() * 4
            
            # 確保合理的價格關係
            if high < low:
                high, low = low, high
            close = max(low, min(high, close))
            
            data.append({
                'timestamp': dates[i],
                'open': base,
                'high': high,
                'low': low,
                'close': close,
                'volume': np.random.randint(500, 2000)
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        print(f"   數據點: {len(df)}")
        print(f"   價格範圍: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
        
        return df
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算所有技術指標"""
        print("📈 計算技術指標...")
        
        # 移動平均線
        df['SMA_10'] = df['close'].rolling(10).mean()
        df['SMA_20'] = df['close'].rolling(20).mean()
        df['SMA_50'] = df['close'].rolling(50).mean()
        df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # RSI
        df['RSI'] = self.calculate_rsi(df['close'], 14)
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']
        
        # 布林帶
        df['BB_middle'] = df['close'].rolling(20).mean()
        bb_std = df['close'].rolling(20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / df['BB_middle']
        
        # ATR（波動率）
        df['ATR'] = self.calculate_atr(df, 14)
        
        # 支撐阻力位（簡單版本）
        df['resistance'] = df['high'].rolling(20).max()
        df['support'] = df['low'].rolling(20).min()
        
        print("✅ 指標計算完成")
        return df
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """計算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """計算ATR"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()
    
    def generate_trading_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """生成交易信號"""
        print("🔍 生成交易信號...")
        
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['close']
        signals['signal'] = 'HOLD'
        signals['strength'] = 0.0
        signals['reason'] = ''
        
        for i in range(50, len(df)):
            current = df.iloc[i]
            prev = df.iloc[i-1]
            
            signal_strength = 0
            reasons = []
            
            # 策略1: 趨勢跟隨（移動平均線交叉）
            if self.strategies['trend_following']:
                # 黃金交叉
                if (prev['SMA_20'] <= prev['SMA_50'] and 
                    current['SMA_20'] > current['SMA_50']):
                    signal_strength += 0.3
                    reasons.append("SMA黃金交叉")
                
                # 死亡交叉
                if (prev['SMA_20'] >= prev['SMA_50'] and 
                    current['SMA_20'] < current['SMA_50']):
                    signal_strength -= 0.3
                    reasons.append("SMA死亡交叉")
            
            # 策略2: 均值回歸（RSI超買超賣）
            if self.strategies['mean_reversion']:
                rsi = current['RSI']
                if pd.notna(rsi):
                    if rsi < 30:
                        signal_strength += 0.4
                        reasons.append(f"RSI超賣({rsi:.1f})")
                    elif rsi > 70:
                        signal_strength -= 0.4
                        reasons.append(f"RSI超買({rsi:.1f})")
            
            # 策略3: 布林帶回歸
            if self.strategies['mean_reversion']:
                price = current['close']
                if price <= current['BB_lower']:
                    signal_strength += 0.3
                    reasons.append("觸及布林帶下軌")
                elif price >= current['BB_upper']:
                    signal_strength -= 0.3
                    reasons.append("觸及布林帶上軌")
            
            # 策略4: 支撐阻力突破
            if self.strategies['support_resistance']:
                if current['close'] > current['resistance']:
                    signal_strength += 0.2
                    reasons.append("突破阻力位")
                elif current['close'] < current['support']:
                    signal_strength -= 0.2
                    reasons.append("跌破支撐位")
            
            # 確定最終信號
            if signal_strength > 0.5:
                signals.at[signals.index[i], 'signal'] = 'BUY'
                signals.at[signals.index[i], 'strength'] = signal_strength
                signals.at[signals.index[i], 'reason'] = " | ".join(reasons)
            elif signal_strength < -0.5:
                signals.at[signals.index[i], 'signal'] = 'SELL'
                signals.at[signals.index[i], 'strength'] = abs(signal_strength)
                signals.at[signals.index[i], 'reason'] = " | ".join(reasons)
        
        print(f"✅ 生成 {len(signals[signals['signal'] != 'HOLD'])} 個交易信號")
        return signals
    
    def simulate_trading(self, df: pd.DataFrame, signals: pd.DataFrame):
        """模擬交易執行"""
        print("\n💼 開始模擬交易...")
        
        position = None
        trade_results = []
        
        for i in range(len(signals)):
            current_time = signals.index[i]
            current_signal = signals.iloc[i]
            current_price = current_signal['price']
            
            # 如果有持倉，檢查是否達到止損止盈
            if position:
                # 計算盈虧
                if position['type'] == 'BUY':
                    profit = (current_price - position['entry_price']) * position['lot_size'] * 100
                else:  # SELL
                    profit = (position['entry_price'] - current_price) * position['lot_size'] * 100
                
                # 檢查止損止盈
                stop_loss = position['entry_price'] * (1 - 0.005) if position['type'] == 'BUY' else position['entry_price'] * (1 + 0.005)
                take_profit = position['entry_price'] * (1 + 0.01) if position['type'] == 'BUY' else position['entry_price'] * (1 - 0.01)
                
                exit_reason = None
                if (position['type'] == 'BUY' and current_price <= stop_loss) or \
                   (position['type'] == 'SELL' and current_price >= stop_loss):
                    exit_reason = 'STOP_LOSS'
                elif (position['type'] == 'BUY' and current_price >= take_profit) or \
                     (position['type'] == 'SELL' and current_price <= take_profit):
                    exit_reason = 'TAKE_PROFIT'
                
                if exit_reason:
                    # 平倉
                    trade = {
                        'entry_time': position['entry_time'],
                        'exit_time': current_time,
                        'type': position['type'],
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'lot_size': position['lot_size'],
                        'profit': profit,
                        'exit_reason': exit_reason,
                        'holding_period': (current_time - position['entry_time']).total_seconds() / 3600
                    }
                    trade_results.append(trade)
                    position = None
            
            # 如果沒有持倉，檢查新信號
            if not position and current_signal['signal'] != 'HOLD':
                # 開倉
                position = {
                    'entry_time': current_time,
                    'type': current_signal['signal'],
                    'entry_price': current_price,
                    'lot_size': self.max_lot_size,
                    'signal_strength': current_signal['strength'],
                    'reason': current_signal['reason']
                }
        
        # 如果有未平倉位，在最後時間平倉
        if position:
            last_price = signals.iloc[-1]['price']
            if position['type'] == 'BUY':
                profit = (last_price - position['entry_price']) * position['lot_size'] * 100
            else:
                profit = (position['entry_price'] - last_price) * position['lot_size'] * 100
            
            trade = {
                'entry_time': position['entry_time'],
                'exit_time': signals.index[-1],
                'type': position['type'],
                'entry_price': position['entry_price'],
                'exit_price': last_price,
                'lot_size': position['lot_size'],
                'profit': profit,
                'exit_reason': 'END_OF_PERIOD',
                'holding_period': (signals.index[-1] - position['entry_time']).total_seconds() / 3600
            }
            trade_results.append(trade)
        
        return trade_results
    
    def analyze_performance(self, trades: List[Dict]):
        """分析交易績效"""
        print("\n📊 交易績效分析:")
        
        if not trades:
            print("   沒有交易記錄")
            return
        
        # 基本統計
        total_trades = len(trades)
        winning_trades = [t for t in trades if t['profit'] > 0]
        losing_trades = [t for t in trades if t['profit'] <= 0]
        
        total_profit = sum(t['profit'] for t in trades)
        total_win = sum(t['profit'] for t in winning_trades)
        total_loss = abs(sum(t['profit'] for t in losing_trades))
        
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        profit_factor = total_win / total_loss if total_loss > 0 else float('inf')
        
        # 最大回撤
        cumulative_profits = np.cumsum([t['profit'] for t in trades])
        running_max = np.maximum.accumulate(cumulative_profits)
        drawdowns = running_max - cumulative_profits
        max_drawdown = drawdowns.max() if len(drawdowns) > 0 else 0
        
        # 平均持倉時間
        avg_holding = np.mean([t['holding_period'] for t in trades])
        
        print(f"   總交易次數: {total_trades}")
        print(f"   盈利交易: {len(winning_trades)} ({win_rate:.1f}%)")
        print(f"   虧損交易: {len(losing_trades)} ({100-win_rate:.1f}%)")
        print(f"   總盈利: ${total_profit:.2f}")
        print(f"   盈利因子: {profit_factor:.2f}")
        print(f"   最大回撤: ${max_drawdown:.2f}")
        print(f"   平均持倉時間: {avg_holding:.1f}小時")
        
        # 詳細交易記錄
        print(f"\n📝 交易記錄 (前10筆):")
        for i, trade in enumerate(trades[:10]):
            profit_color = "🟢" if trade['profit'] > 0 else "🔴"
            print(f"   {i+1}. {trade['type']} @ ${trade['entry_price']:.2f}")
            print(f"      平倉: ${trade['exit_price']:.2f} ({trade['holding_period']:.1f}小時)")
            print(f"      盈虧: {profit_color} ${trade['profit']:.2f}")
            print(f"      原因: {trade['exit_reason']}")
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'avg_holding_hours': avg_holding
        }
    
    def run_complete_simulation(self, days: int = 30):
        """運行完整模擬"""
        print("=" * 60)
        print("🏆 黃金自動交易系統 - 完整模擬")
        print("=" * 60)
        
        # 1. 生成數據
        df = self.generate_test_data(days)
        
        # 2. 計算指標
        df = self.calculate_all_indicators(df)
        
        # 3. 生成信號
        signals = self.generate_trading_signals(df)
        
        # 4. 模擬交易
        trades = self.simulate_trading(df, signals)
        
        # 5. 分析績效
        performance = self.analyze_performance(trades)
        
        # 6. 生成報告
        self.generate_report(performance, trades)
        
        print("\n" + "=" * 60)
        print("✅ 模擬完成")
        print("=" * 60)
    
    def generate_report(self, performance: Dict, trades: List[Dict]):
        """生成交易報告"""
        report = f"""
黃金自動交易系統報告
生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
模擬天數: 30天
最大手數: {self.max_lot_size}手
賬戶資金: ${self.account_balance:.2f}

📊 績效摘要:
   總交易次數: {performance['total_trades']}
   勝率: {performance['win_rate']:.1f}%
   總盈利: ${performance['total_profit']:.2f}
   盈利因子: {performance['profit_factor']:.2f}
   最大回撤: ${performance['max_d
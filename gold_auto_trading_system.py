#!/usr/bin/env python3
"""
黃金自動交易系統
基於股票交易策略，自動進行買賣
最大每注: 0.01手
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import os
import warnings
warnings.filterwarnings('ignore')

class GoldAutoTradingSystem:
    def __init__(self, initial_balance: float = 1000.0):
        """
        初始化黃金自動交易系統
        
        :param initial_balance: 初始資金
        """
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.max_lot_size = 0.01  # 最大每注0.01手
        
        # 交易記錄
        self.trades = []
        self.positions = []
        
        # 策略配置
        self.strategy_config = {
            'trend_following': {
                'enabled': True,
                'weight': 0.3,
                'sma_short': 20,
                'sma_long': 50,
                'rsi_period': 14
            },
            'mean_reversion': {
                'enabled': True,
                'weight': 0.4,
                'bollinger_period': 20,
                'bollinger_std': 2,
                'rsi_oversold': 30,
                'rsi_overbought': 70
            },
            'breakout': {
                'enabled': True,
                'weight': 0.3,
                'lookback_period': 20
            }
        }
        
        # 風險管理
        self.risk_config = {
            'stop_loss_pips': 50,      # 50點止損
            'take_profit_pips': 100,   # 100點止盈
            'max_risk_per_trade': 0.02,  # 2%每筆
            'max_daily_trades': 3,
            'cooldown_after_loss': 2
        }
        
        print("=" * 60)
        print("🏆 黃金自動交易系統 v1.0")
        print("=" * 60)
        print(f"   初始資金: ${self.initial_balance:.2f}")
        print(f"   最大手數: {self.max_lot_size}手")
        print(f"   啟用策略: {sum(1 for s in self.strategy_config.values() if s['enabled'])}個")
        print(f"   風險管理: 止損{self.risk_config['stop_loss_pips']}點/止盈{self.risk_config['take_profit_pips']}點")
    
    def generate_market_data(self, periods: int = 720) -> pd.DataFrame:
        """
        生成模擬市場數據（每小時數據）
        
        :param periods: 數據點數量（30天×24小時=720）
        :return: OHLCV DataFrame
        """
        print(f"\n📊 生成市場數據 ({periods}小時)...")
        
        # 創建時間序列
        end_time = datetime.now()
        dates = pd.date_range(end=end_time, periods=periods, freq='H')
        
        # 模擬黃金價格走勢
        np.random.seed(42)  # 固定隨機種子以便重現
        
        # 1. 長期趨勢（緩慢上升）
        base_trend = np.linspace(1800, 2200, periods)
        
        # 2. 中期波動（幾天的周期）
        medium_cycle = 40 * np.sin(np.linspace(0, 15*np.pi, periods))
        
        # 3. 短期波動（幾小時的周期）
        short_cycle = 15 * np.sin(np.linspace(0, 60*np.pi, periods))
        
        # 4. 隨機噪聲
        random_noise = 10 * np.random.randn(periods)
        
        # 合成價格
        base_price = base_trend + medium_cycle + short_cycle + random_noise
        
        # 生成OHLC數據
        data = []
        for i in range(periods):
            base = base_price[i]
            
            # 生成合理的OHLC
            high = base + abs(np.random.randn() * 8)
            low = base - abs(np.random.randn() * 8)
            close = base + np.random.randn() * 4
            
            # 確保價格關係合理
            if high < low:
                high, low = low, high
            close = np.clip(close, low, high)
            
            # 開盤價（接近前收盤）
            if i == 0:
                open_price = base
            else:
                open_price = data[i-1]['close'] + np.random.randn() * 2
            
            data.append({
                'timestamp': dates[i],
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': np.random.randint(800, 2500)
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        print(f"   時間範圍: {df.index[0]} 到 {df.index[-1]}")
        print(f"   價格範圍: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
        print(f"   最新收盤價: ${df['close'].iloc[-1]:.2f}")
        
        return df
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算技術指標"""
        print("\n📈 計算技術指標...")
        
        # 移動平均線
        df['SMA_10'] = df['close'].rolling(window=10).mean()
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # RSI
        df['RSI'] = self._calculate_rsi(df['close'], 14)
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']
        
        # 布林帶
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / df['BB_middle']
        
        # ATR（平均真實波幅）
        df['ATR'] = self._calculate_atr(df, 14)
        
        # 支撐阻力
        df['resistance_20'] = df['high'].rolling(window=20).max()
        df['support_20'] = df['low'].rolling(window=20).min()
        
        print("✅ 技術指標計算完成")
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """計算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """計算ATR"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=period).mean()
    
    def generate_trading_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """生成交易信號"""
        print("\n🔍 生成交易信號...")
        
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['close']
        signals['signal'] = 'HOLD'
        signals['strength'] = 0.0
        signals['reason'] = ''
        
        for i in range(50, len(df)):  # 從第50個數據點開始（確保有足夠歷史數據）
            current = df.iloc[i]
            prev = df.iloc[i-1]
            
            signal_score = 0.0
            reasons = []
            
            # 策略1: 趨勢跟隨
            if self.strategy_config['trend_following']['enabled']:
                weight = self.strategy_config['trend_following']['weight']
                
                # SMA黃金交叉
                if prev['SMA_20'] <= prev['SMA_50'] and current['SMA_20'] > current['SMA_50']:
                    signal_score += 0.8 * weight
                    reasons.append("SMA黃金交叉")
                
                # SMA死亡交叉
                if prev['SMA_20'] >= prev['SMA_50'] and current['SMA_20'] < current['SMA_50']:
                    signal_score -= 0.8 * weight
                    reasons.append("SMA死亡交叉")
                
                # MACD信號
                if current['MACD'] > current['MACD_signal'] and prev['MACD'] <= prev['MACD_signal']:
                    signal_score += 0.6 * weight
                    reasons.append("MACD金叉")
                elif current['MACD'] < current['MACD_signal'] and prev['MACD'] >= prev['MACD_signal']:
                    signal_score -= 0.6 * weight
                    reasons.append("MACD死叉")
            
            # 策略2: 均值回歸
            if self.strategy_config['mean_reversion']['enabled']:
                weight = self.strategy_config['mean_reversion']['weight']
                
                # RSI超買超賣
                rsi = current['RSI']
                if pd.notna(rsi):
                    if rsi < 30:
                        signal_score += 0.7 * weight
                        reasons.append(f"RSI超賣({rsi:.1f})")
                    elif rsi > 70:
                        signal_score -= 0.7 * weight
                        reasons.append(f"RSI超買({rsi:.1f})")
                
                # 布林帶回歸
                price = current['close']
                if price <= current['BB_lower']:
                    signal_score += 0.6 * weight
                    reasons.append("觸及布林帶下軌")
                elif price >= current['BB_upper']:
                    signal_score -= 0.6 * weight
                    reasons.append("觸及布林帶上軌")
            
            # 策略3: 突破交易
            if self.strategy_config['breakout']['enabled']:
                weight = self.strategy_config['breakout']['weight']
                
                # 阻力突破
                if current['close'] > current['resistance_20']:
                    signal_score += 0.5 * weight
                    reasons.append("突破阻力位")
                
                # 支撐跌破
                if current['close'] < current['support_20']:
                    signal_score -= 0.5 * weight
                    reasons.append("跌破支撐位")
            
            # 確定最終信號
            if signal_score > 0.5:
                signals.at[signals.index[i], 'signal'] = 'BUY'
                signals.at[signals.index[i], 'strength'] = signal_score
                signals.at[signals.index[i], 'reason'] = " | ".join(reasons)
            elif signal_score < -0.5:
                signals.at[signals.index[i], 'signal'] = 'SELL'
                signals.at[signals.index[i], 'strength'] = abs(signal_score)
                signals.at[signals.index[i], 'reason'] = " | ".join(reasons)
        
        # 統計信號
        buy_signals = len(signals[signals['signal'] == 'BUY'])
        sell_signals = len(signals[signals['signal'] == 'SELL'])
        
        print(f"   買入信號: {buy_signals}個")
        print(f"   賣出信號: {sell_signals}個")
        print(f"   持倉觀望: {len(signals) - buy_signals - sell_signals}個")
        
        return signals
    
    def simulate_trading(self, df: pd.DataFrame, signals: pd.DataFrame):
        """模擬交易執行"""
        print("\n💼 模擬交易執行...")
        
        position = None
        trades = []
        consecutive_losses = 0
        
        for i in range(len(signals)):
            current_time = signals.index[i]
            current_signal = signals.iloc[i]
            current_price = current_signal['price']
            
            # 檢查冷卻期
            if consecutive_losses >= self.risk_config['cooldown_after_loss']:
                if position:
                    # 平倉並進入冷卻
                    self._close_position(position, current_price, 'COOLDOWN', trades)
                    position = None
                continue
            
            # 如果有持倉，檢查止損止盈
            if position:
                profit_pips = self._calculate_profit_pips(position, current_price)
                
                # 檢查止損
                if profit_pips <= -self.risk_config['stop_loss_pips']:
                    self._close_position(position, current_price, 'STOP_LOSS', trades)
                    consecutive_losses += 1
                    position = None
                
                # 檢查止盈
                elif profit_pips >= self.risk_config['take_profit_pips']:
                    self._close_position(position, current_price, 'TAKE_PROFIT', trades)
                    consecutive_losses = 0
                    position = None
            
            # 如果沒有持倉，檢查新信號
            if not position and current_signal['signal'] != 'HOLD':
                # 計算倉位大小（考慮0.01手限制）
                lot_size = self._calculate_position_size(current_signal['strength'])
                
                # 開倉
                position = {
                    'entry_time': current_time,
                    'type': current_signal['signal'],
                    'entry_price': current_price,
                    'lot_size': lot_size,
                    'signal_strength': current_signal['strength'],
                    'reason': current_signal['reason']
                }
        
        # 如果有未平倉位，在最後時間平倉
        if position:
            last_price = signals.iloc[-1]['price']
            self._close_position(position, last_price, 'END_OF_PERIOD', trades)
        
        return trades
    
    def _calculate_position_size(self, signal_strength: float) -> float:
        """計算倉位大小（考慮0.01手限制和信號強度）"""
        # 基礎手數（0.01手）
        base_lot = self.max_lot_size
        
        # 根據信號強度調整
        adjusted_lot = base_lot * signal_strength
        
        # 確保在合理範圍內
        adjusted_lot = max(0.01, min(self.max_lot_size, adjusted_lot))
        
        return round(adjusted_lot, 2)
    
    def _calculate_profit_pips(self, position: Dict, current_price: float) -> float:
        """計算盈利點數"""
        if position['type'] == 'BUY':
            profit = (current_price - position['entry_price']) * 10  # 黃金1點=0.10
        else:  # SELL
            profit = (position['entry_price'] - current_price) * 10
        
        return profit
    
    def _close_position(self, position: Dict, exit_price: float, exit_reason: str, trades: List):
        """平倉並記錄交易"""
        profit_pips = self._calculate_profit_pips(position, exit_price)
        profit_dollars = profit_pips * position['lot_size'] * 0.1  # 0.01手每點$0.01
        
        # 更新資金
        self.balance += profit_dollars
        
        # 記錄交易
        trade = {
            'id': len(trades) + 1,
            'entry_time': position['entry_time'],
            'exit_time': datetime.now(),
            'type': position['type'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'lot_size': position['lot_size'],
            'profit_pips': profit_pips,
            'profit_dollars': profit_dollars,
            'exit_reason': exit_reason,
            'holding_hours': (datetime.now() - position['entry_time']).total_seconds() / 3600,
            'signal_strength': position['signal_strength'],
            'reason': position['reason']
        }
        
        trades.append(trade)
        
        # 打印交易結果
        profit_color = "🟢" if profit_dollars > 0 else "🔴"
        print(f"   {trade['id']}. {trade['type']} @ ${trade['entry_price']:.2f}")
        print(f"      平倉: ${trade['exit_price']:.2f} ({trade['holding_hours']:.1f}小時)")
        print(f"
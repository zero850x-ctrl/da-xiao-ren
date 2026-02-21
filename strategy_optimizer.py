#!/usr/bin/env python3
"""
交易策略參數優化器
基於歷史數據優化0.01手黃金交易策略
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import itertools
import json
import warnings
warnings.filterwarnings('ignore')

class StrategyOptimizer:
    def __init__(self):
        """初始化優化器"""
        self.results = []
        self.best_params = {}
        
    def generate_test_data(self, days=90):
        """生成測試數據（90天）"""
        print(f"📊 生成 {days} 天測試數據...")
        
        periods = days * 24  # 每小時數據
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='h')
        
        # 更真實的價格模擬
        np.random.seed(42)
        
        # 多重周期波動
        base_trend = np.linspace(1800, 2200, periods)
        monthly_cycle = 50 * np.sin(np.linspace(0, 3*2*np.pi, periods))
        weekly_cycle = 30 * np.sin(np.linspace(0, 13*2*np.pi, periods))
        daily_cycle = 15 * np.sin(np.linspace(0, 90*2*np.pi, periods))
        noise = 10 * np.random.randn(periods)
        
        prices = base_trend + monthly_cycle + weekly_cycle + daily_cycle + noise
        
        # 生成OHLC數據
        data = []
        for i in range(periods):
            base = prices[i]
            volatility = 0.002 + 0.001 * np.sin(i/100)  # 動態波動率
            
            high = base * (1 + abs(np.random.normal(0, volatility)))
            low = base * (1 - abs(np.random.normal(0, volatility)))
            close = base * (1 + np.random.normal(0, volatility/2))
            
            if high < low:
                high, low = low, high
            close = np.clip(close, low, high)
            
            if i == 0:
                open_price = base
            else:
                open_price = data[i-1]['close'] * (1 + np.random.normal(0, volatility/3))
            
            data.append({
                'timestamp': dates[i],
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': np.random.randint(500, 3000)
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        print(f"✅ 生成 {len(df)} 小時數據")
        print(f"   價格範圍: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
        
        return df
    
    def calculate_indicators(self, df, params):
        """計算技術指標"""
        # 移動平均線
        sma_short = params.get('sma_short', 20)
        sma_long = params.get('sma_long', 50)
        
        df['SMA_short'] = df['close'].rolling(sma_short).mean()
        df['SMA_long'] = df['close'].rolling(sma_long).mean()
        
        # RSI
        rsi_period = params.get('rsi_period', 14)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(rsi_period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 布林帶
        bb_period = params.get('bb_period', 20)
        bb_std = params.get('bb_std', 2)
        df['BB_middle'] = df['close'].rolling(bb_period).mean()
        bb_std_series = df['close'].rolling(bb_period).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std_series * bb_std)
        df['BB_lower'] = df['BB_middle'] - (bb_std_series * bb_std)
        
        # MACD
        ema_short = params.get('ema_short', 12)
        ema_long = params.get('ema_long', 26)
        signal_period = params.get('signal_period', 9)
        
        df['EMA_short'] = df['close'].ewm(span=ema_short, adjust=False).mean()
        df['EMA_long'] = df['close'].ewm(span=ema_long, adjust=False).mean()
        df['MACD'] = df['EMA_short'] - df['EMA_long']
        df['MACD_signal'] = df['MACD'].ewm(span=signal_period, adjust=False).mean()
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']
        
        return df
    
    def generate_signals(self, df, params):
        """生成交易信號"""
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['close']
        signals['signal'] = 'HOLD'
        signals['strength'] = 0.0
        
        # 參數
        rsi_oversold = params.get('rsi_oversold', 30)
        rsi_overbought = params.get('rsi_overbought', 70)
        bb_threshold = params.get('bb_threshold', 0)  # 0=觸及，1=接近
        
        for i in range(50, len(df)):
            current = df.iloc[i]
            prev = df.iloc[i-1]
            
            score = 0.0
            
            # 1. SMA交叉
            if params.get('use_sma', True):
                if prev['SMA_short'] <= prev['SMA_long'] and current['SMA_short'] > current['SMA_long']:
                    score += params.get('sma_weight', 0.3)
                elif prev['SMA_short'] >= prev['SMA_long'] and current['SMA_short'] < current['SMA_long']:
                    score -= params.get('sma_weight', 0.3)
            
            # 2. RSI
            if params.get('use_rsi', True):
                rsi = current['RSI']
                if pd.notna(rsi):
                    if rsi < rsi_oversold:
                        score += params.get('rsi_weight', 0.4)
                    elif rsi > rsi_overbought:
                        score -= params.get('rsi_weight', 0.4)
            
            # 3. 布林帶
            if params.get('use_bb', True):
                price = current['close']
                bb_lower = current['BB_lower']
                bb_upper = current['BB_upper']
                
                if price <= bb_lower * (1 + bb_threshold/100):
                    score += params.get('bb_weight', 0.2)
                elif price >= bb_upper * (1 - bb_threshold/100):
                    score -= params.get('bb_weight', 0.2)
            
            # 4. MACD
            if params.get('use_macd', False):
                if current['MACD'] > current['MACD_signal'] and prev['MACD'] <= prev['MACD_signal']:
                    score += params.get('macd_weight', 0.1)
                elif current['MACD'] < current['MACD_signal'] and prev['MACD'] >= prev['MACD_signal']:
                    score -= params.get('macd_weight', 0.1)
            
            # 確定信號
            threshold = params.get('signal_threshold', 0.5)
            if score >= threshold:
                signals.at[signals.index[i], 'signal'] = 'BUY'
                signals.at[signals.index[i], 'strength'] = score
            elif score <= -threshold:
                signals.at[signals.index[i], 'signal'] = 'SELL'
                signals.at[signals.index[i], 'strength'] = abs(score)
        
        return signals
    
    def simulate_trading(self, signals, params):
        """模擬交易"""
        initial_balance = 1000.0
        balance = initial_balance
        max_lot_size = 0.01
        
        trades = []
        position = None
        
        stop_loss_pips = params.get('stop_loss_pips', 50)
        take_profit_pips = params.get('take_profit_pips', 100)
        max_trades = params.get('max_trades', 100)
        
        for i in range(len(signals)):
            if len(trades) >= max_trades:
                break
                
            current_time = signals.index[i]
            current_signal = signals.iloc[i]
            current_price = current_signal['price']
            
            # 檢查持倉
            if position:
                # 計算持倉時間
                holding_hours = (current_time - position['entry_time']).total_seconds() / 3600
                max_holding = params.get('max_holding_hours', 72)
                
                if holding_hours >= max_holding:
                    # 時間止損
                    self._close_position(position, current_price, 'TIME_LIMIT', trades, balance)
                    position = None
                    continue
                
                # 計算盈虧
                profit_pips = self._calculate_profit_pips(position, current_price)
                
                # 檢查止損
                if profit_pips <= -stop_loss_pips:
                    self._close_position(position, current_price, 'STOP_LOSS', trades, balance)
                    position = None
                    continue
                
                # 檢查止盈
                if profit_pips >= take_profit_pips:
                    self._close_position(position, current_price, 'TAKE_PROFIT', trades, balance)
                    position = None
                    continue
            
            # 開新倉
            if not position and current_signal['signal'] != 'HOLD':
                # 計算手數（考慮信號強度）
                base_lot = max_lot_size
                strength = current_signal['strength']
                lot_size = min(base_lot * strength * 2, max_lot_size)
                lot_size = max(0.01, lot_size)  # 最小0.01手
                
                position = {
                    'entry_time': current_time,
                    'type': current_signal['signal'],
                    'entry_price': current_price,
                    'lot_size': lot_size,
                    'signal_strength': strength
                }
        
        # 清理未平倉位
        if position:
            last_price = signals.iloc[-1]['price']
            self._close_position(position, last_price, 'END_OF_PERIOD', trades, balance)
        
        return trades, balance
    
    def _calculate_profit_pips(self, position, current_price):
        """計算盈利點數"""
        if position['type'] == 'BUY':
            return (current_price - position['entry_price']) * 10
        else:
            return (position['entry_price'] - current_price) * 10
    
    def _close_position(self, position, exit_price, reason, trades, balance):
        """平倉"""
        profit_pips = self._calculate_profit_pips(position, exit_price)
        profit_amount = profit_pips * position['lot_size'] * 0.1
        
        trade = {
            'entry_time': position['entry_time'],
            'exit_time': datetime.now(),
            'type': position['type'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'lot_size': position['lot_size'],
            'profit_pips': profit_pips,
            'profit_amount': profit_amount,
            'exit_reason': reason,
            'signal_strength': position['signal_strength']
        }
        
        trades.append(trade)
        balance += profit_amount
        
        return balance
    
    def evaluate_strategy(self, trades, initial_balance, final_balance):
        """評估策略表現"""
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_profit': 0,
                'profit_percentage': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0
            }
        
        total_trades = len(trades)
        winning_trades = [t for t in trades if t['profit_amount'] > 0]
        losing_trades = [t for t in trades if t['profit_amount'] <= 0]
        
        total_profit = sum(t['profit_amount'] for t in trades)
        total_win = sum(t['profit_amount'] for t in winning_trades)
        total_loss = abs(sum(t['profit_amount'] for t in losing_trades))
        
        win_rate = len(winning_trades) / total_trades * 100
        profit_percentage = (total_profit / initial_balance) * 100
        profit_factor = total_win / total_loss if total_loss > 0 else float('inf')
        
        # 計算最大回撤
        cumulative = np.cumsum([t['profit_amount'] for t in trades])
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = running_max - cumulative
        max_drawdown = drawdowns.max() if len(drawdowns) > 0 else 0
        
        # 計算夏普比率（簡化）
        returns = [t['profit_amount'] / initial_balance for t in trades]
        if len(returns) > 1:
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        else:
            sharpe = 0
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'profit_percentage': profit_percentage,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe
        }
    
    def optimize_parameters(self):
        """優化參數"""
        print("\n" + "=" * 70)
        print("🔧 開始參數優化")
        print("=" * 70)
        
        # 生成測試數據
        df = self.generate_test_data(90)
        
        # 定義參數搜索空間
        param_grid = {
            'sma_short': [10, 15, 20, 25],
            'sma_long': [40, 50, 60],
            'rsi_period': [10, 14, 20],
            'rsi_oversold': [25, 30, 35],
            'rsi_overbought': [65, 70, 75],
            'bb_period': [15, 20, 25],
            'bb_std': [1.5, 2.0, 2.5],
            'stop_loss_pips': [40, 50, 60],
            'take_profit_pips': [80, 100, 120],
            'signal_threshold': [0.4, 0.5, 0.6]
        }
        
        # 生成參數組合（限制數量）
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        # 隨機採樣參數組合
        np.random.seed(42)
        n_combinations = 50  # 測試50種組合
        
        best_score = -float('inf')
        best_params = {}
        best_performance = {}
        
        for combo_idx in range(n_combinations):
            # 隨機選擇參數
            params = {}
            for name, values in param_grid.items():
                params[name] = np.random.choice(values)
            
            # 添加固定參數
            params.update({
                'use_sma': True,
                'use_rsi': True,
                'use_bb': True,
                'use_macd': False,
                'sma_weight': 0.3,
                'rsi_weight': 0.4,
                'bb_weight': 0.2,
                'macd_weight': 0.1,
                'max_trades': 50,
                'max_holding_hours': 72
            })
            
            print(f"\n🔍 測試組合 #{combo_idx+1}/{n_combinations}")
            print(f"   參數: SMA{params['sma_short']}/{params['sma_long']}, "
                  f"RSI{params['rsi_period']}({params['rsi_oversold']}/{params['rsi_overbought']}), "
                  f"BB{params['bb_period']}x{params['bb_std']}")
            
            # 計算指標
            df_with_indicators = self.calculate_indicators(df.copy(), params)
            
            # 生成信號
            signals = self.generate_signals(df_with_indicators, params)
            
            # 模擬交易
            trades, final_balance = self.simulate_trading(signals, params)
            
            # 評估表現
            performance = self.evaluate_strategy(trades, 1000, final_balance)
            
            # 計算綜合評分
            score = self._calculate_score(performance)
            
            # 記錄結果
            result = {
                'params': params.copy(),
                'performance': performance,
                'score': score,
                'trades_count': len(trades)
            }
            
            self.results.append(result)
            
            print(f"   交易次數: {performance['total_trades']}")
            print(f"   勝率: {performance['win_rate']:.1f}%")
            print(f"   盈利: ${performance['total_profit']:.2f} ({performance['profit_percentage']:.2f}%)")
            print(f"
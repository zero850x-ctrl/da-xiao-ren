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
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class GoldAutoTrader:
    def __init__(self, config_path: str = "gold_trader_config.json"):
        """
        初始化黃金自動交易系統
        
        :param config_path: 配置文件路徑
        """
        self.config_path = config_path
        self.config = self.load_config()
        
        # 交易參數
        self.symbol = "XAUUSD"
        self.max_lot_size = 0.01  # 最大每注0.01手
        self.account_balance = self.config.get("account_balance", 1000.0)
        
        # 策略參數
        self.strategies = self.config.get("strategies", {})
        
        # 交易記錄
        self.trades_log = []
        self.performance_log = []
        
        # 狀態
        self.position_open = False
        self.current_position = None
        
        print("=" * 60)
        print("🏆 黃金自動交易系統初始化")
        print("=" * 60)
        print(f"   交易對: {self.symbol}")
        print(f"   最大手數: {self.max_lot_size}手")
        print(f"   賬戶資金: ${self.account_balance:.2f}")
        print(f"   啟用策略: {len(self.strategies)}個")
    
    def load_config(self) -> Dict:
        """加載配置文件"""
        default_config = {
            "account_balance": 1000.0,
            "max_lot_size": 0.01,
            "risk_per_trade": 0.002,  # 0.2%每筆
            "max_daily_loss": 0.01,   # 1%每日
            "strategies": {
                "trend_following": {
                    "enabled": True,
                    "timeframe": "H1",
                    "sma_short": 20,
                    "sma_long": 50,
                    "rsi_period": 14,
                    "rsi_oversold": 30,
                    "rsi_overbought": 70
                },
                "mean_reversion": {
                    "enabled": True,
                    "timeframe": "H4",
                    "bollinger_period": 20,
                    "bollinger_std": 2,
                    "rsi_period": 14
                },
                "breakout": {
                    "enabled": True,
                    "timeframe": "D1",
                    "support_resistance_lookback": 20
                }
            },
            "trading_hours": {
                "start": "00:00",
                "end": "23:59",
                "timezone": "Asia/Hong_Kong"
            },
            "risk_management": {
                "stop_loss_pips": 50,
                "take_profit_pips": 100,
                "max_trades_per_day": 3,
                "cooldown_after_loss": 2
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                print(f"✅ 已加載配置文件: {self.config_path}")
                return config
            else:
                print(f"⚠️  配置文件不存在，使用默認配置")
                return default_config
        except Exception as e:
            print(f"❌ 加載配置文件失敗: {e}")
            return default_config
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"✅ 配置已保存到: {self.config_path}")
        except Exception as e:
            print(f"❌ 保存配置失敗: {e}")
    
    def simulate_market_data(self, periods: int = 200) -> pd.DataFrame:
        """
        模擬市場數據（實際使用時替換為真實API）
        
        :param periods: 數據點數量
        :return: 包含OHLCV的DataFrame
        """
        print(f"\n📊 生成模擬市場數據...")
        
        # 創建時間序列
        end_time = datetime.now()
        start_time = end_time - timedelta(days=periods//24)
        
        dates = pd.date_range(start=start_time, end=end_time, periods=periods)
        
        # 模擬價格走勢（帶趨勢和波動）
        np.random.seed(42)
        
        # 基礎趨勢
        trend = np.linspace(1800, 2200, periods)
        
        # 季節性波動
        seasonal = 50 * np.sin(np.linspace(0, 10*np.pi, periods))
        
        # 隨機波動
        noise = 20 * np.random.randn(periods)
        
        # 合成價格
        base_price = trend + seasonal + noise
        
        # 生成OHLC數據
        data = []
        for i in range(periods):
            base = base_price[i]
            high = base + abs(np.random.randn() * 5)
            low = base - abs(np.random.randn() * 5)
            close = base + np.random.randn() * 2
            
            # 確保 high >= low
            if high < low:
                high, low = low, high
            
            # 確保 close 在 high/low 之間
            close = max(low, min(high, close))
            
            data.append({
                'timestamp': dates[i],
                'open': base,
                'high': high,
                'low': low,
                'close': close,
                'volume': np.random.randint(100, 1000)
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        print(f"   生成 {len(df)} 個數據點")
        print(f"   時間範圍: {df.index[0]} 到 {df.index[-1]}")
        print(f"   價格範圍: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
        print(f"   最新收盤價: ${df['close'].iloc[-1]:.2f}")
        
        return df
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算技術指標"""
        # 移動平均線
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        
        # RSI
        df['RSI'] = self.calculate_rsi(df['close'], period=14)
        
        # 布林帶
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        
        # MACD
        df['MACD'], df['MACD_signal'], df['MACD_hist'] = self.calculate_macd(df['close'])
        
        # ATR (平均真實波幅)
        df['ATR'] = self.calculate_atr(df, period=14)
        
        return df
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """計算RSI指標"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """計算MACD指標"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        return macd, signal, hist
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """計算ATR指標"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        
        atr = true_range.rolling(window=period).mean()
        return atr
    
    def analyze_signals(self, df: pd.DataFrame) -> Dict:
        """
        分析交易信號
        
        :return: 信號字典 {'action': 'BUY'/'SELL'/'HOLD', 'confidence': 0-1, 'reason': str}
        """
        if len(df) < 50:
            return {'action': 'HOLD', 'confidence': 0, 'reason': '數據不足'}
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        signals = []
        confidence_scores = []
        reasons = []
        
        # 策略1: 趨勢跟隨
        if self.strategies.get('trend_following', {}).get('enabled', False):
            # SMA交叉信號
            if prev['SMA_20'] <= prev['SMA_50'] and latest['SMA_20'] > latest['SMA_50']:
                signals.append('BUY')
                confidence_scores.append(0.7)
                reasons.append("SMA20上穿SMA50（黃金交叉）")
            elif prev['SMA_20'] >= prev['SMA_50'] and latest['SMA_20'] < latest['SMA_50']:
                signals.append('SELL')
                confidence_scores.append(0.7)
                reasons.append("SMA20下穿SMA50（死亡交叉）")
            
            # RSI信號
            rsi = latest['RSI']
            if pd.notna(rsi):
                if rsi < 30:
                    signals.append('BUY')
                    confidence_scores.append(0.6)
                    reasons.append(f"RSI超賣 ({rsi:.1f})")
                elif rsi > 70:
                    signals.append('SELL')
                    confidence_scores.append(0.6)
                    reasons.append(f"RSI超買 ({rsi:.1f})")
        
        # 策略2: 均值回歸
        if self.strategies.get('mean_reversion', {}).get('enabled', False):
            # 布林帶信號
            price = latest['close']
            if price <= latest['BB_lower']:
                signals.append('BUY')
                confidence_scores.append(0.8)
                reasons.append(f"價格觸及布林帶下軌 (${price:.2f})")
            elif price >= latest['BB_upper']:
                signals.append('SELL')
                confidence_scores.append(0.8)
                reasons.append(f"價格觸及布林帶上軌 (${price:.2f})")
        
        # 策略3: 突破交易
        if self.strategies.get('breakout', {}).get('enabled', False):
            # 簡單突破策略：價格創20日新高/新低
            lookback = 20
            if len(df) >= lookback:
                recent_high = df['high'].iloc[-lookback:-1].max()
                recent_low = df['low'].iloc[-lookback:-1].min()
                
                if latest['close'] > recent_high:
                    signals.append('BUY')
                    confidence_scores.append(0.75)
                    reasons.append(f"突破20日高點 (${recent_high:.2f})")
                elif latest['close'] < recent_low:
                    signals.append('SELL')
                    confidence_scores.append(0.75)
                    reasons.append(f"跌破20日低點 (${recent_low:.2f})")
        
        # 綜合信號
        if not signals:
            return {'action': 'HOLD', 'confidence': 0, 'reason': '無明確信號'}
        
        # 統計信號
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count > sell_count:
            avg_confidence = np.mean([c for s, c in zip(signals, confidence_scores) if s == 'BUY'])
            reason = " + ".join([r for s, r in zip(signals, reasons) if s == 'BUY'])
            return {'action': 'BUY', 'confidence': avg_confidence, 'reason': reason}
        elif sell_count > buy_count:
            avg_confidence = np.mean([c for s, c in zip(signals, confidence_scores) if s == 'SELL'])
            reason = " + ".join([r for s, r in zip(signals, reasons) if s == 'SELL'])
            return {'action': 'SELL', 'confidence': avg_confidence, 'reason': reason}
        else:
            # 買賣信號數量相同，選擇信心度高的
            max_idx = np.argmax(confidence_scores)
            return {'action': signals[max_idx], 'confidence': confidence_scores[max_idx], 'reason': reasons[max_idx]}
    
    def calculate_position_size(self, signal: Dict) -> float:
        """計算倉位大小（考慮0.01手限制）"""
        risk_per_trade = self.config.get('risk_per_trade', 0.002)  # 0.2%
        stop_loss_pips = self.config['risk_management']['stop_loss_pips']
        
        # 計算風險金額
        risk_amount = self.account_balance * risk_per_trade
        
        # 0.01手每點價值: $0.01
        pip_value_per_0_01_lot = 0.01
        
        # 計算理論手數
        theoretical_lot = risk_amount / (stop_loss_pips * pip_value_per_0_01_lot)
        
        # 應用0.01手限制
        actual_lot = min(theoretical_lot, self.max_lot_size)
        
        # 調整信心度
        confidence = signal.get('confidence', 0.5)
        adjusted_lot = actual_lot * confidence
        
        # 確保不小於0.01手的最小交易單位
        adjusted_lot = max(0.01, adjusted_lot)
        
        return round(adjusted_lot, 2)
    
    def execute_trade(self, signal: Dict, df: pd.DataFrame):
        """執行交易（模擬）"""
        if signal['action'] == 'HOLD':
            print(f"   ⏸️  持倉觀望: {signal['reason']}")
            return None
        
        # 計算倉位大小
        lot_size = self.calculate_position_size(signal)
        
        # 獲取當前價格
        current_price = df['close'].iloc[-1]
        
        # 計算止損止盈
        stop_loss_pips = self.config['risk_management']['stop_loss_pips']
        take_profit_pips = self.config['risk_management']['take_profit_pips']
        
        if signal['action'] == 'BUY':
            entry_price = current_price
            stop_loss = entry_price - (stop_loss_pips / 10)  # 黃金1點=0.10
            take_profit = entry_price + (take_profit_pips / 10)
            direction = "買入"
        else:  # SELL
            entry_price = current_price
            stop_loss = entry_price + (stop_loss_pips / 10)
            take_profit = entry_price - (take_profit_pips / 10)
            direction = "賣出"
        
        # 計算風險
        risk_per_pip = lot_size * 0.01  # 0.01手每點$0.01
        risk_amount = stop_loss_pips * risk_per_pip
        risk_percent = (risk_amount / self.account_balance) * 100
        
        # 創建交易記錄
        trade = {
            'id': len(self.trades_log) + 1,
            'timestamp': datetime.now().isoformat(),
            'action': signal['action'],
            'direction': direction,
            'lot_size': lot_size,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_amount': risk_amount,
            'risk_percent': risk_percent,
            'confidence': signal['confidence'],
            'reason': signal['reason'],
            'status': 'OPEN'
        }
        
        # 添加到交易記錄
        self.trades_log.append(trade)
        
        # 更新持倉狀態
        self.position_open = True
        self.current_position = trade
        
        print(f"\n   🎯 執行交易:")
        print(f"     方向: {direction}")
        print(f"     手數: {lot_size}手")
        print(f"     入場價: ${entry_price:.2f}")
        print(f"     止損: ${stop_loss:.2f} ({stop_loss_pips}點)")
        print(f"     止盈: ${take_profit:.2f
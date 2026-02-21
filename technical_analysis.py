#!/usr/bin/env python3
"""
技术分析库
包含平行通道、黄金分割、旗形、K线等技术分析工具
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class Trend(Enum):
    """趋势方向"""
    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    SIDEWAYS = "sideways"

class Pattern(Enum):
    """图表形态"""
    BULLISH_FLAG = "bullish_flag"      # 看涨旗形
    BEARISH_FLAG = "bearish_flag"      # 看跌旗形
    PARALLEL_CHANNEL = "parallel_channel"  # 平行通道
    GOLDEN_RATIO = "golden_ratio"      # 黄金分割
    BULLISH_ENGULFING = "bullish_engulfing"  # 看涨吞没
    BEARISH_ENGULFING = "bearish_engulfing"  # 看跌吞没
    HAMMER = "hammer"                  # 锤子线
    SHOOTING_STAR = "shooting_star"    # 射击之星

@dataclass
class KLine:
    """K线数据"""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    @property
    def body(self) -> float:
        """实体长度"""
        return abs(self.close - self.open)
    
    @property
    def upper_shadow(self) -> float:
        """上影线长度"""
        return self.high - max(self.open, self.close)
    
    @property
    def lower_shadow(self) -> float:
        """下影线长度"""
        return min(self.open, self.close) - self.low
    
    @property
    def is_bullish(self) -> bool:
        """是否是阳线"""
        return self.close > self.open
    
    @property
    def is_bearish(self) -> bool:
        """是否是阴线"""
        return self.close < self.open

class TechnicalAnalyzer:
    """技术分析器"""
    
    def __init__(self, data: pd.DataFrame):
        """
        初始化技术分析器
        
        Args:
            data: DataFrame包含以下列: ['date', 'open', 'high', 'low', 'close', 'volume']
        """
        self.data = data.copy()
        self.klines = self._create_klines()
        
    def _create_klines(self) -> List[KLine]:
        """创建K线对象列表"""
        klines = []
        for _, row in self.data.iterrows():
            kline = KLine(
                date=str(row['date']),
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=float(row['volume'])
            )
            klines.append(kline)
        return klines
    
    def calculate_sma(self, period: int = 20) -> pd.Series:
        """计算简单移动平均线"""
        return self.data['close'].rolling(window=period).mean()
    
    def calculate_ema(self, period: int = 20) -> pd.Series:
        """计算指数移动平均线"""
        return self.data['close'].ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, period: int = 14) -> pd.Series:
        """计算相对强弱指数(RSI)"""
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """计算MACD指标"""
        ema_fast = self.data['close'].ewm(span=fast_period, adjust=False).mean()
        ema_slow = self.data['close'].ewm(span=slow_period, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def identify_trend(self, lookback: int = 50) -> Trend:
        """识别趋势方向"""
        if len(self.data) < lookback:
            return Trend.SIDEWAYS
        
        recent_data = self.data.tail(lookback)
        highs = recent_data['high']
        lows = recent_data['low']
        
        # 计算高点和低点的线性回归斜率
        high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
        low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
        
        if high_slope > 0 and low_slope > 0:
            return Trend.UPTREND
        elif high_slope < 0 and low_slope < 0:
            return Trend.DOWNTREND
        else:
            return Trend.SIDEWAYS
    
    def find_parallel_channel(self, lookback: int = 100) -> Optional[Dict]:
        """寻找平行通道"""
        if len(self.data) < lookback:
            return None
        
        recent_data = self.data.tail(lookback)
        highs = recent_data['high'].values
        lows = recent_data['low'].values
        
        # 寻找显著的高点和低点
        from scipy.signal import argrelextrema
        
        # 寻找局部高点和低点
        high_indices = argrelextrema(highs, np.greater, order=5)[0]
        low_indices = argrelextrema(lows, np.less, order=5)[0]
        
        if len(high_indices) < 2 or len(low_indices) < 2:
            return None
        
        # 计算阻力线和支撑线
        resistance_points = highs[high_indices]
        support_points = lows[low_indices]
        
        # 线性拟合
        resistance_slope, resistance_intercept = np.polyfit(high_indices, resistance_points, 1)
        support_slope, support_intercept = np.polyfit(low_indices, support_points, 1)
        
        # 检查是否平行（斜率相近）
        slope_diff = abs(resistance_slope - support_slope)
        if slope_diff > 0.01:  # 斜率差异太大，不是平行通道
            return None
        
        return {
            'resistance_slope': resistance_slope,
            'resistance_intercept': resistance_intercept,
            'support_slope': support_slope,
            'support_intercept': support_intercept,
            'channel_width': resistance_intercept - support_intercept,
            'trend': 'up' if resistance_slope > 0 else 'down'
        }
    
    def calculate_golden_ratio_levels(self, swing_high: float, swing_low: float) -> Dict[str, float]:
        """计算黄金分割位"""
        price_range = swing_high - swing_low
        
        return {
            '0.0%': swing_low,
            '23.6%': swing_low + price_range * 0.236,
            '38.2%': swing_low + price_range * 0.382,
            '50.0%': swing_low + price_range * 0.5,
            '61.8%': swing_low + price_range * 0.618,
            '78.6%': swing_low + price_range * 0.786,
            '100.0%': swing_high,
            '127.2%': swing_high + price_range * 0.272,
            '161.8%': swing_high + price_range * 0.618,
            '261.8%': swing_high + price_range * 1.618
        }
    
    def identify_flag_pattern(self, lookback: int = 50) -> Optional[Pattern]:
        """识别旗形形态"""
        if len(self.data) < lookback:
            return None
        
        recent_data = self.data.tail(lookback)
        
        # 寻找旗杆（快速上涨或下跌）
        price_change = recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]
        price_change_pct = abs(price_change) / recent_data['close'].iloc[0]
        
        if price_change_pct < 0.05:  # 价格变化太小，不是旗形
            return None
        
        # 分析最近10根K线的整理形态
        consolidation_data = recent_data.tail(10)
        consolidation_high = consolidation_data['high'].max()
        consolidation_low = consolidation_data['low'].min()
        consolidation_range = consolidation_high - consolidation_low
        
        if consolidation_range / recent_data['close'].iloc[-1] < 0.02:  # 整理幅度太小
            return None
        
        # 判断旗形方向
        if price_change > 0:  # 上涨旗杆
            # 检查是否在整理（价格在区间内波动）
            if consolidation_data['close'].iloc[-1] < consolidation_data['close'].iloc[0]:
                return Pattern.BULLISH_FLAG
        else:  # 下跌旗杆
            if consolidation_data['close'].iloc[-1] > consolidation_data['close'].iloc[0]:
                return Pattern.BEARISH_FLAG
        
        return None
    
    def identify_candlestick_patterns(self, lookback: int = 10) -> List[Pattern]:
        """识别K线形态"""
        patterns = []
        
        if len(self.klines) < 2:
            return patterns
        
        # 分析最近几根K线
        recent_klines = self.klines[-lookback:]
        
        for i in range(1, len(recent_klines)):
            prev = recent_klines[i-1]
            curr = recent_klines[i]
            
            # 看涨吞没形态
            if (prev.is_bearish and curr.is_bullish and 
                curr.open < prev.close and curr.close > prev.open):
                patterns.append(Pattern.BULLISH_ENGULFING)
            
            # 看跌吞没形态
            elif (prev.is_bullish and curr.is_bearish and 
                  curr.open > prev.close and curr.close < prev.open):
                patterns.append(Pattern.BEARISH_ENGULFING)
            
            # 锤子线
            elif (curr.lower_shadow > 2 * curr.body and 
                  curr.upper_shadow < 0.1 * curr.body and
                  curr.is_bullish):
                patterns.append(Pattern.HAMMER)
            
            # 射击之星
            elif (curr.upper_shadow > 2 * curr.body and 
                  curr.lower_shadow < 0.1 * curr.body and
                  curr.is_bearish):
                patterns.append(Pattern.SHOOTING_STAR)
        
        return patterns
    
    def generate_signals(self) -> Dict:
        """生成交易信号"""
        signals = {
            'trend': self.identify_trend(),
            'patterns': [],
            'indicators': {},
            'recommendation': 'HOLD'
        }
        
        # 识别形态
        flag_pattern = self.identify_flag_pattern()
        if flag_pattern:
            signals['patterns'].append(flag_pattern)
        
        candlestick_patterns = self.identify_candlestick_patterns()
        signals['patterns'].extend(candlestick_patterns)
        
        # 计算技术指标
        signals['indicators']['sma_20'] = self.calculate_sma(20).iloc[-1]
        signals['indicators']['sma_50'] = self.calculate_sma(50).iloc[-1]
        signals['indicators']['rsi'] = self.calculate_rsi(14).iloc[-1]
        
        macd_line, signal_line, histogram = self.calculate_macd()
        signals['indicators']['macd'] = macd_line.iloc[-1]
        signals['indicators']['macd_signal'] = signal_line.iloc[-1]
        signals['indicators']['macd_histogram'] = histogram.iloc[-1]
        
        # 生成交易建议
        current_price = self.data['close'].iloc[-1]
        
        # RSI超买超卖
        if signals['indicators']['rsi'] > 70:
            signals['recommendation'] = 'SELL'
        elif signals['indicators']['rsi'] < 30:
            signals['recommendation'] = 'BUY'
        
        # MACD信号
        if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]:
            signals['recommendation'] = 'BUY'
        elif macd_line.iloc[-1] < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2]:
            signals['recommendation'] = 'SELL'
        
        # 形态信号
        if Pattern.BULLISH_ENGULFING in signals['patterns'] or Pattern.HAMMER in signals['patterns']:
            signals['recommendation'] = 'BUY'
        elif Pattern.BEARISH_ENGULFING in signals['patterns'] or Pattern.SHOOTING_STAR in signals['patterns']:
            signals['recommendation'] = 'SELL'
        
        return signals

# 示例使用
if __name__ == "__main__":
    # 创建示例数据
    dates = pd.date_range(start='2026-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    data = pd.DataFrame({
        'date': dates,
        'open': np.random.normal(100, 5, 100).cumsum(),
        'high': np.random.normal(105, 5, 100).cumsum(),
        'low': np.random.normal(95, 5, 100).cumsum(),
        'close': np.random.normal(100, 5, 100).cumsum(),
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    # 创建分析器
    analyzer = TechnicalAnalyzer(data)
    
    # 生成信号
    signals = analyzer.generate_signals()
    
    print("📊 技术分析结果:")
    print(f"趋势: {signals['trend']}")
    print(f"识别形态: {signals['patterns']}")
    print(f"RSI: {signals['indicators']['rsi']:.2f}")
    print(f"MACD: {signals['indicators']['macd']:.4f}")
    print(f"交易建议: {signals['recommendation']}")
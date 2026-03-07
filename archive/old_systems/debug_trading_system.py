#!/usr/bin/env python3
"""
调试交易系统 - 显示详细诊断信息
"""

import sys
import time
import json
import pandas as pd
from datetime import datetime, time as dt_time, timedelta
from futu import *

# 导入技术分析库
sys.path.append('/Users/gordonlui/.openclaw/workspace')
from technical_analysis import TechnicalAnalyzer, Pattern, Trend

class DebugTrader:
    """调试版交易器"""
    
    def __init__(self):
        self.trd_ctx = None
        self.quote_ctx = None
        self.trade_environment = TrdEnv.SIMULATE
        
        # 只监控盈富基金
        self.watchlist = ["HK.02800"]
        
    def connect(self):
        """连接富途API"""
        try:
            print("🔗 连接富途API...")
            self.trd_ctx = OpenSecTradeContext(host='127.0.0.1', port=11111)
            self.quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
            
            # 解锁交易（模拟环境）
            ret, data = self.trd_ctx.unlock_trade(password='123456')
            if ret != RET_OK:
                print("⚠️  交易解锁失败（模拟环境可能不需要）")
            
            print("✅ 连接成功")
            return True
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def get_market_snapshot(self, code):
        """获取市场快照"""
        ret, snapshot = self.quote_ctx.get_market_snapshot([code])
        if ret == RET_OK and len(snapshot) > 0:
            return snapshot.iloc[0]
        return None
    
    def get_historical_data(self, code, days=60):
        """获取历史数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        ret, hist_data, _ = self.quote_ctx.request_history_kline(
            code=code,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            ktype=KLType.K_DAY,
            autype=AuType.QFQ
        )
        
        if ret == RET_OK:
            return hist_data
        return None
    
    def analyze_stock_debug(self, code):
        """详细分析单只股票"""
        print(f"\n🔍 详细分析 {code}")
        
        # 获取当前价格
        snapshot = self.get_market_snapshot(code)
        if snapshot is None:
            print("  ❌ 无法获取市场快照")
            return None
        
        current_price = snapshot['last_price']
        volume = snapshot['volume']
        
        # 尝试不同的涨跌幅列名
        if 'change_rate' in snapshot:
            change_pct = snapshot['change_rate']
        elif 'change_ratio' in snapshot:
            change_pct = snapshot['change_ratio']
        else:
            change_pct = 0.0
        
        print(f"  当前价格: {current_price:.2f}")
        print(f"  成交量: {volume:,}")
        print(f"  涨跌幅: {change_pct:.2f}%")
        
        # 获取历史数据
        hist_data = self.get_historical_data(code, days=60)
        if hist_data is None or len(hist_data) < 20:
            print("  ❌ 历史数据不足")
            return None
        
        print(f"  历史数据: {len(hist_data)} 条K线")
        print(f"  价格范围: {hist_data['low'].min():.2f} - {hist_data['high'].max():.2f}")
        
        # 准备数据用于技术分析
        analysis_data = hist_data[['time_key', 'open', 'high', 'low', 'close', 'volume']].copy()
        analysis_data.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        # 技术分析
        analyzer = TechnicalAnalyzer(analysis_data)
        signals = analyzer.generate_signals()
        
        print(f"  趋势: {signals['trend']}")
        print(f"  形态: {signals['patterns']}")
        print(f"  RSI: {signals['indicators']['rsi']:.2f}")
        print(f"  MACD: {signals['indicators']['macd']:.4f}")
        print(f"  建议: {signals['recommendation']}")
        
        # 计算简单移动平均线
        sma_20 = hist_data['close'].tail(20).mean()
        sma_50 = hist_data['close'].tail(50).mean()
        
        print(f"  SMA20: {sma_20:.2f}")
        print(f"  SMA50: {sma_50:.2f}")
        
        # 价格相对于移动平均线的位置
        price_vs_sma20 = (current_price - sma_20) / sma_20 * 100
        price_vs_sma50 = (current_price - sma_50) / sma_50 * 100
        
        print(f"  价格 vs SMA20: {price_vs_sma20:+.2f}%")
        print(f"  价格 vs SMA50: {price_vs_sma50:+.2f}%")
        
        # 交易信号逻辑
        buy_signals = []
        sell_signals = []
        
        # 买入信号
        if signals['recommendation'] == 'BUY':
            buy_signals.append("技术分析建议买入")
        
        if price_vs_sma20 < -2:  # 价格低于SMA20 2%
            buy_signals.append("价格低于SMA20")
        
        if signals['indicators']['rsi'] < 35:
            buy_signals.append("RSI超卖")
        
        # 卖出信号
        if signals['recommendation'] == 'SELL':
            sell_signals.append("技术分析建议卖出")
        
        if price_vs_sma20 > 5:  # 价格高于SMA20 5%
            sell_signals.append("价格高于SMA20")
        
        if signals['indicators']['rsi'] > 65:
            sell_signals.append("RSI超买")
        
        print(f"  买入信号: {buy_signals}")
        print(f"  卖出信号: {sell_signals}")
        
        return {
            'code': code,
            'price': current_price,
            'volume': volume,
            'signals': signals,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'sma_20': sma_20,
            'sma_50': sma_50
        }
    
    def run(self):
        """运行调试"""
        print("=" * 70)
        print(f"🔧 交易系统调试")
        print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 环境: 模拟账户")
        print("=" * 70)
        
        if not self.connect():
            return
        
        # 分析每只股票
        for code in self.watchlist:
            analysis = self.analyze_stock_debug(code)
            
            if analysis:
                print(f"\n📋 {code} 交易决策:")
                
                if analysis['buy_signals']:
                    print(f"  🟢 建议买入")
                    print(f"     理由: {', '.join(analysis['buy_signals'])}")
                    print(f"     价格: {analysis['price']:.2f}")
                    print(f"     SMA20: {analysis['sma_20']:.2f}")
                elif analysis['sell_signals']:
                    print(f"  🔴 建议卖出")
                    print(f"     理由: {', '.join(analysis['sell_signals'])}")
                else:
                    print(f"  ⚪ 建议持有")
                    print(f"     没有明确的买卖信号")
        
        # 关闭连接
        self.quote_ctx.close()
        self.trd_ctx.close()
        
        print("\n✅ 调试完成")

if __name__ == "__main__":
    trader = DebugTrader()
    trader.run()
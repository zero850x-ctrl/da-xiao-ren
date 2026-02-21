#!/usr/bin/env python3
"""
自動交易系統增強版 - 整合成交量分析
Enhanced Automated Trading System with Volume Analysis
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 導入成交量分析模組
from volume_analyzer import calculate_volume_indicators, analyze_volume_price_relationship, get_volume_trading_signal

class VolumeEnhancedTrader:
    """成交量增強的交易系統"""
    
    def __init__(self):
        self.name = "成交量增強交易系統"
        self.version = "2.0"
        self.trades_log = []
        
        # 默認配置
        self.config = {
            'initial_trade_amount': 10000,  # 初始交易金額
            'dca_amount': 5000,             # 定投金額
            'max_positions': 5,             # 最大持倉數
            'stop_loss_pct': 2,             # 止損比例%
            'take_profit_pct': 10,          # 止盈比例%
        }
        
        # 監控股票列表（帶成交量篩選）
        self.monitored_stocks = [
            {
                "code": "02800",
                "name": "盈富基金",
                "strategy": "momentum",
                "target_price": 27.5,
                "stop_loss": 26.5,
                "volume_filter": True,  # 啟用成交量過濾
            },
            {
                "code": "00700",
                "name": "騰訊控股",
                "strategy": "value",
                "target_price": 580,
                "stop_loss": 530,
                "volume_filter": True,
            },
            {
                "code": "09988",
                "name": "阿里巴巴",
                "strategy": "momentum",
                "target_price": 165,
                "stop_loss": 145,
                "volume_filter": True,
            },
            {
                "code": "01299",
                "name": "友邦保險",
                "strategy": "value",
                "target_price": 95,
                "stop_loss": 75,
                "volume_filter": True,
            },
            {
                "code": "02318",
                "name": "中國平安",
                "strategy": "value",
                "target_price": 58,
                "stop_loss": 48,
                "volume_filter": True,
            },
        ]
        
        # 持倉
        self.positions = {}
        
    def get_simulated_kline(self, stock_code, days=30):
        """獲取模擬K線數據（實際應該從API獲取）"""
        np.random.seed(int(stock_code) % 1000)
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # 模擬價格
        base_price = 100 + np.random.randint(-30, 30)
        prices = [base_price]
        for i in range(days - 1):
            change = np.random.normal(0.1, 2)
            prices.append(prices[-1] * (1 + change/100))
        
        # 模擬成交量（與價格變化相關）
        volumes = []
        for i in range(days):
            price_change = abs((prices[i] - prices[i-1]) / prices[i-1]) if i > 0 else 0
            base_vol = 1000000
            vol = base_vol * (1 + price_change * 10) * np.random.uniform(0.5, 1.5)
            volumes.append(max(vol, 100000))
        
        df = pd.DataFrame({
            'time': dates,
            'open': prices,
            'high': [p * 1.02 for p in prices],
            'low': [p * 0.98 for p in prices],
            'close': prices,
            'volume': volumes,
        })
        
        return df
    
    def analyze_volume_filter(self, stock_code, current_price):
        """
        成交量過濾分析
        返回: (是否通過過濾, 信號, 原因)
        """
        # 獲取K線數據
        df = self.get_simulated_kline(stock_code, days=30)
        
        # 計算成交量指標
        volume_indicators = calculate_volume_indicators(df)
        volume_analysis = analyze_volume_price_relationship(df)
        
        result = {
            'passed': True,
            'signal': 'NEUTRAL',
            'reason': '成交量分析正常',
            'volume_ratio': volume_indicators.get('volume_ratio', 1),
            'volume_change': volume_indicators.get('volume_change', 0),
            'signal_name': volume_analysis.get('signal', '中性'),
            'action': volume_analysis.get('action', '觀望'),
            'strength': volume_analysis.get('strength', '弱'),
        }
        
        # ====== 成交量過濾規則 ======
        
        # 規則1: 買入時必須有成交量配合
        buy_volume_signals = ['🟢 量漲價漲', '🟢 底部縮量', '🟢 恐慌後反彈']
        sell_volume_signals = ['🔴 高位放量滯漲', '🔴 井噴後暴跌', '🔴 跌破放量', '🔴 天量在低位']
        
        # 規則2: 買入信號檢查
        for signal in buy_volume_signals:
            if signal in result['signal_name']:
                result['passed'] = True
                result['signal'] = 'BUY_VOLUME'
                result['reason'] = f'成交量買入信號: {result["signal_name"]}'
                return result
        
        # 規則3: 賣出信號檢查
        for signal in sell_volume_signals:
            if signal in result['signal_name']:
                result['passed'] = True
                result['signal'] = 'SELL_VOLUME'
                result['reason'] = f'成交量賣出信號: {result["signal_name"]}'
                return result
        
        # 規則4: 異常成交量過濾
        if volume_indicators.get('volume_ratio', 1) > 3:
            # 成交量異常放大，可能是假突破
            result['passed'] = False
            result['signal'] = 'VOLUME_SPIKE'
            result['reason'] = f'成交量異常放大({volume_indicators.get("volume_ratio"):.1f}倍)，謹慎操作'
        
        elif volume_indicators.get('volume_ratio', 1) < 0.2:
            # 成交量異常萎縮
            result['passed'] = False
            result['signal'] = 'VOLUME_COLLAPSE'
            result['reason'] = f'成交量異常萎縮({volume_indicators.get("volume_ratio"):.1f}倍)，市場觀望'
        
        return result
    
    def analyze_with_volume(self, stock_info):
        """
        整合成交量分析的股票分析
        """
        stock_code = stock_info['code']
        current_price = 100 + np.random.randint(-30, 30)  # 模擬價格
        
        analysis = {
            'stock_code': stock_code,
            'name': stock_info['name'],
            'strategy': stock_info['strategy'],
            'current_price': current_price,
            'action': 'HOLD',
            'reason': '',
            'volume_filter': stock_info.get('volume_filter', True),
            'volume_analysis': None,
        }
        
        # 首先進行成交量分析
        if stock_info.get('volume_filter', True):
            vol_result = self.analyze_volume_filter(stock_code, current_price)
            analysis['volume_analysis'] = vol_result
            
            # 根據成交量信號調整交易決策
            if vol_result['signal'] == 'BUY_VOLUME':
                # 成交量買入信號 - 增強買入信心
                analysis['volume_boost'] = '增強'
                analysis['reason'] += f"成交量: {vol_result['reason']};"
            
            elif vol_result['signal'] == 'SELL_VOLUME':
                # 成交量賣出信號 - 增強賣出信號
                analysis['volume_boost'] = '減持'
                analysis['reason'] += f"成交量: {vol_result['reason']};"
            
            elif not vol_result['passed']:
                # 成交量異常 - 推遲交易
                analysis['volume_boost'] = '觀望'
                analysis['action'] = 'HOLD'
                analysis['reason'] += f"成交量異常: {vol_result['reason']};"
                return analysis
        
        # 根據策略分析
        strategy = stock_info['strategy']
        
        if strategy == 'momentum':
            target = stock_info.get('target_price', current_price * 1.1)
            stop_loss = stock_info.get('stop_loss', current_price * 0.95)
            
            if current_price >= target * 0.98:
                analysis['action'] = 'SELL'
                analysis['reason'] += f'接近目標價{target}'
                
            elif current_price <= stop_loss:
                analysis['action'] = 'SELL'
                analysis['reason'] += f'觸發止損{stop_loss}'
                
            elif current_price <= target * 0.85:
                analysis['action'] = 'BUY'
                analysis['reason'] += f'價格低於目標85%'
        
        elif strategy == 'value':
            target = stock_info.get('target_price', current_price * 1.2)
            # 只有當前價格低於目標價才算折扣
            if current_price < target:
                discount = ((target - current_price) / target) * 100
                if discount >= 15:
                    analysis['action'] = 'BUY'
                    analysis['reason'] += f'價值折扣{discount:.1f}%'
            else:
                analysis['action'] = 'SELL'
                analysis['reason'] += f'價格高於目標，溢价{((current_price - target) / target * 100):.1f}%'
        
        # 如果成交量分析，增強信號（但不能覆蓋止損決策）
        if analysis['volume_analysis'] and analysis['volume_analysis']['signal'] == 'BUY_VOLUME':
            if analysis['action'] in ['HOLD', 'BUY']:
                # 成交量顯示買入信號，如果當前是 HOLD 可以考慮買入
                if analysis['action'] == 'HOLD':
                    analysis['action'] = 'BUY'
                    analysis['reason'] += '成交量買入信號觸發'
        
        elif analysis['volume_analysis'] and analysis['volume_analysis']['signal'] == 'SELL_VOLUME':
            # 成交量顯示賣出信號，應該賣出（即使策略說 HOLD）
            if analysis['action'] in ['HOLD', 'BUY']:
                analysis['action'] = 'SELL'
                analysis['reason'] += '成交量賣出信號觸發'
        
        # 價漲量縮是警示信號，應該觀望或減持
        elif analysis['volume_analysis'] and '⚠️' in analysis['volume_analysis']['signal_name']:
            if analysis['action'] == 'BUY':
                analysis['action'] = 'HOLD'
                analysis['reason'] += '量價背離，暫緩買入'
        
        return analysis
    
    def run_analysis(self):
        """運行分析"""
        print("=" * 60)
        print("📊 成交量增強自動交易系統")
        print(f"版本: {self.version}")
        print("=" * 60)
        
        buy_signals = []
        sell_signals = []
        hold_signals = []
        
        for stock in self.monitored_stocks:
            analysis = self.analyze_with_volume(stock)
            
            print(f"\n{analysis['stock_code']} {analysis['name']}")
            print(f"  價格: ${analysis['current_price']:.2f}")
            print(f"  策略: {analysis['strategy']}")
            
            if analysis['volume_analysis']:
                va = analysis['volume_analysis']
                print(f"  成交量: 量比={va['volume_ratio']:.2f}, 信號={va['signal_name']}")
                print(f"  成交量建議: {va['action']}")
            
            print(f"  動作: {analysis['action']}")
            print(f"  原因: {analysis['reason']}")
            
            if analysis['action'] == 'BUY':
                buy_signals.append(analysis)
            elif analysis['action'] == 'SELL':
                sell_signals.append(analysis)
            else:
                hold_signals.append(analysis)
        
        # 總結
        print("\n" + "=" * 60)
        print("📈 交易信號總結")
        print("=" * 60)
        
        if buy_signals:
            print(f"\n🟢 買入信號 ({len(buy_signals)}):")
            for s in buy_signals:
                print(f"  • {s['stock_code']} {s['name']}: {s['reason']}")
        
        if sell_signals:
            print(f"\n🔴 賣出信號 ({len(sell_signals)}):")
            for s in sell_signals:
                print(f"  • {s['stock_code']} {s['name']}: {s['reason']}")
        
        if hold_signals:
            print(f"\n⚪ 觀望 ({len(hold_signals)}):")
            for s in hold_signals:
                print(f"  • {s['stock_code']} {s['name']}: {s['reason']}")
        
        if not buy_signals and not sell_signals:
            print("\n⚪ 無交易信號，市場觀望中")
        
        return {
            'buy': buy_signals,
            'sell': sell_signals,
            'hold': hold_signals
        }


def main():
    """主函數"""
    trader = VolumeEnhancedTrader()
    results = trader.run_analysis()
    
    return results

if __name__ == "__main__":
    main()

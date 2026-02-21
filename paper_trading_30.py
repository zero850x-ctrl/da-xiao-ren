#!/usr/bin/env python3
"""
模擬交易練習系統 - Paper Trading
30隻股票自動交易練習
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

# 添加路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 導入成交量分析
from volume_analyzer import calculate_volume_indicators, analyze_volume_price_relationship, get_volume_trading_signal

class PaperTrader:
    """模擬交易系統"""
    
    def __init__(self, initial_capital=1000000):  # 初始資金100萬
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self.positions = {}  # 持倉 {code: {'qty': 數量, 'avg_price': 均價}}
        self.trade_history = []  # 交易歷史
        self.portfolio_value = initial_capital
        self.total_pnl = 0
        
    def get_stock_data(self, stock_code, days=60):
        """獲取股票模擬數據"""
        np.random.seed(int(stock_code.replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', '')[:3] or '1', 36) * 1000 + int(stock_code))
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # 根據股票代碼生成合理的價格
        code_int = int(stock_code.lstrip('0') or '1')
        
        # 合理的股價範圍 (10-300)
        base_price = 30 + (code_int % 200)
        
        # 價格趨勢（不同的股票有不同的趨勢）
        trend = (code_int % 3 - 1) * 0.002  # -0.002, 0, 0.002
        volatility = 0.015 + (code_int % 5) * 0.005
        
        prices = [base_price]
        for i in range(days - 1):
            change = np.random.normal(trend, volatility)
            prices.append(max(prices[-1] * (1 + change), 5))  # 最低5元
        
        # 成交量
        volumes = []
        for i in range(days):
            price_change = abs((prices[i] - prices[i-1]) / prices[i-1]) if i > 0 else 0
            base_vol = 500000 + (code_int % 20) * 50000
            vol = base_vol * (1 + price_change * 3) * np.random.uniform(0.5, 1.5)
            volumes.append(max(vol, 100000))
        
        df = pd.DataFrame({
            'time': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': volumes,
        })
        
        return df
    
    def analyze_stock(self, stock_code, stock_name):
        """分析股票"""
        df = self.get_stock_data(stock_code)
        current_price = df['close'].iloc[-1]
        
        # 技術指標
        closes = df['close'].astype(float)
        ma5 = closes.tail(5).mean()
        ma20 = closes.tail(20).mean()
        
        # RSI
        if len(closes) >= 14:
            changes = closes.diff()
            gains = changes.where(changes > 0, 0)
            losses = (-changes).where(changes < 0, 0)
            avg_gain = gains.tail(14).mean()
            avg_loss = losses.tail(14).mean()
            rs = avg_gain / avg_loss if avg_loss > 0 else 100
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 50
        
        # 成交量分析
        vol_indicators = calculate_volume_indicators(df)
        vol_analysis = analyze_volume_price_relationship(df)
        
        # 趨勢判斷
        if current_price > ma5 > ma20:
            trend = '上升'
        elif current_price < ma5 < ma20:
            trend = '下降'
        else:
            trend = '震盪'
        
        # 信號評估
        signal = 'HOLD'
        reason = ''
        
        # 買入條件
        buy_score = 0
        
        # 趨勢向上的放量信號
        if '🟢' in vol_analysis.get('signal', '') and trend == '上升':
            buy_score += 3
            reason += '量價齊漲;'
        
        # RSI超賣
        if rsi < 35:
            buy_score += 2
            reason += 'RSI超賣;'
        
        # 價格在均線支撐
        if current_price > ma20 * 0.95:
            buy_score += 1
            reason += '站穩MA20;'
        
        # 成交量底部信號
        if '🟢' in vol_analysis.get('signal', '') and '底部' in vol_analysis.get('meaning', ''):
            buy_score += 2
            reason += '底部縮量;'
        
        # 賣出條件
        sell_score = 0
        
        # 放量下跌信號
        if '🔴' in vol_analysis.get('signal', ''):
            sell_score += 3
            reason += '放量下跌;'
        
        # RSI超買
        if rsi > 65:
            sell_score += 2
            reason += 'RSI超買;'
        
        # 跌破均線
        if current_price < ma20 * 0.95:
            sell_score += 2
            reason += '跌破MA20;'
        
        # 價漲量縮
        if '⚠️' in vol_analysis.get('signal', ''):
            sell_score += 1
            reason += '量價背離;'
        
        # 決定信號
        if buy_score >= 4:
            signal = 'BUY'
            reason = f'買入信號(分數:{buy_score}): ' + reason
        elif sell_score >= 3:
            signal = 'SELL'
            reason = f'賣出信號(分數:{sell_score}): ' + reason
        else:
            signal = 'HOLD'
            reason = f'觀望(買入:{buy_score}, 賣出:{sell_score})'
        
        return {
            'code': stock_code,
            'name': stock_name,
            'price': round(current_price, 2),
            'trend': trend,
            'rsi': round(rsi, 1),
            'ma5': round(ma5, 2),
            'ma20': round(ma20, 2),
            'volume_ratio': vol_indicators.get('volume_ratio', 1),
            'volume_signal': vol_analysis.get('signal', '中性'),
            'signal': signal,
            'reason': reason,
            'buy_score': buy_score,
            'sell_score': sell_score
        }
    
    def execute_trade(self, analysis):
        """執行交易"""
        code = analysis['code']
        signal = analysis['signal']
        price = analysis['price']
        
        if signal == 'BUY':
            # 買入
            if code not in self.positions:
                # 每隻股票投入約3%資金
                trade_amount = self.cash * 0.03
                qty = int(trade_amount / price / 100) * 100  # 整手
                
                if qty > 0 and self.cash >= qty * price:
                    self.cash -= qty * price
                    self.positions[code] = {
                        'qty': qty,
                        'avg_price': price,
                        'name': analysis['name']
                    }
                    self.trade_history.append({
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'code': code,
                        'name': analysis['name'],
                        'action': 'BUY',
                        'qty': qty,
                        'price': price,
                        'reason': analysis['reason']
                    })
                    return f"✅ 買入 {code} {qty}股 @ ${price}"
            
        elif signal == 'SELL':
            # 賣出
            if code in self.positions:
                position = self.positions[code]
                qty = position['qty']
                
                self.cash += qty * price
                profit = (price - position['avg_price']) * qty
                self.trade_history.append({
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'code': code,
                    'name': analysis['name'],
                    'action': 'SELL',
                    'qty': qty,
                    'price': price,
                    'profit': profit,
                    'reason': analysis['reason']
                })
                del self.positions[code]
                return f"🔴 賣出 {code} {qty}股 @ ${price} (獲利: ${profit:+.2f})"
        
        return None
    
    def calculate_portfolio_value(self, stocks_data):
        """計算組合價值"""
        positions_value = 0
        for code, pos in self.positions.items():
            # 找到最新價格
            price = pos['avg_price']
            for sd in stocks_data:
                if sd['code'] == code:
                    price = sd['price']
                    break
            positions_value += pos['qty'] * price
        
        self.portfolio_value = self.cash + positions_value
        self.total_pnl = self.portfolio_value - self.initial_capital
        
    def get_status(self):
        """獲取狀態"""
        return {
            'cash': round(self.cash, 2),
            'positions_value': round(self.portfolio_value - self.cash, 2),
            'total_value': round(self.portfolio_value, 2),
            'total_pnl': round(self.total_pnl, 2),
            'pnl_pct': round((self.total_pnl / self.initial_capital) * 100, 2),
            'num_positions': len(self.positions)
        }

# 30隻股票列表
STOCKS = [
    # 藍籌股
    {"code": "00001", "name": "長和"},
    {"code": "00005", "name": "匯豐控股"},
    {"code": "00011", "name": "恒生銀行"},
    {"code": "00175", "name": "恒生銀行"},
    {"code": "01128", "name": "澳門博彩"},
    {"code": "00939", "name": "建設銀行"},
    {"code": "00981", "name": "中芯國際"},
    {"code": "01398", "name": "工商銀行"},
    # 科技股
    {"code": "00700", "name": "騰訊控股"},
    {"code": "09988", "name": "阿里巴巴"},
    {"code": "03690", "name": "美團"},
    {"code": "01810", "name": "小米集團"},
    {"code": "02269", "name": "藥明生物"},
    {"code": "06186", "name": "中國飛鶴"},
    # 金融地產
    {"code": "02318", "name": "中國平安"},
    {"code": "01299", "name": "友邦保險"},
    {"code": "02628", "name": "中國人壽"},
    {"code": "00016", "name": "九龍倉置業"},
    {"code": "00101", "name": "恆隆地產"},
    {"code": "06808", "name": "京東健康"},
    # 消費及公用
    {"code": "02800", "name": "盈富基金"},
    {"code": "02828", "name": "恆生ETF"},
    {"code": "00178", "name": "FIA"},
    {"code": "00388", "name": "港交所"},
    {"code": "00522", "name": "中移動"},
    {"code": "02647", "name": "新鴻基地產"},
    {"code": "01728", "name": "恒大汽車"},
    {"code": "06618", "name": "京東物流"},
    {"code": "09618", "name": "快手"},
    {"code": "06677", "name": "農夫山泉"},
]

def run_paper_trading():
    """運行模擬交易"""
    print("=" * 70)
    print("📈 模擬交易練習系統 - Paper Trading")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    # 創建交易系統
    trader = PaperTrader(initial_capital=1000000)
    
    print(f"\n💰 初始資金: ${trader.initial_capital:,.2f}")
    print(f"📊 股票數量: {len(STOCKS)}")
    print("\n" + "-" * 70)
    
    # 分析所有股票
    print("\n🔍 正在分析30隻股票...")
    all_analysis = []
    
    for stock in STOCKS:
        analysis = trader.analyze_stock(stock['code'], stock['name'])
        all_analysis.append(analysis)
    
    # 統計信號
    buy_signals = [a for a in all_analysis if a['signal'] == 'BUY']
    sell_signals = [a for a in all_analysis if a['signal'] == 'SELL']
    hold_signals = [a for a in all_analysis if a['signal'] == 'HOLD']
    
    print(f"\n📊 信號統計:")
    print(f"  🟢 買入: {len(buy_signals)}隻")
    print(f"  🔴 賣出: {len(sell_signals)}隻")
    print(f"  ⚪ 觀望: {len(hold_signals)}隻")
    
    # 顯示買入信號
    if buy_signals:
        print(f"\n🟢 買入信號 ({len(buy_signals)}隻):")
        for a in sorted(buy_signals, key=lambda x: -x['buy_score'])[:10]:
            print(f"  • {a['code']} {a['name']}: ${a['price']} (Score: {a['buy_score']})")
            print(f"    RSI:{a['rsi']}, 趨勢:{a['trend']}, 量比:{a['volume_ratio']:.2f}")
    
    # 顯示賣出信號
    if sell_signals:
        print(f"\n🔴 賣出信號 ({len(sell_signals)}隻):")
        for a in sorted(sell_signals, key=lambda x: -x['sell_score'])[:10]:
            print(f"  • {a['code']} {a['name']}: ${a['price']} (Score: {a['sell_score']})")
            print(f"    RSI:{a['rsi']}, 趨勢:{a['trend']}, 信號:{a['volume_signal']}")
    
    # 執行交易
    print("\n" + "-" * 70)
    print("📋 執行交易...")
    
    trades_executed = []
    
    # 先處理賣出
    for a in sell_signals:
        # 檢查是否持有
        if a['code'] in trader.positions:
            result = trader.execute_trade(a)
            if result:
                trades_executed.append(result)
                print(result)
    
    # 再處理買入
    for a in buy_signals:
        result = trader.execute_trade(a)
        if result:
            trades_executed.append(result)
            print(result)
    
    if not trades_executed:
        print("  無交易執行")
    
    # 更新組合價值
    trader.calculate_portfolio_value(all_analysis)
    status = trader.get_status()
    
    # 顯示當前持倉
    print("\n" + "-" * 70)
    print("📦 當前持倉:")
    if trader.positions:
        for code, pos in trader.positions.items():
            print(f"  • {code} {pos['name']}: {pos['qty']}股 @ ${pos['avg_price']:.2f}")
    else:
        print("  無持倉")
    
    # 顯示最終狀態
    print("\n" + "=" * 70)
    print("💵 組合狀態:")
    print(f"  現金: ${status['cash']:,.2f}")
    print(f"  持倉價值: ${status['positions_value']:,.2f}")
    print(f"  總價值: ${status['total_value']:,.2f}")
    print(f"  總盈虧: ${status['total_pnl']:+,.2f} ({status['pnl_pct']:+.2f}%)")
    print(f"  持倉數: {status['num_positions']}隻")
    print("=" * 70)
    
    # 顯示交易歷史
    if trader.trade_history:
        print("\n📜 交易歷史 (最近10筆):")
        for t in trader.trade_history[-10:]:
            emoji = "🟢" if t['action'] == 'BUY' else "🔴"
            profit_str = f" (賺${t.get('profit', 0):+.2f})" if t['action'] == 'SELL' else ""
            print(f"  {emoji} {t['time']} {t['code']} {t['action']} {t['qty']}股 @ ${t['price']}{profit_str}")
    
    return trader, all_analysis

if __name__ == "__main__":
    run_paper_trading()

#!/usr/bin/env python3
"""
富途API模擬交易系統 - Paper Trading
使用富途API獲取真實數據，支持模擬倉自動落盤
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

# 成交量分析模組
from volume_analyzer import calculate_volume_indicators, analyze_volume_price_relationship, get_volume_trading_signal

# 富途API
try:
    from futu import *
    FUTU_AVAILABLE = True
except ImportError:
    print("⚠️ 富途API未安裝，將使用模擬數據")
    FUTU_AVAILABLE = False

class FutuPaperTrader:
    """富途API模擬交易系統"""
    
    def __init__(self, initial_capital=1000000):
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self.positions = {}
        self.trade_history = []
        self.portfolio_value = initial_capital
        self.quote_ctx = None
        self.trd_ctx = None
        
    def connect_futu(self):
        """連接富途API"""
        if not FUTU_AVAILABLE:
            print("❌ 富途API不可用")
            return False
            
        try:
            self.quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
            print("✅ 成功連接富途報價API")
            return True
        except Exception as e:
            print(f"❌ 連接富途API失敗: {e}")
            return False
    
    def get_stock_price(self, stock_code):
        """獲取股票實時價格"""
        if not self.quote_ctx:
            return None
            
        try:
            # 確保代碼格式正確
            if not stock_code.startswith('HK.'):
                stock_code = f"HK.{stock_code}"
                
            ret, data = self.quote_ctx.get_market_snapshot([stock_code])
            if ret == RET_OK:
                return float(data['last_price'].iloc[0])
            else:
                print(f"❌ 獲取{stock_code}價格失敗: {data}")
                return None
        except Exception as e:
            print(f"❌ 獲取{stock_code}價格異常: {e}")
            return None
    
    def get_kline_data(self, stock_code, days=60):
        """獲取K線數據"""
        if not self.quote_ctx:
            return self.get_simulated_data(stock_code, days)
        
        try:
            if not stock_code.startswith('HK.'):
                stock_code = f"HK.{stock_code}"
            
            # 使用 request_history_kline
            ret, data, page_req_key = self.quote_ctx.request_history_kline(
                stock_code, 
                start=(datetime.now() - timedelta(days=days*2)).strftime('%Y-%m-%d'),
                end=datetime.now().strftime('%Y-%m-%d'),
                max_count=days
            )
            
            if ret == RET_OK and data is not None and len(data) > 0:
                # 轉換格式
                df = data[['time', 'open', 'high', 'low', 'close', 'volume']].copy()
                df['time'] = pd.to_datetime(df['time'])
                df = df.tail(days)
                return df
            else:
                return self.get_simulated_data(stock_code, days)
                
        except Exception as e:
            return self.get_simulated_data(stock_code, days)
    
    def get_simulated_data(self, stock_code, days=60):
        """獲取模擬數據（後備）"""
        np.random.seed(int(stock_code.replace('HK.', '') or '1') * 1000 + int(datetime.now().timestamp()) % 1000)
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        code_int = int(stock_code.replace('HK.', '').lstrip('0') or '1')
        base_price = 20 + (code_int % 200)
        
        trend = (code_int % 3 - 1) * 0.002
        volatility = 0.02 + (code_int % 5) * 0.01
        
        prices = [base_price]
        for i in range(days - 1):
            change = np.random.normal(trend, volatility)
            prices.append(max(prices[-1] * (1 + change), 5))
        
        volumes = []
        for i in range(days):
            price_change = abs((prices[i] - prices[i-1]) / prices[i-1]) if i > 0 else 0
            base_vol = 500000 + (code_int % 20) * 50000
            vol = base_vol * (1 + price_change * 3) * np.random.uniform(0.5, 1.5)
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
    
    def analyze_stock(self, stock_code, stock_name):
        """分析股票"""
        # 獲取K線數據
        df = self.get_kline_data(stock_code, days=60)
        
        if df is None or len(df) < 30:
            return None
        
        # 獲取當前價格
        current_price = self.get_stock_price(stock_code)
        if current_price is None:
            current_price = df['close'].iloc[-1]
        
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
        
        # 趨勢
        if current_price > ma5 > ma20:
            trend = '上升'
        elif current_price < ma5 < ma20:
            trend = '下降'
        else:
            trend = '震盪'
        
        # 信號評分
        buy_score = 0
        sell_score = 0
        
        if '🟢' in vol_analysis.get('signal', '') and trend == '上升':
            buy_score += 3
        
        if rsi < 35:
            buy_score += 2
        
        if current_price > ma20 * 0.95:
            buy_score += 1
        
        if '🟢' in vol_analysis.get('signal', '') and '底部' in vol_analysis.get('meaning', ''):
            buy_score += 2
        
        if '🔴' in vol_analysis.get('signal', ''):
            sell_score += 3
        
        if rsi > 65:
            sell_score += 2
        
        if current_price < ma20 * 0.95:
            sell_score += 2
        
        if '⚠️' in vol_analysis.get('signal', ''):
            sell_score += 1
        
        # 決定信號
        if buy_score >= 4:
            signal = 'BUY'
            reason = f'買入(分數:{buy_score})'
        elif sell_score >= 3:
            signal = 'SELL'
            reason = f'賣出(分數:{sell_score})'
        else:
            signal = 'HOLD'
            reason = f'觀望(買:{buy_score}, 賣:{sell_score})'
        
        return {
            'code': stock_code.replace('HK.', ''),
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
        
        if signal == 'BUY' and code not in self.positions:
            trade_amount = self.cash * 0.03
            qty = int(trade_amount / price / 100) * 100
            
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
                    'action': 'BUY',
                    'qty': qty,
                    'price': price,
                    'reason': analysis['reason']
                })
                return f"✅ 買入 {code} {qty}股 @ ${price}"
        
        elif signal == 'SELL' and code in self.positions:
            position = self.positions[code]
            qty = position['qty']
            
            self.cash += qty * price
            profit = (price - position['avg_price']) * qty
            self.trade_history.append({
                'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'code': code,
                'action': 'SELL',
                'qty': qty,
                'price': price,
                'profit': profit,
                'reason': analysis['reason']
            })
            del self.positions[code]
            return f"🔴 賣出 {code} {qty}股 @ ${price} (賺${profit:+,.2f})"
        
        return None
    
    def calculate_portfolio_value(self, stocks_data):
        """計算組合價值"""
        positions_value = 0
        for code, pos in self.positions.items():
            price = pos['avg_price']
            for sd in stocks_data:
                if sd['code'] == code:
                    price = sd['price']
                    break
            positions_value += pos['qty'] * price
        
        self.portfolio_value = self.cash + positions_value
        
    def get_status(self):
        return {
            'cash': round(self.cash, 2),
            'positions_value': round(self.portfolio_value - self.cash, 2),
            'total_value': round(self.portfolio_value, 2),
            'total_pnl': round(self.portfolio_value - self.initial_capital, 2),
            'pnl_pct': round((self.portfolio_value - self.initial_capital) / self.initial_capital * 100, 2),
            'num_positions': len(self.positions)
        }


# 50隻股票列表（已移除退市的恒生銀行）
STOCKS_50 = [
    # 藍籌股 (15隻)
    {"code": "00001", "name": "長和"},
    {"code": "00005", "name": "匯豐控股"},
    {"code": "01128", "name": "澳門博彩"},
    {"code": "00939", "name": "建設銀行"},
    {"code": "00981", "name": "中芯國際"},
    {"code": "01398", "name": "工商銀行"},
    {"code": "03333", "name": "中國能源"},
    {"code": "00968", "name": "中國電力"},
    # 科技股 (10隻)
    {"code": "00700", "name": "騰訊控股"},
    {"code": "09988", "name": "阿里巴巴"},
    {"code": "03690", "name": "美團"},
    {"code": "01810", "name": "小米集團"},
    {"code": "02269", "name": "藥明生物"},
    {"code": "06186", "name": "中國飛鶴"},
    {"code": "09618", "name": "快手"},
    {"code": "06618", "name": "京東物流"},
    {"code": "02490", "name": "泡泡瑪特"},
    {"code": "03888", "name": "金山軟件"},
    # 金融保險 (8隻)
    {"code": "02318", "name": "中國平安"},
    {"code": "01299", "name": "友邦保險"},
    {"code": "02628", "name": "中國人壽"},
    {"code": "02388", "name": "中銀香港"},
    {"code": "03988", "name": "中國銀行"},
    {"code": "06677", "name": "農夫山泉"},
    # 地產 (7隻)
    {"code": "00016", "name": "九龍倉置業"},
    {"code": "00101", "name": "恆隆地產"},
    {"code": "02647", "name": "新鴻基地產"},
    {"code": "01113", "name": "長實集團"},
    {"code": "00175", "name": "恒生銀行"},  # 注意：用新編碼
    {"code": "06808", "name": "京東健康"},
    # 消費及公用 (10隻)
    {"code": "02800", "name": "盈富基金"},
    {"code": "02828", "name": "恆生ETF"},
    {"code": "00178", "name": "FIA"},
    {"code": "00388", "name": "港交所"},
    {"code": "00522", "name": "中移動"},
    {"code": "01728", "name": "恒大汽車"},
    {"code": "01928", "name": "銀河娛樂"},
    {"code": "02202", "name": "石藥集團"},
    {"code": "00883", "name": "中國海洋石油"},
    {"code": "00857", "name": "中國石油"},
]

def run_futu_paper_trading():
    """運行富途API模擬交易"""
    print("=" * 70)
    print("📈 富途API模擬交易系統 - Paper Trading")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    # 創建交易系統
    trader = FutuPaperTrader(initial_capital=1000000)
    
    # 嘗試連接富途API
    trader.connect_futu()
    
    print(f"\n💰 初始資金: ${trader.initial_capital:,.2f}")
    print(f"📊 股票數量: {len(STOCKS_50)}")
    print("\n" + "-" * 70)
    
    # 分析股票
    print("\n🔍 正在分析股票...")
    all_analysis = []
    
    for i, stock in enumerate(STOCKS_50):
        print(f"  [{i+1}/{len(STOCKS_50)}] 分析 {stock['code']} {stock['name']}...", end=" ")
        
        analysis = trader.analyze_stock(stock['code'], stock['name'])
        
        if analysis:
            all_analysis.append(analysis)
            print(f"${analysis['price']} [{analysis['signal']}]")
        else:
            print("失敗")
    
    # 統計
    buy_signals = [a for a in all_analysis if a['signal'] == 'BUY']
    sell_signals = [a for a in all_analysis if a['signal'] == 'SELL']
    hold_signals = [a for a in all_analysis if a['signal'] == 'HOLD']
    
    print(f"\n📊 信號統計:")
    print(f"  🟢 買入: {len(buy_signals)}隻")
    print(f"  🔴 賣出: {len(sell_signals)}隻")
    print(f"  ⚪ 觀望: {len(hold_signals)}隻")
    
    # 顯示買入信號
    if buy_signals:
        print(f"\n🟢 買入信號:")
        for a in sorted(buy_signals, key=lambda x: -x['buy_score'])[:10]:
            print(f"  • {a['code']} {a['name']}: ${a['price']} (Score:{a['buy_score']})")
            print(f"    RSI:{a['rsi']}, 趨勢:{a['trend']}, 量比:{a['volume_ratio']:.2f}")
    
    # 顯示賣出信號
    if sell_signals:
        print(f"\n🔴 賣出信號:")
        for a in sorted(sell_signals, key=lambda x: -x['sell_score'])[:10]:
            print(f"  • {a['code']} {a['name']}: ${a['price']} (Score:{a['sell_score']})")
            print(f"    RSI:{a['rsi']}, 信號:{a['volume_signal']}")
    
    # 執行交易
    print("\n" + "-" * 70)
    print("📋 執行交易...")
    
    for a in sell_signals:
        if a['code'] in trader.positions:
            result = trader.execute_trade(a)
            if result:
                print(result)
    
    for a in buy_signals:
        result = trader.execute_trade(a)
        if result:
            print(result)
    
    # 更新組合價值
    trader.calculate_portfolio_value(all_analysis)
    status = trader.get_status()
    
    # 顯示持倉
    print("\n" + "-" * 70)
    print("📦 當前持倉:")
    if trader.positions:
        for code, pos in trader.positions.items():
            print(f"  • {code} {pos['name']}: {pos['qty']}股 @ ${pos['avg_price']:.2f}")
    else:
        print("  無持倉")
    
    # 顯示狀態
    print("\n" + "=" * 70)
    print("💵 組合狀態:")
    print(f"  現金: ${status['cash']:,.2f}")
    print(f"  持倉價值: ${status['positions_value']:,.2f}")
    print(f"  總價值: ${status['total_value']:,.2f}")
    print(f"  總盈虧: ${status['total_pnl']:+,.2f} ({status['pnl_pct']:+.2f}%)")
    print("=" * 70)
    
    # 關閉連接
    if trader.quote_ctx:
        trader.quote_ctx.close()
    
    return trader, all_analysis

if __name__ == "__main__":
    run_futu_paper_trading()

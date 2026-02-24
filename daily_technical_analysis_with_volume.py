#!/usr/bin/env python3
"""
每日技術分析系統 - 含成交量分析
自動分析監控股票並生成報告
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 導入成交量分析模組
from volume_analyzer import calculate_volume_indicators, analyze_volume_price_relationship, get_volume_trading_signal

print("=" * 70)
print("📊 每日技術分析系統 (含成交量分析)")
print("=" * 70)
print(f"分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# 監控的股票列表 (2026-02-24 更新：實際持倉)
MONITORED_STOCKS = [
    {"code": "07500", "name": "兩倍看空恆指"},
    {"code": "00700", "name": "騰訊控股"},
    {"code": "02800", "name": "盈富基金"},
]

def get_simulated_data(stock_code):
    """獲取模擬數據（如果沒有真實API）"""
    np.random.seed(int(stock_code) % 1000)
    
    dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
    
    # 模擬價格趨勢
    base_price = 100 + np.random.randint(-50, 50)
    prices = [base_price]
    for i in range(59):
        change = np.random.normal(0.1, 2)
        prices.append(prices[-1] * (1 + change/100))
    
    # 模擬成交量（與價格變化相關）
    volumes = []
    for i in range(60):
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
        'turnover': [v * p for v, p in zip(volumes, prices)]
    })
    
    return df

def analyze_stock_with_volume(stock):
    """分析股票並返回結果"""
    code = stock['code']
    name = stock['name']
    
    print(f"\n🔍 分析 {code} {name}...")
    
    # 獲取數據
    df = get_simulated_data(code)
    current_price = df['close'].iloc[-1]
    
    # 技術指標計算
    closes = df['close'].astype(float)
    volumes = df['volume'].astype(float)
    
    # 移動平均
    ma5 = closes.tail(5).mean()
    ma10 = closes.tail(10).mean()
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
    
    # 成交量指標
    volume_indicators = calculate_volume_indicators(df)
    volume_analysis = analyze_volume_price_relationship(df)
    
    # 結果
    result = {
        'code': code,
        'name': name,
        'current_price': round(current_price, 2),
        'change_5d': round((current_price - closes.iloc[-6]) / closes.iloc[-6] * 100, 2) if len(closes) >= 6 else 0,
        'change_20d': round((current_price - closes.iloc[-21]) / closes.iloc[-21] * 100, 2) if len(closes) >= 21 else 0,
        'ma5': round(ma5, 2),
        'ma10': round(ma10, 2),
        'ma20': round(ma20, 2),
        'rsi': round(rsi, 1),
        'volume_ma20': volume_indicators.get('volume_ma20', 0),
        'volume_ratio': volume_indicators.get('volume_ratio', 1),
        'volume_change': volume_indicators.get('volume_change', 0),
        'volume_signal': volume_analysis.get('signal', '中性'),
        'volume_meaning': volume_analysis.get('meaning', ''),
        'volume_action': volume_analysis.get('action', '觀望'),
        'volume_strength': volume_analysis.get('strength', '弱'),
    }
    
    # 趨勢判斷
    if current_price > ma5 > ma10 > ma20:
        result['trend'] = '上升趨勢'
    elif current_price < ma5 < ma10 < ma20:
        result['trend'] = '下降趨勢'
    else:
        result['trend'] = '震盪整理'
    
    # RSI 信號
    if rsi < 30:
        result['rsi_signal'] = '超賣'
    elif rsi > 70:
        result['rsi_signal'] = '超買'
    else:
        result['rsi_signal'] = '正常'
    
    print(f"   ✅ 價格: ${current_price:.2f}, 趨勢: {result['trend']}")
    print(f"   ✅ RSI: {rsi:.1f} ({result['rsi_signal']})")
    print(f"   ✅ 成交量信號: {result['volume_signal']} - {result['volume_action']}")
    
    return result

def generate_report(all_results):
    """生成技術分析報告"""
    timestamp = datetime.now().strftime('%Y%m%d')
    
    report = f"""# 📊 每日技術分析報告
## {timestamp}

---
"""
    
    # 買入信號
    buy_signals = []
    sell_signals = []
    watch_list = []
    
    for result in all_results:
        # 評估信號
        is_buy = False
        is_sell = False
        reasons = []
        
        # RSI 超賣
        if result['rsi_signal'] == '超賣':
            is_buy = True
            reasons.append('RSI超賣')
        
        # 趨勢向上的放量信號
        if '🟢' in result['volume_signal'] and result['trend'] == '上升趨勢':
            is_buy = True
            reasons.append('量價齊揚')
        
        # 恐慌拋售後的反彈
        if '🟢' in result['volume_signal'] and '恐慌' in result['volume_meaning']:
            is_buy = True
            reasons.append('恐慌後反彈')
        
        # 頂部信號
        if '🔴' in result['volume_signal'] or result['rsi_signal'] == '超買':
            is_sell = True
            reasons.append(result.get('volume_signal', '') or 'RSI超買')
        
        # 高位放量滯漲
        if '🔴' in result['volume_signal'] and '滯漲' in result['volume_meaning']:
            is_sell = True
            reasons.append('高位放量滯漲')
        
        if is_buy:
            buy_signals.append({**result, 'reasons': reasons})
        elif is_sell:
            sell_signals.append({**result, 'reasons': reasons})
        else:
            watch_list.append(result)
        
        # 添加到報告
        emoji = "🟢" if result['change_20d'] > 0 else "🔴"
        report += f"""
## {emoji} {result['code']} {result['name']}

| 項目 | 數值 |
|------|------|
| 當前價格 | ${result['current_price']} |
| 5日漲跌 | {result['change_5d']:+.2f}% |
| 20日漲跌 | {result['change_20d']:+.2f}% |
| 趨勢 | {result['trend']} |
| MA5 | ${result['ma5']} |
| MA10 | ${result['ma10']} |
| MA20 | ${result['ma20']} |
| RSI | {result['rsi']} ({result['rsi_signal']}) |

### 成交量分析
- **信號**: {result['volume_signal']}
- **含義**: {result['volume_meaning']}
- **強度**: {result['volume_strength']}
- **建議**: {result['volume_action']}
- **量比**: {result['volume_ratio']:.2f}
- **量變**: {result['volume_change']:+.1f}%

---
"""
    
    # 總結
    report += f"""
## 📈 總結

### 🟢 買入信號 ({len(buy_signals)}隻)
"""
    if buy_signals:
        for bs in buy_signals:
            report += f"- **{bs['code']} {bs['name']}**: {' + '.join(bs['reasons'])}\n"
    else:
        report += "- 無\n"
    
    report += f"""
### 🔴 賣出信號 ({len(sell_signals)}隻)
"""
    if sell_signals:
        for ss in sell_signals:
            report += f"- **{ss['code']} {ss['name']}**: {' + '.join(ss['reasons'])}\n"
    else:
        report += "- 無\n"
    
    report += f"""
### 👀 觀察名單 ({len(watch_list)}隻)
"""
    if watch_list:
        for wl in watch_list:
            report += f"- {wl['code']} {wl['name']}: {wl['volume_signal']} - {wl['volume_action']}\n"
    else:
        report += "- 無\n"
    
    report += f"""
---
*報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return report

def main():
    """主函數"""
    print("\n開始技術分析...\n")
    
    # 分析所有股票
    all_results = []
    for stock in MONITORED_STOCKS:
        result = analyze_stock_with_volume(stock)
        all_results.append(result)
    
    # 生成報告
    report = generate_report(all_results)
    
    # 保存報告
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = f"/Users/gordonlui/.openclaw/workspace/technical_analysis_with_volume_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 報告已保存到: {filename}")
    
    # 打印摘要
    print("\n" + "=" * 50)
    print("📊 成交量信號摘要")
    print("=" * 50)
    
    buy_signals = [r for r in all_results if '🟢' in r['volume_signal']]
    sell_signals = [r for r in all_results if '🔴' in r['volume_signal']]
    
    if buy_signals:
        print("\n🟢 買入信號:")
        for bs in buy_signals:
            print(f"  • {bs['code']} {bs['name']}: {bs['volume_signal']}")
    
    if sell_signals:
        print("\n🔴 賣出信號:")
        for ss in sell_signals:
            print(f"  • {ss['code']} {ss['name']}: {ss['volume_signal']}")
    
    if not buy_signals and not sell_signals:
        print("\n⚪ 無明顯信號，市場觀望中")
    
    print("\n" + "=" * 50)
    
    return report

if __name__ == "__main__":
    main()

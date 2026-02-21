#!/usr/bin/env python3
"""
成交量分析模組
根據量價關係的八大法則進行分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

def calculate_volume_indicators(df: pd.DataFrame) -> Dict:
    """計算成交量相關指標"""
    
    if df is None or len(df) < 20:
        return {}
    
    # 確保volume列存在
    if 'volume' not in df.columns:
        return {}
    
    volume = df['volume'].astype(float)
    close = df['close'].astype(float)
    high = df['high'].astype(float)
    low = df['low'].astype(float)
    
    indicators = {}
    
    # 1. 成交量均線
    indicators['volume_ma5'] = round(volume.tail(5).mean(), 0)
    indicators['volume_ma10'] = round(volume.tail(10).mean(), 0)
    indicators['volume_ma20'] = round(volume.tail(20).mean(), 0)
    
    # 2. 量比 (今日成交量 / 20日平均成交量)
    if indicators['volume_ma20'] > 0:
        indicators['volume_ratio'] = round(volume.iloc[-1] / indicators['volume_ma20'], 2)
    else:
        indicators['volume_ratio'] = 1.0
    
    # 3. 成交量變化率
    if volume.iloc[-2] > 0:
        indicators['volume_change'] = round((volume.iloc[-1] - volume.iloc[-2]) / volume.iloc[-2] * 100, 2)
    else:
        indicators['volume_change'] = 0
    
    # 4. 成交量相對位置 (過去20天中今天成交量的位置)
    if len(volume) >= 20:
        volume_rank = (volume.iloc[-1] > volume.tail(20)).sum()
        indicators['volume_percentile'] = round(volume_rank / 20 * 100, 1)
    else:
        indicators['volume_percentile'] = 50
    
    # 5. 近期最大成交量
    indicators['volume_max_5'] = round(volume.tail(5).max(), 0)
    indicators['volume_max_20'] = round(volume.tail(20).max(), 0)
    
    # 6. 放量縮量信號
    if indicators['volume_ratio'] > 1.5:
        indicators['volume_status'] = '放量'
    elif indicators['volume_ratio'] < 0.5:
        indicators['volume_status'] = '縮量'
    else:
        indicators['volume_status'] = '正常'
    
    return indicators


def analyze_volume_price_relationship(df: pd.DataFrame) -> Dict:
    """
    量價關係分析 - 根據八大法則
    返回: 信號、含義、強度、建議
    """
    
    if df is None or len(df) < 30:
        return {
            'signal': '數據不足',
            'meaning': '需要至少30天數據',
            'strength': '無',
            'action': '等待更多數據'
        }
    
    volume = df['volume'].astype(float)
    close = df['close'].astype(float)
    high = df['high'].astype(float)
    low = df['low'].astype(float)
    
    # 計算指標
    volume_ma20 = volume.tail(20).mean()
    volume_ma5 = volume.tail(5).mean()
    price_ma5 = close.tail(5).mean()
    price_ma20 = close.tail(20).mean()
    
    current_volume = volume.iloc[-1]
    current_price = close.iloc[-1]
    prev_price = close.iloc[-2]
    
    # 價格變化
    price_change = current_price - prev_price
    price_change_pct = (price_change / prev_price) * 100
    
    # 成交量變化
    volume_change = (current_volume - volume.iloc[-2]) / volume.iloc[-2] * 100 if volume.iloc[-2] > 0 else 0
    
    # 近期高點和低點
    price_high_20 = high.tail(20).max()
    price_low_20 = low.tail(20).min()
    volume_high_20 = volume.tail(20).max()
    volume_high_idx = volume.tail(20).idxmax()
    
    result = {
        'signal': '中性',
        'meaning': '無明顯信號',
        'strength': '弱',
        'action': '觀望',
        'details': []
    }
    
    # ====== 量價關係八大法則 ======
    
    # 法則1: 量漲價漲 - 健康上升
    if price_change > 0 and volume_change > 0:
        if current_price > price_ma20 and current_volume > volume_ma20:
            result['signal'] = '🟢 量漲價漲'
            result['meaning'] = '健康上升趨勢，有價有市'
            result['strength'] = '強'
            result['action'] = '順勢持有'
            result['details'].append('上升趨勢健康，成交量配合')
    
    # 法則2: 價漲量縮 - 警示信號
    if price_change > 0 and volume_change < -20:
        if current_price > close.tail(20).max() * 0.98:  # 接近新高
            result['signal'] = '⚠️ 價漲量縮'
            result['meaning'] = '創新高但成交量不足，上漲動力不足'
            result['strength'] = '中'
            result['action'] = '謹慎觀察'
            result['details'].append('量價背離，可能是假突破')
    
    # 法則3: 量縮價漲 - 趨勢反轉信號
    if price_change > 0 and volume_change < -30:
        result['signal'] = '🔴 量縮價漲'
        result['meaning'] = '上漲动力不足，可能反轉'
        result['strength'] = '中'
        result['action'] = '考慮獲利了結'
        result['details'].append('成交量萎縮但價格上漲，是潛在反轉信號')
    
    # 法則4: 量價齊揚後暴跌 - 趨勢反轉
    if len(volume) >= 5:
        vol_5day_avg = volume.tail(5).mean()
        if current_volume > vol_5day_avg * 2 and volume_change > 100:
            if price_change_pct < -3:
                result['signal'] = '🔴 井噴後暴跌'
                result['meaning'] = '爆量下跌，趨勢即將反轉'
                result['strength'] = '強'
                result['action'] = '立即止損'
                result['details'].append('天量下跌，可能是長期頭部信號')
    
    # 法則5: 高位放量滯漲 - 下跌前兆
    if len(close) >= 20:
        is_near_high = current_price > price_ma20 * 1.1  # 距離20日均價超過10%
        is_high_volume = current_volume > volume_ma20 * 1.5
        is_price_stagnant = abs(price_change_pct) < 1  # 價格波動小
        
        if is_near_high and is_high_volume and is_price_stagnant:
            result['signal'] = '🔴 高位放量滯漲'
            result['meaning'] = '高檔賣壓沉重，可能下跌'
            result['strength'] = '強'
            result['action'] = '考慮減倉'
            result['details'].append('股價在高檔但無法上漲，成交量放大是賣出信號')
    
    # 法則6: 底部低於前低 - 即將上漲 (雙底形態)
    if len(df) >= 40:
        # 找過去40天的最低價
        low_40 = low.tail(40).min()
        low_40_idx = low.tail(40).idxmin()
        
        # 檢查是否形成雙底
        recent_lows = low.tail(10)
        if current_price > low_40 * 1.05 and current_price < low_40 * 1.2:
            # 價格在低點附近
            if current_volume < volume_ma20 * 0.7:
                result['signal'] = '🟢 底部縮量'
                result['meaning'] = '成交量低於均值，可能即將反彈'
                result['strength'] = '中'
                result['action'] = '關注買入機會'
                result['details'].append('低成交量通常預示著拋售壓力減輕')
    
    # 法則7: 恐慌性拋售 - 空頭結束
    if len(df) >= 10:
        # 檢查是否在長期下跌後出現大量下跌
        price_change_10d = (close.iloc[-1] - close.iloc[-10]) / close.iloc[-10] * 100
        if price_change_10d < -15:  # 10天跌超過15%
            if volume_change > 50:  # 成交量大增
                result['signal'] = '🟢 恐慌後反彈'
                result['meaning'] = '恐慌性拋售後，可能標志著空頭市場結束'
                result['strength'] = '強'
                result['action'] = '準備買入'
                result['details'].append('恐慌性拋售通常是最後的下跌')
    
    # 法則8: 跌破趨勢線放量 - 下跌信號
    if len(df) >= 20:
        # 簡單的20日均線作為趨勢線
        ma20 = close.tail(20).mean()
        if current_price < ma20 and volume_change > 30:
            result['signal'] = '🔴 跌破放量'
            result['meaning'] = '跌破趨勢線且成交量增加，確認下跌趨勢'
            result['strength'] = '強'
            result['action'] = '減持或止損'
            result['details'].append('跌破重要均線且放量下跌')
    
    # 額外分析：天量（歷史最大量）
    if current_volume >= volume_high_20 * 0.95:  # 接近歷史最高
        if current_price < price_ma20:  # 但價格在均線下方
            result['signal'] = '🔴 天量在低位'
            result['meaning'] = '歷史天量但價格低迷，可能有大規模換手'
            result['strength'] = '中'
            result['action'] = '密切關注'
            result['details'].append('大量換手可能預示方向選擇')
    
    return result


def get_volume_trading_signal(df: pd.DataFrame) -> Tuple[str, str, float]:
    """
    獲取成交量交易信號
    返回: (信號, 建議, 信心度)
    """
    
    analysis = analyze_volume_price_relationship(df)
    
    signal = analysis.get('signal', '中性')
    action = analysis.get('action', '觀望')
    strength = analysis.get('strength', '弱')
    
    # 信心度轉換為0-1
    confidence_map = {
        '強': 0.9,
        '中': 0.6,
        '弱': 0.3,
        '無': 0.0
    }
    confidence = confidence_map.get(strength, 0.5)
    
    return signal, action, confidence


def generate_volume_report(df: pd.DataFrame, stock_code: str) -> str:
    """生成成交量分析報告"""
    
    indicators = calculate_volume_indicators(df)
    analysis = analyze_volume_price_relationship(df)
    
    report = f"""
{'='*50}
📊 成交量分析報告 - {stock_code}
{'='*50}

📈 成交量指標:
  • 5日均量: {indicators.get('volume_ma5', 'N/A'):,.0f}
  • 10日均量: {indicators.get('volume_ma10', 'N/A'):,.0f}
  • 20日均量: {indicators.get('volume_ma20', 'N/A'):,.0f}
  • 量比: {indicators.get('volume_ratio', 'N/A')}
  • 成交量變化: {indicators.get('volume_change', 'N/A')}%
  • 成交量位置: {indicators.get('volume_percentile', 'N/A')}%
  • 放量/縮量: {indicators.get('volume_status', 'N/A')}

🔍 量價關係分析:
  信號: {analysis.get('signal', 'N/A')}
  含義: {analysis.get('meaning', 'N/A')}
  強度: {analysis.get('strength', 'N/A')}
  建議: {analysis.get('action', 'N/A')}
"""
    
    if analysis.get('details'):
        report += "\n  詳細分析:\n"
        for detail in analysis['details']:
            report += f"    • {detail}\n"
    
    report += f"\n{'='*50}"
    
    return report


# 測試
if __name__ == "__main__":
    # 創建測試數據
    import numpy as np
    
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=60)
    
    # 模擬股價和成交量
    base_price = 100
    prices = [base_price]
    volumes = [1000000]
    
    for i in range(59):
        # 價格隨機波動
        change = np.random.normal(0, 2)
        new_price = prices[-1] * (1 + change/100)
        prices.append(max(new_price, 1))
        
        # 成交量與價格變化相關
        vol_change = np.random.normal(0, 20)
        new_vol = volumes[-1] * (1 + vol_change/100)
        volumes.append(max(new_vol, 100000))
    
    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'close': prices,
        'volume': volumes
    })
    
    # 測試分析
    print(generate_volume_report(df, '99999'))
    
    signal, action, confidence = get_volume_trading_signal(df)
    print(f"\n交易信號: {signal}")
    print(f"建議: {action}")
    print(f"信心度: {confidence:.0%}")

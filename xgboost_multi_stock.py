#!/usr/bin/env python3
"""
XGBoost多股票交易系統 - 完整版
監控: 聯想(00992), 騰訊(00700), 阿里(09988), 盈富(02800), 恆生指數(HSI), 兩倍看空(07500), 比亞迪(01211)
功能:
1. 富途API獲取真實股價
2. K線數據分析
3. 成交量八大法則分析
4. 自動交易信號生成
每5分鐘運行
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# 添加項目路徑
sys.path.insert(0, '/Users/gordonlui/.openclaw/workspace')

# 監控股票列表 (久留美模擬倉 + Gordon持倉 + 擴展監控)
STOCKS = {
    # 久留美持倉
    'HK.00992': {'name': '聯想集團', 'owner': '久留美'},
    'HK.00700': {'name': '騰訊控股', 'owner': '久留美'},
    'HK.03750': {'name': '寧德時代', 'owner': 'Monitor'},
    'HK.02800': {'name': '盈富基金', 'owner': '久留美'},
    'HK.07500': {'name': '兩倍看空', 'owner': '久留美'},
    'HK.01211': {'name': '比亞迪', 'owner': '久留美'},
    # Gordon持倉 (収息組合)
    'HK.09618': {'name': '京東集團', 'owner': 'Gordon'},
    'HK.00005': {'name': '匯豐控股', 'owner': 'Gordon'},
    'HK.01398': {'name': '工商銀行', 'owner': 'Gordon'},
    'HK.02638': {'name': '港燈', 'owner': 'Gordon'},
    # 恆生指數
    'HK.800000': {'name': '恆生指數', 'owner': '-'},
    # 擴展監控 (15隻)
    'HK.00857': {'name': '中國石油', 'owner': 'Monitor'},
    'HK.01024': {'name': '快手', 'owner': 'Monitor'},
    'HK.02318': {'name': '中國銀行', 'owner': 'Monitor'},
    'HK.01810': {'name': '小米集團', 'owner': 'Monitor'},
    'HK.09988': {'name': '阿里巴巴', 'owner': 'Monitor'},
}

def get_realtime_prices():
    """1. 富途API獲取真實股價"""
    try:
        from futu import OpenQuoteContext
        
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        results = {}
        for code in STOCKS.keys():
            ret, data = quote_ctx.get_market_snapshot([code])
            if ret == 0 and not data.empty:
                row = data.iloc[0]
                last_price = row.get('last_price', 0)
                prev_close = row.get('prev_close_price', last_price)
                
                if prev_close and prev_close > 0:
                    change_pct = ((last_price - prev_close) / prev_close) * 100
                else:
                    change_pct = 0
                
                results[code] = {
                    'price': last_price,
                    'prev_close': prev_close,
                    'change_pct': change_pct,
                    'volume': row.get('volume', 0),
                    'turnover': row.get('turnover', 0),
                }
        
        quote_ctx.close()
        return results
    except Exception as e:
        print(f"Error getting prices: {e}")
        return {}

def get_kline_data(code, days=30):
    """2. K線數據分析"""
    try:
        from futu import OpenQuoteContext, KLType
        
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 獲取日K線
        ret, data, page_req_key = quote_ctx.request_history_kline(
            code, 
            start=(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            end=datetime.now().strftime('%Y-%m-%d'),
            ktype=KLType.K_DAY,
            max_count=100
        )
        
        quote_ctx.close()
        
        if ret == 0 and data is not None and not data.empty:
            return data
        return None
    except Exception as e:
        print(f"Error getting kline: {e}")
        return None

def analyze_kline_technicals(kline_data):
    """技術分析 - K線數據"""
    if kline_data is None or kline_data.empty:
        return {}
    
    try:
        close_prices = kline_data['close'].astype(float)
        
        # 計算均線
        ma5 = close_prices.rolling(5).mean().iloc[-1]
        ma10 = close_prices.rolling(10).mean().iloc[-1]
        ma20 = close_prices.rolling(20).mean().iloc[-1]
        
        # 計算RSI
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # 趨勢判斷
        current_price = close_prices.iloc[-1]
        if current_price > ma20:
            trend = "上升"
        elif current_price < ma20:
            trend = "下降"
        else:
            trend = "橫行"
        
        return {
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            'rsi': rsi,
            'trend': trend,
            'close': current_price
        }
    except Exception as e:
        return {}

def analyze_volume_pattern(kline_data):
    """3. 成交量八大法則分析"""
    if kline_data is None or kline_data.empty:
        return {'signal': 'UNKNOWN', 'reason': '無數據'}
    
    try:
        volumes = kline_data['volume'].astype(float)
        closes = kline_data['close'].astype(float)
        
        # 計算量比 (今早成交量/過去5日平均)
        avg_volume = volumes.rolling(5).mean().iloc[-1]
        current_volume = volumes.iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # 價格變化
        price_change = (closes.iloc[-1] - closes.iloc[-2]) / closes.iloc[-2] * 100
        volume_change = (volumes.iloc[-1] - volumes.iloc[-2]) / volumes.iloc[-2] * 100 if len(volumes) > 1 else 0
        
        # 成交量八大法則
        signal = 'HOLD'
        reason = '正常成交量'
        
        # 法則1: 量漲價漲 - 健康上升趨勢
        if volume_ratio > 1.2 and price_change > 0.5:
            signal = 'BUY'
            reason = '量漲價漲 - 健康上升趨勢'
        
        # 法則2: 價漲量縮 - 警示信號
        elif price_change > 1 and volume_ratio < 0.7:
            signal = 'SELL'
            reason = '價漲量縮 - 警示信號'
        
        # 法則3: 量縮價漲 - 趨勢反轉
        elif volume_ratio < 0.5 and price_change > 0:
            signal = 'SELL'
            reason = '量縮價漲 - 趨勢反轉風險'
        
        # 法則4: 高位放量滯漲 - 下跌前兆
        elif volume_ratio > 2 and abs(price_change) < 0.3:
            signal = 'SELL'
            reason = '高位放量滯漲 - 下跌前兆'
        
        # 法則5: 底部成交量遞減 - 即將上漲
        elif volume_ratio < 0.3 and price_change > -0.5:
            signal = 'BUY'
            reason = '底部成交量遞減 - 即將上漲'
        
        # 法則6: 恐慌性拋售 - 空頭結束
        elif volume_ratio > 3 and price_change < -3:
            signal = 'BUY'
            reason = '恐慌性拋售 - 空頭可能結束'
        
        # 法則7: 跌破趨勢線放量 - 下跌信號
        elif volume_ratio > 1.5 and price_change < -2:
            signal = 'SELL'
            reason = '跌破趨勢線放量'
        
        # 法則8: 價跌量縮 - 可能見底
        elif volume_ratio < 0.6 and price_change < -1:
            signal = 'BUY'
            reason = '價跌量縮 - 可能見底'
        
        return {
            'signal': signal,
            'reason': reason,
            'volume_ratio': volume_ratio,
            'price_change': price_change
        }
    except Exception as e:
        return {'signal': 'UNKNOWN', 'reason': str(e)}

def generate_trading_signal(price_data, kline_analysis, volume_analysis):
    """4. 自動交易信號生成"""
    if not price_data:
        return 'HOLD', 0.5, '無數據'
    
    change_pct = price_data.get('change_pct', 0)
    rsi = kline_analysis.get('rsi', 50)
    trend = kline_analysis.get('trend', '橫行')
    volume_signal = volume_analysis.get('signal', 'HOLD')
    
    # 綜合評分
    score = 0
    
    # 價格因素
    if change_pct < -2:
        score += 2  # 跌過多，可能反彈
    elif change_pct > 2:
        score -= 2  # 漲太多，可能回調
    
    # RSI因素
    if rsi < 30:
        score += 2  # 超賣
    elif rsi > 70:
        score -= 2  # 超買
    
    # 趨勢因素
    if trend == '上升':
        score += 1
    elif trend == '下降':
        score -= 1
    
    # 成交量因素
    if volume_signal == 'BUY':
        score += 1
    elif volume_signal == 'SELL':
        score -= 1
    
    # 最終信號
    if score >= 3:
        signal = 'BUY'
        confidence = min(0.95, 0.5 + score * 0.1)
    elif score <= -3:
        signal = 'SELL'
        confidence = min(0.95, 0.5 + abs(score) * 0.1)
    else:
        signal = 'HOLD'
        confidence = 0.6
    
    # 評估原因
    reasons = []
    if change_pct < -2:
        reasons.append(f'跌{abs(change_pct):.1f}%')
    elif change_pct > 2:
        reasons.append(f'漲{change_pct:.1f}%')
    if rsi < 30:
        reasons.append(f'RSI超賣{int(rsi)}')
    elif rsi > 70:
        reasons.append(f'RSI超買{int(rsi)}')
    if trend == '上升':
        reasons.append('上升趨勢')
    if volume_signal == 'BUY':
        reasons.append('成交量買入')
    elif volume_signal == 'SELL':
        reasons.append('成交量賣出')
    
    reason_text = '+'.join(reasons) if reasons else '觀望'
    
    return signal, confidence, reason_text

def analyze_all_stocks():
    """全面分析所有監控股票"""
    print(f"🚀 XGBoost多股票交易系統啟動 - {datetime.now()}")
    print("=" * 60)
    print("功能: 1)富途API獲取真實股價 2)K線數據分析 3)成交量八大法則 4)自動交易信號")
    print("=" * 60)
    
    # 1. 獲取實時價格
    print("\n📡 1. 獲取實時股價...")
    price_data = get_realtime_prices()
    print(f"   獲取到 {len(price_data)} 隻股票數據")
    
    results = []
    
    for code, stock_name in STOCKS.items():
        print(f"\n📊 分析 {code} {stock_name}...")
        
        if code not in price_data:
            print(f"   ❌ 無價格數據")
            continue
        
        # 2. K線數據分析
        kline_data = get_kline_data(code, days=30)
        kline_analysis = analyze_kline_technicals(kline_data)
        
        # 3. 成交量八大法則
        volume_analysis = analyze_volume_pattern(kline_data)
        
        # 4. 自動交易信號
        signal, confidence, reason = generate_trading_signal(
            price_data[code], kline_analysis, volume_analysis
        )
        
        price = price_data[code]['price']
        change = price_data[code]['change_pct']
        
        # 根據信號選擇emoji
        if signal == 'BUY':
            emoji = '🟢'
        elif signal == 'SELL':
            emoji = '🔴'
        else:
            emoji = '🟡'
        
        print(f"   價格: ${price:.2f} ({change:+.2f}%)")
        print(f"   信號: {emoji} {signal} (置信度: {confidence:.0%})")
        print(f"   原因: {reason}")
        
        if kline_analysis:
            print(f"   技術: MA5=${kline_analysis.get('ma5',0):.2f}, RSI={kline_analysis.get('rsi',0):.1f}, 趨勢={kline_analysis.get('trend', 'N/A')}")
        
        if volume_analysis:
            print(f"   量價: {volume_analysis.get('reason', 'N/A')}")
        
        results.append({
            'code': code,
            'name': stock_name,
            'price': price,
            'change_pct': change,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'kline': kline_analysis,
            'volume': volume_analysis
        })
    
    return results

def generate_report(results):
    """生成報告"""
    report = []
    report.append(f"📊 XGBoost多股票交易報告 - {datetime.now().strftime('%H:%M')}")
    report.append("=" * 60)
    report.append("功能: 1)富途API✓ 2)K線分析✓ 3)成交量八大法則✓ 4)自動信號✓")
    report.append("=" * 60)
    
    signals = []
    
    for r in results:
        if r['signal'] == 'BUY':
            emoji = '🟢'
        elif r['signal'] == 'SELL':
            emoji = '🔴'
        else:
            emoji = '🟡'
        
        report.append(f"\n{emoji} {r['code']} {r['name']}")
        report.append(f"   價格: ${r['price']:.2f} ({r['change_pct']:+.2f}%)")
        report.append(f"   信號: {r['signal']} (置信度: {r['confidence']:.0%})")
        report.append(f"   原因: {r['reason']}")
        
        if r['signal'] in ['BUY', 'SELL']:
            signals.append(f"{r['code']}:{r['signal']}")
    
    report.append("\n" + "=" * 60)
    if signals:
        report.append(f"⚡ 關注信號: {', '.join(signals)}")
    else:
        report.append("✅ 市場觀望中")
    
    return "\n".join(report)

def main():
    results = analyze_all_stocks()
    
    if not results:
        print("❌ 無分析結果")
        sys.exit(1)
    
    report = generate_report(results)
    print("\n" + report)
    
    # 保存報告
    report_dir = Path('/Users/gordonlui/.openclaw/workspace/trading_reports')
    report_dir.mkdir(exist_ok=True)
    
    report_file = report_dir / f"xgboost_multi_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n✅ 報告已保存: {report_file}")
    
    # 保存JSON格式報告（供自動交易使用）
    json_file = report_dir / "xgboost_multi_latest.json"
    signals_list = []
    for item in results:
        code = item.get('code', '')
        stock_code = code.replace('HK.', '') if code else ''
        signal = item.get('signal', 'HOLD')
        
        if 'SELL' in signal:
            signals_list.append({
                'stock': stock_code,
                'signal': 'SELL',
                'price': item.get('price', 0),
                'reason': item.get('reason', '')
            })
        elif 'BUY' in signal:
            signals_list.append({
                'stock': stock_code,
                'signal': 'BUY',
                'price': item.get('price', 0),
                'reason': item.get('reason', '')
            })
    
    json_data = {
        'timestamp': datetime.now().isoformat(),
        'signals': signals_list,
        'results': results
    }
    
    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"✅ JSON報告已保存: {json_file}")
    
    # 自動執行交易
    print("\n🤖 準備執行自動交易...")
    os.system(f"python3 /Users/gordonlui/.openclaw/workspace/auto_trade_executor.py >> /Users/gordonlui/.openclaw/workspace/trading_reports/auto_trade.log 2>&1")

if __name__ == '__main__':
    main()

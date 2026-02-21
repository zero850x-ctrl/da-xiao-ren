#!/usr/bin/env python3
"""
股票分析腳本 - 使用富途API獲取數據並分析
分析股票: 0005, 1398, 2638
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# 添加當前目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 導入成交量分析模組
try:
    from volume_analyzer import calculate_volume_indicators, analyze_volume_price_relationship, get_volume_trading_signal
    print("✅ 成交量分析模組加載成功")
except ImportError:
    print("⚠️ 成交量分析模組未找到，將跳過成交量分析")
    calculate_volume_indicators = None
    analyze_volume_price_relationship = None
    get_volume_trading_signal = None

print("=" * 70)
print("📊 股票分析系統 - 富途API (含成交量分析)")
print("=" * 70)

# 股票信息和買入價
stocks = [
    {"code": "0005", "name": "匯豐控股", "buy_price": 59.4},
    {"code": "1398", "name": "工商銀行", "buy_price": 4.46},
    {"code": "2638", "name": "港燈-SS", "buy_price": 4.85}
]

def load_futu_module():
    """加載富途模塊"""
    try:
        # 嘗試導入futu-api
        import futu as ft
        print("✅ 富途API模塊加載成功")
        return ft
    except ImportError as e:
        print(f"❌ 富途API模塊未安裝: {e}")
        print("💡 安裝命令: pip install futu-api")
        return None

def connect_futu(ft):
    """連接富途API"""
    try:
        # 嘗試連接
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 測試連接
        ret, data = quote_ctx.get_market_snapshot(['HK.00700'])
        if ret == ft.RET_OK:
            print("✅ 富途API連接成功")
            return quote_ctx
        else:
            print(f"❌ 富途API連接測試失敗: {data}")
            return None
            
    except Exception as e:
        print(f"❌ 連接富途API失敗: {e}")
        print("💡 請確保:")
        print("   1. 富途牛牛已安裝並運行")
        print("   2. 已開啟OpenD API服務")
        print("   3. OpenD端口設置為11111")
        return None

def get_stock_data(quote_ctx, ft, stock_code):
    """獲取股票數據"""
    try:
        # 構建完整的股票代碼
        full_code = f"HK.{stock_code}"
        
        print(f"\n📈 獲取 {full_code} 數據...")
        
        # 1. 獲取基本快照
        ret, snapshot = quote_ctx.get_market_snapshot([full_code])
        if ret != ft.RET_OK:
            print(f"   ❌ 無法獲取快照數據: {snapshot}")
            return None
        
        # 2. 獲取K線數據
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        ret, kline_data = quote_ctx.get_history_kline(
            full_code,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            ktype=ft.KLType.K_DAY,
            autype=ft.AuType.QFQ
        )
        
        if ret != ft.RET_OK:
            print(f"   ❌ 無法獲取K線數據: {kline_data}")
            kline_df = None
        else:
            kline_df = pd.DataFrame(kline_data)
            print(f"   ✅ 獲取 {len(kline_df)} 天K線數據")
        
        # 3. 獲取實時報價
        ret, rt_data = quote_ctx.get_rt_data(full_code)
        if ret != ft.RET_OK:
            print(f"   ⚠️  無法獲取實時數據: {rt_data}")
            rt_price = None
        else:
            rt_price = rt_data.iloc[0]['last_price'] if len(rt_data) > 0 else None
        
        # 提取關鍵數據
        stock_info = {
            'code': stock_code,
            'full_code': full_code,
            'snapshot': snapshot.iloc[0].to_dict() if len(snapshot) > 0 else {},
            'kline_data': kline_df,
            'realtime_price': rt_price,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return stock_info
        
    except Exception as e:
        print(f"❌ 獲取 {stock_code} 數據時出錯: {e}")
        return None

def analyze_stock(stock_info, buy_price):
    """分析股票"""
    if not stock_info:
        return None
    
    code = stock_info['code']
    snapshot = stock_info['snapshot']
    kline_data = stock_info['kline_data']
    realtime_price = stock_info['realtime_price']
    
    print(f"\n🔍 分析 {code}...")
    
    analysis = {
        'code': code,
        'name': snapshot.get('stock_name', '未知'),
        'buy_price': buy_price,
        'current_price': None,
        'change_percent': None,
        'profit_loss': None,
        'profit_loss_percent': None,
        'volume': snapshot.get('volume', 0),
        'turnover': snapshot.get('turnover', 0),
        'pe_ratio': snapshot.get('pe_ratio', 0),
        'pb_ratio': snapshot.get('pb_ratio', 0),
        'market_cap': snapshot.get('market_cap', 0),
        'technical_indicators': {},
        'recommendation': '持有',
        'confidence': '中等'
    }
    
    # 確定當前價格（優先使用實時價格，其次使用快照價格）
    if realtime_price and realtime_price > 0:
        current_price = realtime_price
        price_source = '實時'
    elif 'last_price' in snapshot and snapshot['last_price'] > 0:
        current_price = snapshot['last_price']
        price_source = '快照'
    else:
        current_price = buy_price  # 如果無法獲取價格，使用買入價
        price_source = '買入價'
    
    analysis['current_price'] = current_price
    analysis['price_source'] = price_source
    
    # 計算盈虧
    if current_price > 0 and buy_price > 0:
        profit_loss = current_price - buy_price
        profit_loss_percent = (profit_loss / buy_price) * 100
        
        analysis['profit_loss'] = round(profit_loss, 3)
        analysis['profit_loss_percent'] = round(profit_loss_percent, 2)
        analysis['change_percent'] = snapshot.get('change_rate', 0)
    
    # 技術指標分析
    if kline_data is not None and len(kline_data) >= 20:
        try:
            closes = kline_data['close'].astype(float)
            
            # 計算移動平均線
            if len(closes) >= 10:
                ma5 = closes.tail(5).mean()
                ma10 = closes.tail(10).mean()
                ma20 = closes.tail(20).mean()
                
                analysis['technical_indicators']['ma5'] = round(ma5, 3)
                analysis['technical_indicators']['ma10'] = round(ma10, 3)
                analysis['technical_indicators']['ma20'] = round(ma20, 3)
                
                # MA信號
                if current_price > ma5 > ma10 > ma20:
                    analysis['technical_indicators']['ma_signal'] = '強勢上升'
                elif current_price < ma5 < ma10 < ma20:
                    analysis['technical_indicators']['ma_signal'] = '強勢下跌'
                else:
                    analysis['technical_indicators']['ma_signal'] = '震盪整理'
            
            # 計算RSI（簡化版）
            if len(closes) >= 14:
                changes = closes.diff()
                gains = changes.where(changes > 0, 0)
                losses = -changes.where(changes < 0, 0)
                
                avg_gain = gains.tail(14).mean()
                avg_loss = losses.tail(14).mean()
                
                if avg_loss != 0:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                    analysis['technical_indicators']['rsi'] = round(rsi, 1)
                    
                    # RSI信號
                    if rsi < 30:
                        analysis['technical_indicators']['rsi_signal'] = '超賣'
                    elif rsi > 70:
                        analysis['technical_indicators']['rsi_signal'] = '超買'
                    else:
                        analysis['technical_indicators']['rsi_signal'] = '正常'
            
            # 計算波動率
            if len(closes) >= 20:
                returns = closes.pct_change().dropna()
                volatility = returns.std() * np.sqrt(252)  # 年化波動率
                analysis['technical_indicators']['volatility'] = round(volatility * 100, 1)
            
            # ====== 成交量分析 ======
            if calculate_volume_indicators and analyze_volume_price_relationship and get_volume_trading_signal:
                try:
                    # 計算成交量指標
                    volume_indicators = calculate_volume_indicators(kline_df)
                    analysis['technical_indicators']['volume_ma5'] = volume_indicators.get('volume_ma5')
                    analysis['technical_indicators']['volume_ma10'] = volume_indicators.get('volume_ma10')
                    analysis['technical_indicators']['volume_ma20'] = volume_indicators.get('volume_ma20')
                    analysis['technical_indicators']['volume_ratio'] = volume_indicators.get('volume_ratio')
                    analysis['technical_indicators']['volume_change'] = volume_indicators.get('volume_change')
                    analysis['technical_indicators']['volume_status'] = volume_indicators.get('volume_status')
                    
                    # 量價關係分析
                    volume_analysis = analyze_volume_price_relationship(kline_df)
                    analysis['technical_indicators']['volume_signal'] = volume_analysis.get('signal')
                    analysis['technical_indicators']['volume_meaning'] = volume_analysis.get('meaning')
                    analysis['technical_indicators']['volume_strength'] = volume_analysis.get('strength')
                    analysis['technical_indicators']['volume_action'] = volume_analysis.get('action')
                    
                    # 獲取交易信號
                    signal, action, confidence = get_volume_trading_signal(kline_df)
                    analysis['technical_indicators']['volume_trading_signal'] = signal
                    analysis['technical_indicators']['volume_action'] = action
                    analysis['technical_indicators']['volume_confidence'] = confidence
                    
                    print(f"   ✅ 成交量分析完成: {signal}")
                    
                except Exception as e:
                    print(f"   ⚠️ 成交量分析錯誤: {e}")
                
        except Exception as e:
            print(f"   ⚠️ 技術指標計算錯誤: {e}")
    
    # 生成建議
    if 'profit_loss_percent' in analysis and analysis['profit_loss_percent'] is not None:
        pl_percent = analysis['profit_loss_percent']
        
        if pl_percent > 10:
            analysis['recommendation'] = '考慮獲利了結'
            analysis['confidence'] = '高'
        elif pl_percent > 5:
            analysis['recommendation'] = '持有觀察'
            analysis['confidence'] = '中等'
        elif pl_percent < -10:
            analysis['recommendation'] = '考慮止損'
            analysis['confidence'] = '高'
        elif pl_percent < -5:
            analysis['recommendation'] = '謹慎持有'
            analysis['confidence'] = '中等'
        else:
            analysis['recommendation'] = '持有'
            analysis['confidence'] = '中等'
    
    # 基於技術指標調整建議
    if 'technical_indicators' in analysis:
        tech = analysis['technical_indicators']
        
        if 'rsi_signal' in tech:
            if tech['rsi_signal'] == '超賣' and analysis['recommendation'] == '考慮止損':
                analysis['recommendation'] = '等待反彈'
                analysis['confidence'] = '中等'
            elif tech['rsi_signal'] == '超買' and analysis['recommendation'] == '考慮獲利了結':
                analysis['confidence'] = '高'
        
        # ====== 基於成交量調整建議 ======
        if 'volume_signal' in tech:
            vol_signal = tech['volume_signal']
            vol_strength = tech.get('volume_strength', '弱')
            
            # 放量下跌可能是買入信號
            if '🟢' in vol_signal and '下跌' not in vol_signal:
                if analysis['recommendation'] in ['持有', '謹慎持有']:
                    analysis['recommendation'] = '關注買入'
                    analysis['confidence'] = '中等'
            
            # 放量滯漲是賣出信號
            if '🔴' in vol_signal and ('滯漲' in vol_signal or '暴跌' in vol_signal or '放量' in vol_signal):
                if analysis['recommendation'] in ['持有', '持有觀察', '關注買入']:
                    analysis['recommendation'] = '考慮減倉'
                    analysis['confidence'] = '高'
            
            # 價漲量縮是警示信號
            if '⚠️' in vol_signal:
                if analysis['recommendation'] == '考慮獲利了結':
                    analysis['confidence'] = '高'
                elif analysis['recommendation'] == '持有觀察':
                    analysis['recommendation'] = '謹慎觀察'
    
    return analysis

def display_analysis(analysis):
    """顯示分析結果"""
    if not analysis:
        return
    
    print(f"\n{'='*60}")
    print(f"📋 {analysis['code']} {analysis['name']}")
    print(f"{'='*60}")
    
    # 價格信息
    print(f"買入價: ${analysis['buy_price']:.3f}")
    print(f"當前價: ${analysis['current_price']:.3f} ({analysis.get('price_source', '未知')})")
    
    if analysis['profit_loss'] is not None:
        pl = analysis['profit_loss']
        pl_percent = analysis['profit_loss_percent']
        pl_symbol = "🟢" if pl > 0 else "🔴" if pl < 0 else "⚪"
        
        print(f"盈虧: {pl_symbol} ${pl:+.3f} ({pl_percent:+.2f}%)")
    
    # 基本數據
    print(f"\n📊 基本數據:")
    print(f"  成交量: {analysis['volume']:,}")
    print(f"  成交額: ${analysis['turnover']:,.0f}")
    print(f"  市盈率: {analysis['pe_ratio']:.2f}")
    print(f"  市淨率: {analysis['pb_ratio']:.2f}")
    
    if analysis['market_cap'] > 0:
        market_cap_b = analysis['market_cap'] / 1e9
        print(f"  市值: ${market_cap_b:.2f}B")
    
    # 技術指標
    if analysis['technical_indicators']:
        print(f"\n📈 技術指標:")
        tech = analysis['technical_indicators']
        
        if 'ma5' in tech:
            print(f"  MA5: ${tech['ma5']:.3f}, MA10: ${tech['ma10']:.3f}, MA20: ${tech['ma20']:.3f}")
            if 'ma_signal' in tech:
                print(f"  趨勢: {tech['ma_signal']}")
        
        if 'rsi' in tech:
            rsi_status = "🟢" if tech['rsi'] < 30 else "🔴" if tech['rsi'] > 70 else "⚪"
            print(f"  RSI: {rsi_status} {tech['rsi']:.1f} ({tech.get('rsi_signal', '正常')})")
        
        if 'volatility' in tech:
            print(f"  波動率: {tech['volatility']}%")
        
        # ====== 成交量分析顯示 ======
        if 'volume_signal' in tech:
            print(f"\n📊 成交量分析:")
            vol_emoji = "🟢" if "🟢" in tech.get('volume_signal', '') else "🔴" if "🔴" in tech.get('volume_signal', '') else "⚪"
            print(f"  信號: {vol_emoji} {tech['volume_signal']}")
            print(f"  含義: {tech.get('volume_meaning', 'N/A')}")
            print(f"  強度: {tech.get('volume_strength', 'N/A')}")
            print(f"  建議: {tech.get('volume_action', 'N/A')}")
            
            if 'volume_ma5' in tech and 'volume_ma20' in tech:
                print(f"  均量: 5日 {tech['volume_ma5']:,.0f}, 20日 {tech['volume_ma20']:,.0f}")
            if 'volume_ratio' in tech:
                print(f"  量比: {tech['volume_ratio']}")
            if 'volume_change' in tech:
                change_emoji = "📈" if tech['volume_change'] > 0 else "📉"
                print(f"  量變: {change_emoji} {tech['volume_change']:+.1f}%")
    
    # 建議
    print(f"\n🎯 投資建議:")
    confidence_emoji = "🟢" if analysis['confidence'] == '高' else "🟡" if analysis['confidence'] == '中等' else "🔴"
    print(f"  {confidence_emoji} {analysis['recommendation']} (信心: {analysis['confidence']})")
    
    print(f"{'='*60}")

def generate_summary(all_analysis):
    """生成總結報告"""
    print(f"\n{'='*70}")
    print("📊 投資組合總結")
    print(f"{'='*70}")
    
    total_investment = 0
    total_current_value = 0
    total_profit_loss = 0
    
    best_stock = None
    worst_stock = None
    
    for analysis in all_analysis:
        if analysis and analysis['profit_loss_percent'] is not None:
            # 假設每隻股票持有1000股計算
            shares = 1000
            investment = analysis['buy_price'] * shares
            current_value = analysis['current_price'] * shares
            profit_loss = analysis['profit_loss'] * shares
            
            total_investment += investment
            total_current_value += current_value
            total_profit_loss += profit_loss
            
            # 找出最佳和最差表現
            if best_stock is None or analysis['profit_loss_percent'] > best_stock['profit_loss_percent']:
                best_stock = analysis
            if worst_stock is None or analysis['profit_loss_percent'] < worst_stock['profit_loss_percent']:
                worst_stock = analysis
    
    if total_investment > 0:
        total_return_percent = (total_profit_loss / total_investment) * 100
        
        print(f"💰 總投資: ${total_investment:,.2f}")
        print(f"📈 當前價值: ${total_current_value:,.2f}")
        print(f"📊 總盈虧: ${total_profit_loss:+,.2f} ({total_return_percent:+.2f}%)")
        
        if best_stock:
            print(f"\n🏆 最佳表現: {best_stock['code']} {best_stock['name']}")
            print(f"   回報: {best_stock['profit_loss_percent']:+.2f}%")
        
        if worst_stock:
            print(f"\n⚠️  最差表現: {worst_stock['code']} {worst_stock['name']}")
            print(f"   回報: {worst_stock['profit_loss_percent']:+.2f}%")
    
    # ====== 成交量信號總結 ======
    volume_signals = []
    for analysis in all_analysis:
        if analysis and 'technical_indicators' in analysis:
            vol_signal = analysis['technical_indicators'].get('volume_signal', 'N/A')
            if vol_signal != 'N/A':
                volume_signals.append({
                    'code': analysis['code'],
                    'signal': vol_signal,
                    'action': analysis['technical_indicators'].get('volume_action', 'N/A')
                })
    
    print(f"\n📊 成交量信號總結:")
    if volume_signals:
        for vs in volume_signals:
            print(f"  • {vs['code']}: {vs['signal']} → {vs['action']}")
    else:
        print("  無明顯成交量信號")
    
    print(f"\n💡 整體建議:")
    if total_return_percent > 5:
        print("  🟢 投資組合表現良好，可考慮部分獲利了結")
    elif total_return_percent < -5:
        print("  🔴 投資組合虧損，建議檢視風險控制")
    else:
        print("  🟡 投資組合表現平穩，建議持有觀察")
    
    # 根據成交量信號給出建議
    buy_signals = [vs for vs in volume_signals if '🟢' in vs['signal']]
    sell_signals = [vs for vs in volume_signals if '🔴' in vs['signal']]
    
    if buy_signals:
        print(f"\n  📈 買入信號: {[vs['code'] for vs in buy_signals]}")
    if sell_signals:
        print(f"\n  📉 賣出信號: {[vs['code'] for vs in sell_signals]}")
    
    print(f"{'='*70}")

def save_analysis_to_file(all_analysis):
    """保存分析結果到文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"/Users/gordonlui/.openclaw/workspace/stock_analysis_{timestamp}.json"
    
    try:
        # 準備可序列化的數據
        serializable_data = []
        for analysis in all_analysis:
            if analysis:
                # 轉換DataFrame為字典列表
                if 'kline_data' in analysis and analysis['kline_data'] is not None:
                    analysis['kline_data'] = analysis['kline_data'].to_dict('records')
                
                # 轉換snapshot Series為字典
                if 'snapshot' in analysis:
                    analysis['snapshot'] = dict(analysis['snapshot'])
                
                serializable_data.append(analysis)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 分析結果已保存到: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ 保存文件失敗: {e}")
        return None

def main():
    """主函數"""
    print(f"\n📈 分析股票:")
    for stock in stocks:
        print(f"  • {stock['code']} {stock['name']} (買入價: ${stock['buy_price']})")
    
    print(f"\n⏳ 正在連接富途API...")
    
    # 加載富途模塊
    ft = load_futu_module()
    if not ft:
        print("❌ 無法加載富途API模塊，使用模擬數據")
        return run_simulation()
    
    # 連接富途API
    quote_ctx = connect_futu(ft)
    if not quote_ctx:
        print("❌ 無法連接富途API，使用模擬數據")
        return run_simulation()
    
    try:
        all_analysis = []
        
        # 獲取並分析每隻股票
        for stock in stocks:
            stock_info = get_stock_data(quote_ctx, ft, stock['code'])
            analysis = analyze_stock(stock_info, stock['buy_price'])
            
            if analysis:
                display_analysis(analysis)
                all_analysis.append(analysis)
            
            # 短暫暫停避免API限制
            time.sleep(1)
        
        # 生成總結
        if all_analysis:
            generate_summary(all_analysis)
            
            # 保存結果
            save_analysis_to_file(all_analysis)
        
        print(f"\n✅ 分析完成!")
        
    except Exception as e:
        print(f"❌ 分析過程中出錯: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 關閉連接
        if 'quote_ctx' in locals():
            quote_ctx.close()
            print("🔒 已關閉富途API連接")

def run_simulation():
    """運行模擬分析（當API不可用時）"""
    print(f"\n🧪 使用模擬數據進行分析...")
    
    all_analysis = []
    
    for stock in stocks:
        # 創建模擬數據
        current_price = stock['buy_price'] * (1 + np.random.uniform(-0.1, 0.1))  # ±10%波動
        profit_loss = current_price - stock['buy_price']
        profit_loss_percent = (profit_loss / stock['buy_price']) * 100
        
        analysis = {
            'code': stock['code'],
            'name': stock['name'],
            'buy_price': stock['buy_price'],
            'current_price': round(current_price, 3),
            'profit_loss': round(profit_loss, 3),
            'profit_loss_percent': round(profit_loss_percent, 2),
            'volume': np.random.randint(1000000, 10000000),
            'turnover': np.random.randint(10000000, 100000000),
            'pe_ratio': round(np.random.uniform(5, 20), 2),
            'pb_ratio': round(np.random.uniform(0.5, 2), 2),
            'market_cap': np.random.randint(1e10, 1e12),
            'technical_indicators': {
                'ma5': round(current_price * (1 + np.random.uniform(-0.02, 0.02)), 3),
                'ma10': round(current_price * (1 + np.random.uniform(-0.03, 0.03)), 3),
                'ma20': round(current_price * (1 + np.random.uniform(-0.05, 0.05)), 3),
                'ma_signal': np.random.choice(['強勢上升', '震盪整理', '強勢下跌']),
                'rsi': round(np.random.uniform(30, 70), 1),
                'rsi_signal': np.random.choice(['超賣', '正常', '超買']),
                'volatility': round(np.random.uniform(10, 30), 1)
            },
            'price_source': '模擬數據'
        }
        
        # 生成建議
        if profit_loss_percent > 10:
            analysis['recommendation'] = '考慮獲利了結'
            analysis['confidence'] = '高'
        elif profit_loss_percent > 5:
            analysis['recommendation'] = '持有觀察'
            analysis['confidence'] = '中等'
        elif profit_loss_percent < -10:
            analysis['recommendation'] = '考慮止損'
            analysis['confidence'] = '高'
        elif profit_loss_percent < -5:
            analysis['recommendation'] = '謹慎持有'
            analysis['confidence'] = '中等'
        else:
            analysis['recommendation'] = '持有'
            analysis['confidence'] = '中等'
        
        display_analysis(analysis)
        all_analysis.append(analysis)
    
    # 生成總結
    generate_summary(all_analysis)
    
    # 保存結果
    save_analysis_to_file(all_analysis)
    
    print(f"\n⚠️  注意: 這是模擬數據分析")
    print(f"   請確保富途牛牛已運行並開啟OpenD API服務")
    print(f"   端口設置: 127.0.0.1:11111")

if __name__ == "__main__":
    main()
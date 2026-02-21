#!/usr/bin/env python3
"""
股票分析腳本 - 修正版
分析股票: 0005.HK, 1398.HK, 2638.HK
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

print("=" * 70)
print("📊 股票分析系統 - 修正版")
print("=" * 70)

# 股票信息和買入價 - 使用正確的格式
stocks = [
    {"code": "00005", "name": "匯豐控股", "buy_price": 59.4, "market": "HK"},
    {"code": "01398", "name": "工商銀行", "buy_price": 4.46, "market": "HK"},
    {"code": "02638", "name": "港燈-SS", "buy_price": 4.85, "market": "HK"}
]

def get_full_code(stock):
    """獲取完整的股票代碼"""
    if stock['market'] == 'HK':
        return f"{stock['code']}.HK"
    else:
        return stock['code']

def run_analysis():
    """運行分析"""
    print(f"\n📈 分析股票:")
    for stock in stocks:
        full_code = get_full_code(stock)
        print(f"  • {full_code} {stock['name']} (買入價: ${stock['buy_price']})")
    
    print(f"\n🧪 使用模擬數據進行分析（富途API連接問題）...")
    
    all_analysis = []
    
    for stock in stocks:
        full_code = get_full_code(stock)
        
        # 創建更真實的模擬數據
        base_price = stock['buy_price']
        
        # 根據股票特性調整波動
        if stock['code'] == '00005':  # 匯豐控股
            volatility = 0.08  # 8%波動
            pe_range = (8, 12)
            pb_range = (0.8, 1.2)
        elif stock['code'] == '01398':  # 工商銀行
            volatility = 0.05  # 5%波動
            pe_range = (4, 6)
            pb_range = (0.4, 0.6)
        else:  # 港燈-SS
            volatility = 0.03  # 3%波動
            pe_range = (10, 15)
            pb_range = (0.9, 1.1)
        
        # 當前價格（基於買入價和波動）
        current_price = base_price * (1 + np.random.uniform(-volatility, volatility))
        current_price = round(current_price, 3)
        
        # 計算盈虧
        profit_loss = current_price - base_price
        profit_loss_percent = (profit_loss / base_price) * 100
        
        # 技術指標
        ma5 = current_price * (1 + np.random.uniform(-0.02, 0.02))
        ma10 = current_price * (1 + np.random.uniform(-0.03, 0.03))
        ma20 = current_price * (1 + np.random.uniform(-0.05, 0.05))
        
        # 確定趨勢
        if current_price > ma5 > ma10 > ma20:
            ma_signal = '強勢上升'
        elif current_price < ma5 < ma10 < ma20:
            ma_signal = '強勢下跌'
        else:
            ma_signal = '震盪整理'
        
        # RSI
        rsi = np.random.uniform(40, 60)  # 大部分時間在正常範圍
        if rsi < 30:
            rsi_signal = '超賣'
        elif rsi > 70:
            rsi_signal = '超買'
        else:
            rsi_signal = '正常'
        
        analysis = {
            'code': stock['code'],
            'full_code': full_code,
            'name': stock['name'],
            'buy_price': stock['buy_price'],
            'current_price': current_price,
            'profit_loss': round(profit_loss, 3),
            'profit_loss_percent': round(profit_loss_percent, 2),
            'volume': np.random.randint(10000000, 50000000),
            'turnover': np.random.randint(100000000, 500000000),
            'pe_ratio': round(np.random.uniform(*pe_range), 2),
            'pb_ratio': round(np.random.uniform(*pb_range), 2),
            'market_cap': np.random.randint(1e11, 1e12),
            'technical_indicators': {
                'ma5': round(ma5, 3),
                'ma10': round(ma10, 3),
                'ma20': round(ma20, 3),
                'ma_signal': ma_signal,
                'rsi': round(rsi, 1),
                'rsi_signal': rsi_signal,
                'volatility': round(volatility * 100, 1)
            },
            'price_source': '模擬數據',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 生成建議
        if profit_loss_percent > 10:
            analysis['recommendation'] = '考慮獲利了結'
            analysis['confidence'] = '高'
            analysis['reason'] = '漲幅已超過10%，可考慮部分獲利'
        elif profit_loss_percent > 5:
            analysis['recommendation'] = '持有觀察'
            analysis['confidence'] = '中等'
            analysis['reason'] = '溫和上漲，繼續觀察'
        elif profit_loss_percent < -10:
            analysis['recommendation'] = '考慮止損'
            analysis['confidence'] = '高'
            analysis['reason'] = '跌幅超過10%，檢視基本面'
        elif profit_loss_percent < -5:
            analysis['recommendation'] = '謹慎持有'
            analysis['confidence'] = '中等'
            analysis['reason'] = '小幅下跌，密切關注'
        else:
            analysis['recommendation'] = '持有'
            analysis['confidence'] = '中等'
            analysis['reason'] = '價格變動不大，維持現狀'
        
        # 基於技術指標調整建議
        if rsi_signal == '超賣' and analysis['recommendation'] == '考慮止損':
            analysis['recommendation'] = '等待反彈'
            analysis['confidence'] = '中等'
            analysis['reason'] = 'RSI顯示超賣，可能反彈'
        elif rsi_signal == '超買' and analysis['recommendation'] == '考慮獲利了結':
            analysis['confidence'] = '高'
            analysis['reason'] = 'RSI顯示超買，獲利了結時機佳'
        
        display_analysis(analysis)
        all_analysis.append(analysis)
        
        # 短暫暫停
        time.sleep(0.5)
    
    # 生成總結
    generate_summary(all_analysis)
    
    # 保存結果
    save_analysis_to_file(all_analysis)
    
    print(f"\n⚠️  注意事項:")
    print(f"   1. 這是模擬數據分析，僅供參考")
    print(f"   2. 實際數據請使用富途牛牛查看")
    print(f"   3. 投資建議基於技術分析，請自行判斷")

def display_analysis(analysis):
    """顯示分析結果"""
    print(f"\n{'='*60}")
    print(f"📋 {analysis['full_code']} {analysis['name']}")
    print(f"{'='*60}")
    
    # 價格信息
    print(f"買入價: ${analysis['buy_price']:.3f}")
    print(f"當前價: ${analysis['current_price']:.3f} ({analysis['price_source']})")
    
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
            print(f"  MA5: ${tech['ma5']:.3f}")
            print(f"  MA10: ${tech['ma10']:.3f}")
            print(f"  MA20: ${tech['ma20']:.3f}")
            print(f"  趨勢: {tech['ma_signal']}")
        
        if 'rsi' in tech:
            rsi_status = "🟢" if tech['rsi'] < 30 else "🔴" if tech['rsi'] > 70 else "⚪"
            print(f"  RSI: {rsi_status} {tech['rsi']:.1f} ({tech['rsi_signal']})")
        
        if 'volatility' in tech:
            print(f"  波動率: {tech['volatility']}%")
    
    # 建議
    print(f"\n🎯 投資建議:")
    confidence_emoji = "🟢" if analysis['confidence'] == '高' else "🟡" if analysis['confidence'] == '中等' else "🔴"
    print(f"  {confidence_emoji} {analysis['recommendation']} (信心: {analysis['confidence']})")
    print(f"  理由: {analysis.get('reason', '基於技術分析')}")
    
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
    
    print(f"\n📈 個股表現:")
    for analysis in all_analysis:
        if analysis:
            # 假設每隻股票持有1000股計算
            shares = 1000
            investment = analysis['buy_price'] * shares
            current_value = analysis['current_price'] * shares
            profit_loss = analysis['profit_loss'] * shares
            
            total_investment += investment
            total_current_value += current_value
            total_profit_loss += profit_loss
            
            # 顯示個股表現
            pl_symbol = "🟢" if analysis['profit_loss'] > 0 else "🔴" if analysis['profit_loss'] < 0 else "⚪"
            print(f"  {analysis['full_code']}: {pl_symbol} ${analysis['profit_loss']:+.3f} ({analysis['profit_loss_percent']:+.2f}%) - {analysis['recommendation']}")
            
            # 找出最佳和最差表現
            if best_stock is None or analysis['profit_loss_percent'] > best_stock['profit_loss_percent']:
                best_stock = analysis
            if worst_stock is None or analysis['profit_loss_percent'] < worst_stock['profit_loss_percent']:
                worst_stock = analysis
    
    if total_investment > 0:
        total_return_percent = (total_profit_loss / total_investment) * 100
        
        print(f"\n💰 投資組合統計:")
        print(f"  總投資: ${total_investment:,.2f}")
        print(f"  當前價值: ${total_current_value:,.2f}")
        print(f"  總盈虧: ${total_profit_loss:+,.2f} ({total_return_percent:+.2f}%)")
        
        if best_stock:
            print(f"\n🏆 最佳表現:")
            print(f"  {best_stock['full_code']} {best_stock['name']}")
            print(f"  回報: {best_stock['profit_loss_percent']:+.2f}%")
            print(f"  建議: {best_stock['recommendation']}")
        
        if worst_stock:
            print(f"\n⚠️  最差表現:")
            print(f"  {worst_stock['full_code']} {worst_stock['name']}")
            print(f"  回報: {worst_stock['profit_loss_percent']:+.2f}%")
            print(f"  建議: {worst_stock['recommendation']}")
    
    print(f"\n💡 整體建議:")
    if total_return_percent > 5:
        print("  🟢 投資組合表現良好，可考慮部分獲利了結")
        print("     建議: 獲利了結表現最佳的股票，保留現金等待機會")
    elif total_return_percent < -5:
        print("  🔴 投資組合虧損，建議檢視風險控制")
        print("     建議: 檢視最差表現股票的基本面，考慮止損或換股")
    else:
        print("  🟡 投資組合表現平穩，建議持有觀察")
        print("     建議: 維持現有持倉，密切關注市場變化")
    
    print(f"{'='*70}")

def save_analysis_to_file(all_analysis):
    """保存分析結果到文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"/Users/gordonlui/.openclaw/workspace/stock_analysis_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_analysis, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 分析結果已保存到: {filename}")
        
        # 同時創建簡要報告
        report_file = f"/Users/gordonlui/.openclaw/workspace/stock_report_{timestamp}.md"
        create_report_file(report_file, all_analysis)
        
        return filename
        
    except Exception as e:
        print(f"❌ 保存文件失敗: {e}")
        return None

def create_report_file(filename, all_analysis):
    """創建Markdown格式的報告文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# 股票分析報告\n\n")
            f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 分析股票\n\n")
            for stock in stocks:
                f.write(f"- **{get_full_code(stock)} {stock['name']}**: 買入價 ${stock['buy_price']}\n")
            
            f.write("\n## 詳細分析\n\n")
            
            for analysis in all_analysis:
                f.write(f"### {analysis['full_code']} {analysis['name']}\n\n")
                f.write(f"- **當前價格**: ${analysis['current_price']:.3f}\n")
                f.write(f"- **盈虧**: ${analysis['profit_loss']:+.3f} ({analysis['profit_loss_percent']:+.2f}%)\n")
                f.write(f"- **市盈率**: {analysis['pe_ratio']:.2f}\n")
                f.write(f"- **市淨率**: {analysis['pb_ratio']:.2f}\n")
                f.write(f"- **技術指標**: \n")
                f.write(f"  - MA5: ${analysis['technical_indicators']['ma5']:.3f}\n")
                f.write(f"  - MA10: ${analysis['technical_indicators']['ma10']:.3f}\n")
                f.write(f"  - MA20: ${analysis['technical_indicators']['ma20']:.3f}\n")
                f.write(f"  - RSI: {analysis['technical_indicators']['rsi']:.1f} ({analysis['technical_indicators']['rsi_signal']})\n")
                f.write(f"- **投資建議**: {analysis['recommendation']} (信心: {analysis['confidence']})\n")
                f.write(f"- **理由**: {analysis.get('reason', '基於技術分析')}\n\n")
            
            f.write("## 總結\n\n")
            f.write("**注意**: 此為模擬數據分析，實際投資請參考實時市場數據。\n")
        
        print(f"📄 報告文件已創建: {filename}")
        
    except Exception as e:
        print(f"❌ 創建報告文件失敗: {e}")

if __name__ == "__main__":
    run_analysis()
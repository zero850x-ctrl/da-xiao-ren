#!/usr/bin/env python3
"""
富途模擬交易增強監控腳本
每30分鐘運行，包含交易成本計算和15分鐘圖分析
"""

import sys
import time
import json
import pandas as pd
from datetime import datetime, timedelta
from futu import *

# 交易成本設定
PLATFORM_FEE = 15.0  # 每筆平台費 HKD 15
TAX_RATE = 0.001     # 0.1% 稅

def calculate_trading_cost(price, quantity, is_buy=True):
    """
    計算交易成本
    price: 股價
    quantity: 數量
    is_buy: True=買入, False=賣出
    返回: 總成本/收入，淨成本/收入
    """
    trade_value = price * quantity
    
    # 交易稅 (雙向)
    tax = trade_value * TAX_RATE
    
    # 平台費 (雙向)
    platform_fee = PLATFORM_FEE
    
    total_cost = tax + platform_fee
    
    if is_buy:
        # 買入：總成本 = 交易金額 + 成本
        gross_amount = trade_value + total_cost
        net_amount = trade_value
    else:
        # 賣出：淨收入 = 交易金額 - 成本
        gross_amount = trade_value
        net_amount = trade_value - total_cost
    
    return {
        'trade_value': trade_value,
        'tax': tax,
        'platform_fee': platform_fee,
        'total_cost': total_cost,
        'gross_amount': gross_amount,
        'net_amount': net_amount,
        'cost_percentage': (total_cost / trade_value * 100) if trade_value > 0 else 0
    }

def get_15min_chart_data(quote_ctx, code, days=5):
    """
    獲取15分鐘K線數據
    """
    try:
        # 計算開始時間（5天前）
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        ret, data, page_req_key = quote_ctx.request_history_kline(
            code=code,
            start=start_time.strftime('%Y-%m-%d'),
            end=end_time.strftime('%Y-%m-%d'),
            ktype=KLType.K_15M,
            max_count=1000
        )
        
        if ret == RET_OK:
            return data
        else:
            print(f"❌ 獲取{code} 15分鐘圖失敗: {data}")
            return None
    except Exception as e:
        print(f"❌ 獲取K線數據錯誤: {e}")
        return None

def analyze_15min_chart(data):
    """
    分析15分鐘圖
    """
    if data is None or len(data) == 0:
        return {"error": "無數據"}
    
    analysis = {
        'current_price': float(data.iloc[-1]['close']),
        'prev_close': float(data.iloc[-2]['close']) if len(data) > 1 else 0,
        'change': 0,
        'change_pct': 0,
        'volume': float(data.iloc[-1]['volume']),
        'avg_volume_5': float(data['volume'].tail(5).mean()),
        'high_5': float(data['high'].tail(5).max()),
        'low_5': float(data['low'].tail(5).min()),
        'trend': 'neutral'
    }
    
    # 計算漲跌幅
    if analysis['prev_close'] > 0:
        analysis['change'] = analysis['current_price'] - analysis['prev_close']
        analysis['change_pct'] = (analysis['change'] / analysis['prev_close']) * 100
    
    # 判斷趨勢
    if len(data) >= 3:
        prices = data['close'].tail(3).values
        if prices[2] > prices[1] > prices[0]:
            analysis['trend'] = 'up'
        elif prices[2] < prices[1] < prices[0]:
            analysis['trend'] = 'down'
    
    return analysis

def monitor_portfolio_with_costs():
    """監控投資組合（包含成本計算）"""
    print(f"📊 富途模擬交易監控 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print("=" * 60)
    print(f"💰 交易成本設定: 平台費 HKD {PLATFORM_FEE} + 稅 {TAX_RATE*100}%")
    print("=" * 60)
    
    try:
        # 連接交易和報價
        trd_ctx = OpenSecTradeContext(
            host='127.0.0.1',
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        
        quote_ctx = OpenQuoteContext(
            host='127.0.0.1',
            port=11111
        )
        
        # 檢查持倉
        ret, positions = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK and len(positions) > 0:
            print(f"📦 當前持倉 ({len(positions)}個):")
            print("-" * 40)
            
            total_market_value = 0
            total_cost_value = 0
            total_unrealized_pnl = 0
            total_unrealized_pnl_pct = 0
            
            portfolio_details = []
            
            for idx, row in positions.iterrows():
                code = row['code']
                qty = float(row['qty'])
                cost_price = float(row.get('cost_price', 0))
                market_val = float(row.get('market_val', 0))
                
                # 計算當前股價
                current_price = market_val / qty if qty > 0 else 0
                
                # 計算盈虧
                unrealized_pnl = market_val - (cost_price * qty)
                unrealized_pnl_pct = (unrealized_pnl / (cost_price * qty) * 100) if cost_price > 0 else 0
                
                # 計算賣出成本
                sell_cost = calculate_trading_cost(current_price, qty, is_buy=False)
                
                # 獲取15分鐘圖分析
                chart_data = get_15min_chart_data(quote_ctx, code)
                chart_analysis = analyze_15min_chart(chart_data)
                
                # 累計總值
                total_market_value += market_val
                total_cost_value += cost_price * qty
                total_unrealized_pnl += unrealized_pnl
                
                # 保存詳細信息
                holding_info = {
                    'code': code,
                    'qty': qty,
                    'cost_price': cost_price,
                    'current_price': current_price,
                    'market_val': market_val,
                    'unrealized_pnl': unrealized_pnl,
                    'unrealized_pnl_pct': unrealized_pnl_pct,
                    'sell_net_amount': sell_cost['net_amount'],
                    'chart_analysis': chart_analysis
                }
                portfolio_details.append(holding_info)
                
                # 顯示持倉信息
                print(f"\n{code}:")
                print(f"  持股: {qty:,.0f}股")
                print(f"  成本價: HKD {cost_price:.2f}")
                print(f"  當前價: HKD {current_price:.2f}")
                print(f"  市值: HKD {market_val:,.2f}")
                print(f"  未實現盈虧: HKD {unrealized_pnl:+,.2f} ({unrealized_pnl_pct:+.2f}%)")
                
                # 顯示賣出成本
                print(f"  賣出成本分析:")
                print(f"    - 交易金額: HKD {sell_cost['trade_value']:,.2f}")
                print(f"    - 交易稅 ({TAX_RATE*100}%): HKD {sell_cost['tax']:.2f}")
                print(f"    - 平台費: HKD {sell_cost['platform_fee']:.2f}")
                print(f"    - 總成本: HKD {sell_cost['total_cost']:.2f} ({sell_cost['cost_percentage']:.2f}%)")
                print(f"    - 淨收入: HKD {sell_cost['net_amount']:,.2f}")
                
                # 顯示15分鐘圖分析
                if chart_analysis.get('error') is None:
                    trend_emoji = "📈" if chart_analysis['trend'] == 'up' else "📉" if chart_analysis['trend'] == 'down' else "➡️"
                    print(f"  15分鐘圖分析:")
                    print(f"    - 當前價: HKD {chart_analysis['current_price']:.2f}")
                    print(f"    - 漲跌: {chart_analysis['change']:+.2f} ({chart_analysis['change_pct']:+.2f}%)")
                    print(f"    - 趨勢: {trend_emoji} {chart_analysis['trend']}")
                    print(f"    - 成交量: {chart_analysis['volume']:,.0f} (5均: {chart_analysis['avg_volume_5']:,.0f})")
                    print(f"    - 5期範圍: HKD {chart_analysis['low_5']:.2f} - {chart_analysis['high_5']:.2f}")
            
            # 計算總盈虧百分比
            total_unrealized_pnl_pct = (total_unrealized_pnl / total_cost_value * 100) if total_cost_value > 0 else 0
            
            print("\n" + "=" * 60)
            print("📊 投資組合總結:")
            print(f"  持倉數量: {len(positions)}個")
            print(f"  總成本: HKD {total_cost_value:,.2f}")
            print(f"  總市值: HKD {total_market_value:,.2f}")
            print(f"  總未實現盈虧: HKD {total_unrealized_pnl:+,.2f} ({total_unrealized_pnl_pct:+.2f}%)")
            
            # 風險提示
            print("\n⚠️  風險提示:")
            for holding in portfolio_details:
                if holding['unrealized_pnl_pct'] < -5:
                    print(f"  ❗ {holding['code']}: 虧損超過5% ({holding['unrealized_pnl_pct']:.1f}%)")
                elif holding['unrealized_pnl_pct'] > 10:
                    print(f"  💰 {holding['code']}: 盈利超過10% ({holding['unrealized_pnl_pct']:.1f}%)")
            
            # 交易建議
            print("\n💡 交易建議:")
            for holding in portfolio_details:
                chart = holding['chart_analysis']
                if chart.get('error') is None:
                    if chart['trend'] == 'down' and holding['unrealized_pnl_pct'] < -3:
                        print(f"  ⚠️  {holding['code']}: 趨勢向下且虧損，考慮止損")
                    elif chart['trend'] == 'up' and holding['unrealized_pnl_pct'] > 15:
                        print(f"  🎯 {holding['code']}: 趨勢向上且盈利豐厚，考慮部分獲利")
            
        else:
            print("📭 無持倉")
            print("💡 建議: 可考慮建立新倉位")
        
        # 關閉連接
        trd_ctx.close()
        quote_ctx.close()
        
    except Exception as e:
        print(f"❌ 監控錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)
    print(f"⏰ 下次監控: {(datetime.now() + timedelta(minutes=30)).strftime('%H:%M')}")
    print("=" * 60)
    
    # 保存監控報告
    save_monitor_report(portfolio_details if 'portfolio_details' in locals() else [])

def save_monitor_report(portfolio_details):
    """保存監控報告"""
    try:
        report = {
            'timestamp': datetime.now().isoformat(),
            'portfolio': portfolio_details,
            'cost_settings': {
                'platform_fee': PLATFORM_FEE,
                'tax_rate': TAX_RATE
            }
        }
        
        report_file = f"/Users/gordonlui/.openclaw/workspace/monitor_reports/monitor_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        
        # 確保目錄存在
        import os
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📁 監控報告已保存: {report_file}")
        
    except Exception as e:
        print(f"❌ 保存報告失敗: {e}")

def test_cost_calculation():
    """測試成本計算"""
    print("\n🧪 交易成本計算測試:")
    print("-" * 40)
    
    test_cases = [
        (100, 1000, True, "買入1000股@100"),
        (100, 1000, False, "賣出1000股@100"),
        (50, 5000, True, "買入5000股@50"),
        (50, 5000, False, "賣出5000股@50"),
    ]
    
    for price, qty, is_buy, desc in test_cases:
        cost = calculate_trading_cost(price, qty, is_buy)
        action = "買入" if is_buy else "賣出"
        print(f"\n{desc}:")
        print(f"  交易金額: HKD {cost['trade_value']:,.2f}")
        print(f"  成本: HKD {cost['total_cost']:.2f} ({cost['cost_percentage']:.3f}%)")
        print(f"  {action}總額: HKD {cost['gross_amount']:,.2f}")
        print(f"  {action}淨額: HKD {cost['net_amount']:,.2f}")

if __name__ == "__main__":
    print("🚀 富途模擬交易增強監控系統")
    print("=" * 60)
    
    # 測試成本計算
    test_cost_calculation()
    
    print("\n" + "=" * 60)
    print("開始監控投資組合...")
    print("=" * 60)
    
    monitor_portfolio_with_costs()
    
    print("\n✅ 監控完成")
    print(f"⏰ 下次運行時間: 30分鐘後 ({(datetime.now() + timedelta(minutes=30)).strftime('%H:%M')})")
#!/usr/bin/env python3
"""
精確獲取富途API實時數據
專門針對香港股票
"""

import sys
import os
import time
from datetime import datetime

print("=" * 70)
print("🎯 富途API精確數據獲取 - 香港股票")
print("=" * 70)

# 股票信息
stocks = [
    {"code": "00005", "name": "匯豐控股", "buy_price": 59.4},
    {"code": "01398", "name": "工商銀行", "buy_price": 4.46},
    {"code": "02638", "name": "港燈-SS", "buy_price": 4.85}
]

def connect_futu():
    """連接富途API"""
    try:
        import futu as ft
        print("✅ 富途API模塊加載成功")
        
        # 連接
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 測試連接 - 使用騰訊股票
        ret, data = quote_ctx.get_market_snapshot(['HK.00700'])
        if ret == ft.RET_OK:
            print("✅ 富途API連接成功")
            return quote_ctx, ft
        else:
            print(f"❌ 連接測試失敗")
            return None, None
            
    except Exception as e:
        print(f"❌ 連接失敗: {e}")
        return None, None

def get_hk_stock_data(quote_ctx, ft, stock_code):
    """獲取香港股票數據"""
    try:
        # 香港股票標準格式
        hk_codes = [
            f"{stock_code}",           # 純數字
            f"HK.{stock_code}",        # HK.前綴
            f"{stock_code}.HK",        # .HK後綴
            f"{stock_code.lstrip('0')}",  # 去掉前導零
            f"HK.{stock_code.lstrip('0')}",  # 去掉前導零加HK前綴
        ]
        
        for hk_code in hk_codes:
            print(f"  嘗試: {hk_code}")
            
            # 獲取市場快照
            ret, data = quote_ctx.get_market_snapshot([hk_code])
            
            if ret == ft.RET_OK and len(data) > 0:
                snapshot = data.iloc[0]
                
                # 檢查數據有效性
                if 'last_price' in snapshot and snapshot['last_price'] > 0:
                    print(f"  成功獲取: {hk_code}")
                    
                    # 獲取股票名稱
                    stock_name = snapshot.get('stock_name', '')
                    if not stock_name:
                        # 嘗試獲取基本資料
                        ret_info, info_data = quote_ctx.get_stock_basicinfo(ft.Market.HK, ft.SecurityType.STOCK, [hk_code])
                        if ret_info == ft.RET_OK and len(info_data) > 0:
                            stock_name = info_data.iloc[0].get('name', '')
                    
                    return {
                        'code': stock_code,
                        'full_code': hk_code,
                        'name': stock_name if stock_name else '未知',
                        'snapshot': snapshot.to_dict(),
                        'success': True
                    }
        
        print(f"  所有格式都失敗")
        return {
            'code': stock_code,
            'success': False,
            'error': '無法獲取有效數據'
        }
        
    except Exception as e:
        print(f"  錯誤: {e}")
        return {
            'code': stock_code,
            'success': False,
            'error': str(e)
        }

def display_precise_data(stock_info, buy_price):
    """顯示精確數據"""
    if not stock_info['success']:
        print(f"❌ {stock_info['code']}: {stock_info.get('error', '失敗')}")
        return None
    
    code = stock_info['code']
    full_code = stock_info['full_code']
    name = stock_info['name']
    snapshot = stock_info['snapshot']
    
    # 獲取價格
    last_price = snapshot.get('last_price', 0)
    if last_price <= 0:
        print(f"❌ {code}: 價格數據無效")
        return None
    
    # 計算盈虧
    profit_loss = last_price - buy_price
    profit_loss_percent = (profit_loss / buy_price) * 100
    
    print(f"\n{'='*60}")
    print(f"📊 {full_code} - {name}")
    print(f"{'='*60}")
    
    print(f"買入價格: ${buy_price:.3f}")
    print(f"當前價格: ${last_price:.3f}")
    
    # 今日變動
    change_rate = snapshot.get('change_rate', 0)
    change_symbol = "🟢" if change_rate > 0 else "🔴" if change_rate < 0 else "⚪"
    print(f"今日變動: {change_symbol} {change_rate:+.2f}%")
    
    # 盈虧
    pl_symbol = "🟢" if profit_loss > 0 else "🔴" if profit_loss < 0 else "⚪"
    print(f"持倉盈虧: {pl_symbol} ${profit_loss:+.3f} ({profit_loss_percent:+.2f}%)")
    
    # 交易數據
    print(f"\n📈 交易數據:")
    volume = snapshot.get('volume', 0)
    if volume > 0:
        print(f"  成交量: {volume:,}")
    
    turnover = snapshot.get('turnover', 0)
    if turnover > 0:
        turnover_m = turnover / 1_000_000
        print(f"  成交額: ${turnover_m:.2f}M")
    
    # 財務數據
    print(f"\n💰 財務數據:")
    pe_ratio = snapshot.get('pe_ratio', 0)
    if pe_ratio > 0:
        print(f"  市盈率: {pe_ratio:.2f}")
    
    pb_ratio = snapshot.get('pb_ratio', 0)
    if pb_ratio > 0:
        print(f"  市淨率: {pb_ratio:.2f}")
    
    market_cap = snapshot.get('market_cap', 0)
    if market_cap > 0:
        market_cap_b = market_cap / 1_000_000_000
        print(f"  市值: ${market_cap_b:.2f}B")
    
    # 價格範圍
    high_price = snapshot.get('high_price', 0)
    low_price = snapshot.get('low_price', 0)
    if high_price > 0 and low_price > 0:
        print(f"  今日範圍: ${low_price:.3f} - ${high_price:.3f}")
    
    # 投資建議
    print(f"\n🎯 投資建議:")
    
    if profit_loss_percent > 20:
        suggestion = "強烈建議獲利了結"
        reason = "漲幅已超過20%，風險增加"
        confidence = "🟢 高"
    elif profit_loss_percent > 10:
        suggestion = "考慮獲利了結"
        reason = "漲幅超過10%，可考慮部分獲利"
        confidence = "🟡 中"
    elif profit_loss_percent > 5:
        suggestion = "持有觀察"
        reason = "溫和上漲，繼續持有"
        confidence = "🟡 中"
    elif profit_loss_percent < -15:
        suggestion = "強烈建議檢視"
        reason = "跌幅超過15%，檢視基本面"
        confidence = "🔴 高"
    elif profit_loss_percent < -8:
        suggestion = "考慮止損"
        reason = "跌幅較大，控制風險"
        confidence = "🟡 中"
    elif profit_loss_percent < -3:
        suggestion = "謹慎持有"
        reason = "小幅下跌，密切關注"
        confidence = "🟡 中"
    else:
        suggestion = "持有"
        reason = "價格變動不大，維持現狀"
        confidence = "⚪ 低"
    
    print(f"  {suggestion}")
    print(f"  信心: {confidence}")
    print(f"  理由: {reason}")
    
    print(f"{'='*60}")
    
    return {
        'code': code,
        'full_code': full_code,
        'name': name,
        'buy_price': buy_price,
        'current_price': last_price,
        'change_rate': change_rate,
        'profit_loss': profit_loss,
        'profit_loss_percent': profit_loss_percent,
        'suggestion': suggestion,
        'confidence': confidence,
        'reason': reason
    }

def main():
    """主函數"""
    print(f"\n🎯 分析目標:")
    for stock in stocks:
        print(f"  • {stock['code']} {stock['name']} (買入價: ${stock['buy_price']})")
    
    print(f"\n🔗 連接富途API...")
    
    quote_ctx, ft = connect_futu()
    if not quote_ctx:
        print(f"\n❌ 無法連接富途API")
        print(f"💡 請確認:")
        print(f"   1. 富途牛牛正在運行")
        print(f"   2. OpenD API已啟用 (工具 → OpenD API設置)")
        print(f"   3. 端口11111可用")
        return
    
    try:
        print(f"\n📡 獲取實時數據...")
        print(f"開始時間: {datetime.now().strftime('%H:%M:%S')}")
        
        all_results = []
        
        for stock in stocks:
            print(f"\n🔍 {stock['code']} {stock['name']}")
            
            # 獲取數據
            stock_info = get_hk_stock_data(quote_ctx, ft, stock['code'])
            
            # 顯示數據
            result = display_precise_data(stock_info, stock['buy_price'])
            
            if result:
                all_results.append(result)
            
            time.sleep(0.5)  # 避免API限制
        
        # 總結報告
        if all_results:
            print(f"\n{'='*70}")
            print("📊 投資組合分析報告")
            print(f"{'='*70}")
            
            total_investment = sum(s['buy_price'] * 1000 for s in stocks)  # 假設每隻1000股
            total_current = sum(r['current_price'] * 1000 for r in all_results)
            total_pl = total_current - total_investment
            total_pl_percent = (total_pl / total_investment) * 100
            
            print(f"\n💰 投資組合統計:")
            print(f"  總投資: ${total_investment:,.2f}")
            print(f"  當前價值: ${total_current:,.2f}")
            print(f"  總盈虧: ${total_pl:+,.2f} ({total_pl_percent:+.2f}%)")
            
            # 個股表現
            print(f"\n📈 個股表現排名:")
            sorted_results = sorted(all_results, key=lambda x: x['profit_loss_percent'], reverse=True)
            
            for i, result in enumerate(sorted_results, 1):
                rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                pl_symbol = "🟢" if result['profit_loss'] > 0 else "🔴" if result['profit_loss'] < 0 else "⚪"
                
                print(f"  {rank_emoji} {result['code']} {result['name']}")
                print(f"     回報: {pl_symbol} {result['profit_loss_percent']:+.2f}%")
                print(f"     建議: {result['suggestion']} ({result['confidence']})")
            
            # 整體建議
            print(f"\n💡 整體投資建議:")
            if total_pl_percent > 15:
                print("  🟢 投資組合表現優秀，建議部分獲利了結")
                print("     可考慮獲利了結漲幅最大的股票，保留現金等待機會")
            elif total_pl_percent > 5:
                print("  🟡 投資組合表現良好，建議持有觀察")
                print("     繼續持有優質股票，關注市場變化")
            elif total_pl_percent < -10:
                print("  🔴 投資組合虧損較大，建議檢視風險")
                print("     檢視基本面，考慮止損或調整持倉")
            elif total_pl_percent < -3:
                print("  🟡 投資組合小幅虧損，建議謹慎持有")
                print("     密切關注市場，準備應對措施")
            else:
                print("  ⚪ 投資組合表現平穩，建議維持現狀")
                print("     定期檢視，等待更好機會")
        
        print(f"\n📅 報告信息:")
        print(f"  數據來源: 富途牛牛實時API")
        print(f"  生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  分析工具: 精確數據獲取系統")
        print(f"{'='*70}")
        
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        
    finally:
        if quote_ctx:
            quote_ctx.close()
            print(f"\n🔒 API連接已關閉")

if __name__ == "__main__":
    main()
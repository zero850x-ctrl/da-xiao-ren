#!/usr/bin/env python3
"""
直接使用富途API獲取實時數據
不使用任何模擬數據
"""

import sys
import os
import time
from datetime import datetime

print("=" * 70)
print("📡 富途API實時數據獲取")
print("=" * 70)

# 股票信息 - 使用正確的格式
stocks = [
    {"code": "00005", "name": "匯豐控股", "buy_price": 59.4},
    {"code": "01398", "name": "工商銀行", "buy_price": 4.46},
    {"code": "02638", "name": "港燈-SS", "buy_price": 4.85}
]

def connect_futu_direct():
    """直接連接富途API"""
    try:
        import futu as ft
        print("✅ 富途API模塊加載成功")
        
        # 嘗試連接
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 測試連接
        ret, data = quote_ctx.get_market_snapshot(['HK.00700'])
        if ret == ft.RET_OK:
            print("✅ 富途API連接成功")
            return quote_ctx, ft
        else:
            print(f"❌ 富途API連接測試失敗: {data}")
            return None, None
            
    except ImportError:
        print("❌ 錯誤: 未安裝futu-api模塊")
        print("💡 請運行: pip install futu-api")
        return None, None
    except Exception as e:
        print(f"❌ 連接失敗: {e}")
        print("💡 請確保:")
        print("   1. 富途牛牛已安裝並運行")
        print("   2. 工具 → OpenD API設置 → 啟用API")
        print("   3. 端口設置為11111")
        return None, None

def get_stock_data_direct(quote_ctx, ft, stock_code):
    """直接獲取股票數據"""
    try:
        # 嘗試不同的代碼格式
        formats_to_try = [
            f"{stock_code}.HK",      # 標準格式
            f"HK.{stock_code}",      # 另一種格式
            stock_code,              # 純數字
        ]
        
        for code_format in formats_to_try:
            print(f"  嘗試代碼格式: {code_format}")
            
            # 獲取快照數據
            ret, data = quote_ctx.get_market_snapshot([code_format])
            
            if ret == ft.RET_OK and len(data) > 0:
                snapshot = data.iloc[0]
                
                # 獲取實時報價
                ret_rt, rt_data = quote_ctx.get_rt_data(code_format)
                realtime_price = None
                if ret_rt == ft.RET_OK and len(rt_data) > 0:
                    realtime_price = rt_data.iloc[0]['last_price']
                
                return {
                    'code': stock_code,
                    'full_code': code_format,
                    'snapshot': snapshot.to_dict(),
                    'realtime_price': realtime_price,
                    'success': True
                }
        
        # 如果所有格式都失敗
        print(f"  所有代碼格式都失敗")
        return {
            'code': stock_code,
            'success': False,
            'error': '無法識別股票代碼'
        }
        
    except Exception as e:
        print(f"  獲取數據時出錯: {e}")
        return {
            'code': stock_code,
            'success': False,
            'error': str(e)
        }

def display_real_time_data(stock_data, buy_price):
    """顯示實時數據"""
    if not stock_data['success']:
        print(f"❌ {stock_data['code']}: 無法獲取數據 - {stock_data.get('error', '未知錯誤')}")
        return None
    
    code = stock_data['code']
    full_code = stock_data['full_code']
    snapshot = stock_data['snapshot']
    realtime_price = stock_data['realtime_price']
    
    # 確定當前價格
    if realtime_price and realtime_price > 0:
        current_price = realtime_price
        price_source = "實時報價"
    elif 'last_price' in snapshot and snapshot['last_price'] > 0:
        current_price = snapshot['last_price']
        price_source = "快照數據"
    else:
        print(f"❌ {code}: 無法獲取有效價格")
        return None
    
    # 計算盈虧
    profit_loss = current_price - buy_price
    profit_loss_percent = (profit_loss / buy_price) * 100
    
    # 顯示結果
    print(f"\n{'='*50}")
    print(f"📊 {full_code}")
    print(f"{'='*50}")
    
    print(f"股票名稱: {snapshot.get('stock_name', '未知')}")
    print(f"買入價格: ${buy_price:.3f}")
    print(f"當前價格: ${current_price:.3f} ({price_source})")
    
    pl_symbol = "🟢" if profit_loss > 0 else "🔴" if profit_loss < 0 else "⚪"
    print(f"盈虧: {pl_symbol} ${profit_loss:+.3f} ({profit_loss_percent:+.2f}%)")
    
    # 顯示其他數據
    if 'change_rate' in snapshot:
        print(f"今日變動: {snapshot['change_rate']:+.2f}%")
    
    if 'volume' in snapshot:
        print(f"成交量: {snapshot['volume']:,}")
    
    if 'turnover' in snapshot:
        turnover_m = snapshot['turnover'] / 1_000_000
        print(f"成交額: ${turnover_m:.2f}M")
    
    if 'pe_ratio' in snapshot:
        print(f"市盈率: {snapshot['pe_ratio']:.2f}")
    
    if 'pb_ratio' in snapshot:
        print(f"市淨率: {snapshot['pb_ratio']:.2f}")
    
    # 簡單建議
    if profit_loss_percent > 10:
        suggestion = "考慮獲利了結"
    elif profit_loss_percent > 5:
        suggestion = "持有觀察"
    elif profit_loss_percent < -10:
        suggestion = "考慮止損"
    elif profit_loss_percent < -5:
        suggestion = "謹慎持有"
    else:
        suggestion = "持有"
    
    print(f"建議: {suggestion}")
    print(f"{'='*50}")
    
    return {
        'code': code,
        'name': snapshot.get('stock_name', '未知'),
        'buy_price': buy_price,
        'current_price': current_price,
        'profit_loss': profit_loss,
        'profit_loss_percent': profit_loss_percent,
        'suggestion': suggestion
    }

def main():
    """主函數"""
    print(f"\n📈 獲取以下股票實時數據:")
    for stock in stocks:
        print(f"  • {stock['code']} {stock['name']} (買入價: ${stock['buy_price']})")
    
    print(f"\n🔗 正在連接富途API...")
    
    # 連接富途API
    quote_ctx, ft = connect_futu_direct()
    
    if not quote_ctx or not ft:
        print(f"\n❌ 無法連接富途API")
        print(f"💡 請檢查:")
        print(f"   1. 富途牛牛是否運行")
        print(f"   2. OpenD API是否啟用")
        print(f"   3. 網絡連接是否正常")
        return
    
    try:
        all_results = []
        success_count = 0
        
        print(f"\n📡 正在獲取實時數據...")
        print(f"⏰ 開始時間: {datetime.now().strftime('%H:%M:%S')}")
        
        for stock in stocks:
            print(f"\n🔍 獲取 {stock['code']} {stock['name']}...")
            
            # 獲取數據
            stock_data = get_stock_data_direct(quote_ctx, ft, stock['code'])
            
            # 顯示數據
            result = display_real_time_data(stock_data, stock['buy_price'])
            
            if result:
                all_results.append(result)
                success_count += 1
            
            # 短暫暫停避免API限制
            time.sleep(1)
        
        # 顯示總結
        print(f"\n{'='*70}")
        print("📊 實時數據獲取總結")
        print(f"{'='*70}")
        
        print(f"成功獲取: {success_count}/{len(stocks)} 隻股票")
        print(f"完成時間: {datetime.now().strftime('%H:%M:%S')}")
        
        if all_results:
            total_pl = sum(r['profit_loss'] for r in all_results)
            total_pl_percent = sum(r['profit_loss_percent'] for r in all_results) / len(all_results)
            
            print(f"\n💰 投資組合表現:")
            print(f"平均盈虧: ${total_pl/len(all_results):+.3f} ({total_pl_percent:+.2f}%)")
            
            # 找出最佳和最差
            best = max(all_results, key=lambda x: x['profit_loss_percent'])
            worst = min(all_results, key=lambda x: x['profit_loss_percent'])
            
            print(f"\n🏆 最佳表現: {best['code']} {best['name']}")
            print(f"   回報: {best['profit_loss_percent']:+.2f}% - {best['suggestion']}")
            
            print(f"\n⚠️  最差表現: {worst['code']} {worst['name']}")
            print(f"   回報: {worst['profit_loss_percent']:+.2f}% - {worst['suggestion']}")
        
        print(f"\n💡 數據來源: 富途牛牛實時API")
        print(f"   更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
    except Exception as e:
        print(f"\n❌ 獲取數據過程中出錯: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 關閉連接
        if quote_ctx:
            quote_ctx.close()
            print(f"\n🔒 已關閉富途API連接")

if __name__ == "__main__":
    main()
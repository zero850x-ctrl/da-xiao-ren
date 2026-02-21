#!/usr/bin/env python3
"""
最終股票檢查 - 獲取最準確的實時數據
"""

import sys
import time
from datetime import datetime

print("=" * 70)
print("🎯 最終股票數據檢查")
print("=" * 70)

def get_accurate_data():
    """獲取準確數據"""
    try:
        import futu as ft
        
        print("🔗 建立高質量API連接...")
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 設置高質量數據請求
        stocks = ['HK.00005', 'HK.01398', 'HK.02638']
        
        print(f"\n📡 獲取高質量數據...")
        
        results = []
        
        for stock in stocks:
            print(f"\n🔍 {stock}")
            
            # 方法1: 獲取市場快照
            ret1, data1 = quote_ctx.get_market_snapshot([stock])
            
            # 方法2: 獲取實時報價
            ret2, data2 = quote_ctx.get_rt_data(stock)
            
            # 方法3: 獲取基本資料
            ret3, data3 = quote_ctx.get_stock_basicinfo(
                ft.Market.HK, ft.SecurityType.STOCK, [stock]
            )
            
            if ret1 == ft.RET_OK and len(data1) > 0:
                snapshot = data1.iloc[0]
                
                # 提取數據
                stock_data = {
                    'code': stock,
                    'last_price': snapshot.get('last_price', 0),
                    'prev_close': snapshot.get('prev_close_price', 0),
                    'open_price': snapshot.get('open_price', 0),
                    'high_price': snapshot.get('high_price', 0),
                    'low_price': snapshot.get('low_price', 0),
                    'volume': snapshot.get('volume', 0),
                    'turnover': snapshot.get('turnover', 0),
                    'change_rate': snapshot.get('change_rate', 0),
                    'pe_ratio': snapshot.get('pe_ratio', 0),
                    'pb_ratio': snapshot.get('pb_ratio', 0),
                }
                
                # 添加實時數據
                if ret2 == ft.RET_OK and len(data2) > 0:
                    rt = data2.iloc[0]
                    stock_data['rt_price'] = rt.get('last_price', 0)
                    stock_data['rt_time'] = rt.get('data_time', '')
                
                # 添加基本資料
                if ret3 == ft.RET_OK and len(data3) > 0:
                    basic = data3.iloc[0]
                    stock_data['name'] = basic.get('name', '未知')
                    stock_data['lot_size'] = basic.get('lot_size', 0)
                    stock_data['stock_type'] = basic.get('security_type', '未知')
                
                results.append(stock_data)
                
                # 顯示
                name = stock_data.get('name', '未知')
                price = stock_data.get('last_price', 0)
                rt_price = stock_data.get('rt_price', 0)
                
                print(f"  名稱: {name}")
                print(f"  收盤價: ${price:.2f}")
                if rt_price:
                    print(f"  實時價: ${rt_price:.2f}")
                print(f"  成交量: {stock_data.get('volume', 0):,}")
                
            else:
                print(f"  ❌ 無法獲取數據")
        
        quote_ctx.close()
        return results
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return []

def analyze_results(results, buy_prices):
    """分析結果"""
    if not results:
        return
    
    print(f"\n{'='*70}")
    print("📊 數據分析報告")
    print(f"{'='*70}")
    
    buy_price_map = {
        'HK.00005': 59.4,
        'HK.01398': 4.46,
        'HK.02638': 4.85
    }
    
    for result in results:
        code = result['code']
        name = result.get('name', '未知')
        price = result['last_price']
        buy_price = buy_price_map.get(code, 0)
        
        if buy_price > 0 and price > 0:
            pl = price - buy_price
            pl_percent = (pl / buy_price) * 100
            
            print(f"\n{code} - {name}")
            print(f"  買入價: ${buy_price:.2f}")
            print(f"  當前價: ${price:.2f}")
            print(f"  盈虧: ${pl:+.2f} ({pl_percent:+.2f}%)")
            
            # 數據質量評估
            data_quality = []
            
            if result.get('name') == '未知':
                data_quality.append("❌ 名稱未知")
            
            if result['change_rate'] == 0:
                data_quality.append("⚠️  無變動數據")
            
            if result['volume'] == 0:
                data_quality.append("⚠️  無成交量")
            
            if data_quality:
                print(f"  數據質量: {', '.join(data_quality)}")
            else:
                print(f"  數據質量: ✅ 良好")
    
    print(f"\n💡 數據解讀:")
    print(f"  1. 如果價格顯示異常高，可能是:")
    print(f"     • 股票拆分後未調整")
    print(f"     • API數據源問題")
    print(f"     • 貨幣單位錯誤")
    print(f"  2. 建議在富途牛牛界面直接確認")
    print(f"  3. 對比其他財經數據源")

def main():
    """主函數"""
    print(f"\n🎯 檢查股票:")
    print(f"  1. HK.00005 (匯豐控股) - 買入價: $59.40")
    print(f"  2. HK.01398 (工商銀行) - 買入價: $4.46")
    print(f"  3. HK.02638 (港燈-SS) - 買入價: $4.85")
    
    print(f"\n⏰ 開始時間: {datetime.now().strftime('%H:%M:%S')}")
    
    # 獲取數據
    results = get_accurate_data()
    
    if results:
        print(f"\n✅ 成功獲取 {len(results)} 隻股票數據")
        
        # 分析
        buy_prices = {
            'HK.00005': 59.4,
            'HK.01398': 4.46,
            'HK.02638': 4.85
        }
        analyze_results(results, buy_prices)
    else:
        print(f"\n❌ 無法獲取有效數據")
    
    print(f"\n🔚 完成時間: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
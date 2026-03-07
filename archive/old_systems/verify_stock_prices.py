#!/usr/bin/env python3
"""
驗證股票價格準確性
對比多個數據點
"""

import sys
import time
from datetime import datetime

print("=" * 70)
print("🔍 股票價格驗證系統")
print("=" * 70)

def verify_with_futu():
    """使用富途API驗證"""
    try:
        import futu as ft
        
        print("🔗 連接富途API...")
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 測試股票
        test_stocks = ['HK.00005', 'HK.01398', 'HK.02638', 'HK.00700']
        
        print(f"\n📊 獲取驗證數據...")
        
        for stock in test_stocks:
            ret, data = quote_ctx.get_market_snapshot([stock])
            
            if ret == ft.RET_OK and len(data) > 0:
                snapshot = data.iloc[0]
                name = snapshot.get('stock_name', '未知')
                price = snapshot.get('last_price', 0)
                change = snapshot.get('change_rate', 0)
                
                print(f"  {stock}: {name}")
                print(f"    價格: ${price:.2f}")
                print(f"    變動: {change:+.2f}%")
                
                # 獲取詳細信息
                ret_info, info_data = quote_ctx.get_stock_basicinfo(
                    ft.Market.HK, ft.SecurityType.STOCK, [stock]
                )
                
                if ret_info == ft.RET_OK and len(info_data) > 0:
                    info = info_data.iloc[0]
                    print(f"    類型: {info.get('security_type', '未知')}")
                    print(f"    狀態: {info.get('listing_status', '未知')}")
            else:
                print(f"  {stock}: 無法獲取數據")
            
            print()
            time.sleep(0.3)
        
        quote_ctx.close()
        return True
        
    except Exception as e:
        print(f"❌ 驗證失敗: {e}")
        return False

def check_price_consistency():
    """檢查價格一致性"""
    print(f"\n📈 價格合理性檢查:")
    
    # 已知的合理價格範圍（港元）
    reasonable_ranges = {
        '00005': (50, 70),      # 匯豐控股
        '01398': (3, 6),        # 工商銀行  
        '02638': (4, 7),        # 港燈-SS
        '00700': (300, 600),    # 騰訊
    }
    
    print(f"💡 預期合理價格範圍:")
    for code, (low, high) in reasonable_ranges.items():
        print(f"  {code}: ${low} - ${high}")
    
    print(f"\n⚠️  如果API返回價格超出此範圍，可能:")
    print(f"   1. 數據錯誤")
    print(f"   2. 股票拆分/合併")
    print(f"   3. 貨幣單位問題")
    print(f"   4. 市場異常波動")

def main():
    """主函數"""
    print(f"\n🎯 驗證目標:")
    print(f"  1. 匯豐控股 (00005)")
    print(f"  2. 工商銀行 (01398)")
    print(f"  3. 港燈-SS (02638)")
    print(f"  4. 騰訊 (00700) - 對照組")
    
    print(f"\n⏰ 開始時間: {datetime.now().strftime('%H:%M:%S')}")
    
    # 使用富途API驗證
    success = verify_with_futu()
    
    if success:
        print(f"✅ 富途API驗證完成")
    else:
        print(f"❌ 富途API驗證失敗")
    
    # 檢查價格一致性
    check_price_consistency()
    
    print(f"\n🔍 驗證建議:")
    print(f"  1. 在富途牛牛界面直接查看股票")
    print(f"  2. 對比其他財經網站數據")
    print(f"  3. 檢查股票歷史價格走勢")
    print(f"  4. 確認買入記錄和價格")
    
    print(f"\n📅 驗證完成時間: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
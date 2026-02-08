#!/usr/bin/env python3
import sys
import time

try:
    from futu import *
except ImportError:
    print("❌ 未安裝futu-api庫")
    print("請運行: pip install futu-api")
    sys.exit(1)

def test_hsi_data():
    """測試獲取HSI數據"""
    print("📊 測試獲取HSI實時數據...")
    print(f"時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # 連接Futu
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 正確的HSI代碼
        hsi_codes = ["HK.800000", "HK.HSI"]  # 兩種可能的代碼格式
        
        for code in hsi_codes:
            print(f"\n嘗試代碼: {code}")
            
            # 獲取市場快照
            ret, data = quote_ctx.get_market_snapshot([code])
            
            if ret == RET_OK:
                print(f"✅ 成功獲取{code}數據！")
                print(f"股票名稱: {data['code'][0]}")
                print(f"最新價格: {data['last_price'][0]}")
                print(f"漲跌幅: {data['change_rate'][0]:.2f}%")
                print(f"成交量: {data['volume'][0]}")
                print(f"成交額: {data['turnover'][0]}")
                print(f"開盤價: {data['open_price'][0]}")
                print(f"最高價: {data['high_price'][0]}")
                print(f"最低價: {data['low_price'][0]}")
                print(f"昨收價: {data['prev_close_price'][0]}")
                
                # 獲取歷史K線
                print(f"\n獲取{code}歷史K線...")
                ret, kline_data = quote_ctx.request_history_kline(
                    code, 
                    start="2025-11-08", 
                    end="2026-02-08",
                    ktype=KLType.K_DAY
                )
                
                if ret == RET_OK:
                    print(f"✅ 歷史K線獲取成功！")
                    print(f"數據點數量: {len(kline_data)}")
                    print(f"日期範圍: {kline_data['time_key'][0]} 到 {kline_data['time_key'][-1]}")
                    
                    # 保存數據
                    import json
                    import pandas as pd
                    
                    # 轉換為DataFrame
                    df = pd.DataFrame(kline_data)
                    
                    # 保存為JSON
                    df.to_json(f"hsi_real_data_{code.replace('.', '_')}.json", orient='records')
                    df.to_csv(f"hsi_real_data_{code.replace('.', '_')}.csv", index=False)
                    
                    print(f"✅ 數據已保存:")
                    print(f"  - hsi_real_data_{code.replace('.', '_')}.json")
                    print(f"  - hsi_real_data_{code.replace('.', '_')}.csv")
                    
                    # 顯示最新幾條數據
                    print(f"\n最新5個交易日數據:")
                    latest_data = df.tail(5)
                    for idx, row in latest_data.iterrows():
                        print(f"  {row['time_key']}: 開{row['open']:.2f} 高{row['high']:.2f} 低{row['low']:.2f} 收{row['close']:.2f} 量{row['volume']}")
                    
                    quote_ctx.close()
                    return True, code, df
                else:
                    print(f"❌ 歷史K線獲取失敗: {kline_data}")
            else:
                print(f"❌ {code}數據獲取失敗: {data}")
        
        quote_ctx.close()
        print("\n❌ 所有代碼格式都失敗")
        return False, None, None
        
    except Exception as e:
        print(f"❌ 連接過程中出錯: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

if __name__ == "__main__":
    success, code, data = test_hsi_data()
    
    print("\n" + "=" * 50)
    if success:
        print(f"🎉 Futu OpenD連接成功！")
        print(f"成功獲取{code}的實時數據")
        print(f"數據點數量: {len(data)}")
        print(f"時間範圍: {data['time_key'].iloc[0]} 到 {data['time_key'].iloc[-1]}")
        print("\n可以開始進行技術分析了！")
    else:
        print("⚠️  Futu OpenD連接有問題")
        print("建議:")
        print("1. 檢查OpenD是否已登錄")
        print("2. 檢查API權限設置")
        print("3. 嘗試重啟OpenD")
        print("4. 檢查網絡連接")
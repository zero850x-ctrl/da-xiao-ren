#!/usr/bin/env python3
import sys
import time

try:
    from futu import *
except ImportError:
    print("❌ 未安裝futu-api庫")
    print("請運行: pip install futu-api")
    sys.exit(1)

def test_futu_connection():
    """測試Futu API連接"""
    print("🔌 測試Futu OpenD API連接...")
    print(f"時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # 嘗試連接
        print("1. 創建OpenQuoteContext...")
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        print("2. 測試連接狀態...")
        ret, data = quote_ctx.get_global_state()
        
        if ret == RET_OK:
            print(f"✅ 連接成功！")
            print(f"市場狀態: {data}")
            
            # 測試獲取HSI數據
            print("\n3. 測試獲取HSI數據...")
            ret, data = quote_ctx.get_market_snapshot(["HK.HSI"])
            
            if ret == RET_OK:
                print(f"✅ HSI數據獲取成功！")
                print(f"最新價格: {data['last_price'][0]}")
                print(f"漲跌幅: {data['change_rate'][0]:.2f}%")
                print(f"成交量: {data['volume'][0]}")
                
                # 測試歷史數據
                print("\n4. 測試獲取歷史K線...")
                ret, data = quote_ctx.request_history_kline(
                    "HK.HSI", 
                    start="2026-01-01", 
                    end="2026-02-08",
                    ktype=KLType.K_DAY
                )
                
                if ret == RET_OK:
                    print(f"✅ 歷史K線獲取成功！")
                    print(f"數據點數量: {len(data)}")
                    print(f"日期範圍: {data['time_key'][0]} 到 {data['time_key'][-1]}")
                else:
                    print(f"❌ 歷史K線獲取失敗: {data}")
            else:
                print(f"❌ HSI數據獲取失敗: {data}")
            
            # 關閉連接
            quote_ctx.close()
            print("\n✅ 所有測試完成！")
            return True
            
        else:
            print(f"❌ 連接失敗: {data}")
            quote_ctx.close()
            return False
            
    except Exception as e:
        print(f"❌ 連接過程中出錯: {e}")
        return False

if __name__ == "__main__":
    success = test_futu_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Futu OpenD連接完全正常！")
        print("可以開始獲取實時數據進行分析")
    else:
        print("⚠️  Futu OpenD連接有問題")
        print("建議:")
        print("1. 檢查OpenD是否已登錄")
        print("2. 檢查API權限設置")
        print("3. 嘗試重啟OpenD")
        print("4. 檢查網絡連接")
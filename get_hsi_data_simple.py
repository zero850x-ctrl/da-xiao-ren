#!/usr/bin/env python3
import sys
import time
import json

try:
    from futu import *
except ImportError:
    print("❌ 未安裝futu-api庫")
    sys.exit(1)

def get_hsi_data():
    """獲取HSI數據"""
    print("📊 獲取HSI實時數據...")
    
    try:
        # 連接Futu
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 使用正確的HSI代碼
        hsi_code = "HK.800000"
        
        print(f"1. 獲取{ hsi_code }實時數據...")
        ret, data = quote_ctx.get_market_snapshot([hsi_code])
        
        if ret == RET_OK:
            print("✅ 實時數據獲取成功")
            
            # 顯示關鍵數據
            realtime_data = {
                "code": hsi_code,
                "last_price": float(data['last_price'][0]),
                "open_price": float(data['open_price'][0]),
                "high_price": float(data['high_price'][0]),
                "low_price": float(data['low_price'][0]),
                "prev_close_price": float(data['prev_close_price'][0]),
                "volume": int(data['volume'][0]),
                "turnover": float(data['turnover'][0]),
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "data_source": "Futu OpenD"
            }
            
            print(f"   最新價格: {realtime_data['last_price']}")
            print(f"   漲跌: {realtime_data['last_price'] - realtime_data['prev_close_price']:.2f}")
            print(f"   成交量: {realtime_data['volume']:,}")
            print(f"   成交額: {realtime_data['turnover']:,.0f}")
            
            # 保存實時數據
            with open("hsi_realtime.json", "w") as f:
                json.dump(realtime_data, f, indent=2)
            
            print(f"2. 獲取{ hsi_code }歷史K線數據...")
            ret, kline_data, page_req_key = quote_ctx.request_history_kline(
                hsi_code, 
                start="2025-11-08", 
                end="2026-02-08",
                ktype=KLType.K_DAY,
                max_count=1000
            )
            
            if ret == RET_OK:
                print(f"✅ 歷史K線獲取成功，共{len(kline_data)}個數據點")
                
                # 保存歷史數據
                history_data = []
                for i in range(len(kline_data)):
                    history_data.append({
                        "date": kline_data['time_key'][i],
                        "open": float(kline_data['open'][i]),
                        "high": float(kline_data['high'][i]),
                        "low": float(kline_data['low'][i]),
                        "close": float(kline_data['close'][i]),
                        "volume": int(kline_data['volume'][i]),
                        "turnover": float(kline_data['turnover'][i])
                    })
                
                with open("hsi_history.json", "w") as f:
                    json.dump(history_data, f, indent=2)
                
                # 保存為CSV
                import csv
                with open("hsi_history.csv", "w", newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=["date", "open", "high", "low", "close", "volume", "turnover"])
                    writer.writeheader()
                    writer.writerows(history_data)
                
                print(f"✅ 數據已保存:")
                print(f"   - hsi_realtime.json (實時數據)")
                print(f"   - hsi_history.json (歷史K線)")
                print(f"   - hsi_history.csv (CSV格式)")
                
                # 顯示最新數據
                print(f"\n📈 最新5個交易日:")
                for i in range(min(5, len(history_data))):
                    day = history_data[-(i+1)]
                    print(f"   {day['date']}: 開{day['open']:.2f} 高{day['high']:.2f} 低{day['low']:.2f} 收{day['close']:.2f} 量{day['volume']:,}")
                
                quote_ctx.close()
                return True, realtime_data, history_data
            else:
                print(f"❌ 歷史K線獲取失敗: {kline_data}")
                quote_ctx.close()
                return False, None, None
        else:
            print(f"❌ 實時數據獲取失敗: {data}")
            quote_ctx.close()
            return False, None, None
            
    except Exception as e:
        print(f"❌ 出錯: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

if __name__ == "__main__":
    print("=" * 50)
    print("Futu OpenD HSI數據獲取")
    print(f"時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    success, realtime, history = get_hsi_data()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 數據獲取成功！")
        print(f"實時價格: {realtime['last_price']}")
        print(f"歷史數據點: {len(history)}個")
        print(f"數據範圍: {history[0]['date']} 到 {history[-1]['date']}")
        print("\n✅ OpenD連接問題已解決！")
        print("可以開始進行技術分析了")
    else:
        print("❌ 數據獲取失敗")
        print("請檢查OpenD連接狀態")
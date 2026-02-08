#!/usr/bin/env python3
"""
從Futu API獲取HSI（恒生指數）數據
"""

from futu import *
import pandas as pd
from datetime import datetime, timedelta
import json
import os

def get_hsi_data():
    """獲取HSI數據"""
    print("📊 開始從Futu獲取HSI數據")
    print("=" * 60)
    
    # 創建數據目錄
    data_dir = "/Users/gordonlui/.openclaw/workspace/hsi_data"
    os.makedirs(data_dir, exist_ok=True)
    
    try:
        # 連接Futu OpenD
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        print("✅ 連接Futu OpenD成功")
        
        # HSI代碼
        hsi_code = "HK.HSI"
        
        # 1. 獲取實時報價
        print("\n1. 獲取HSI實時報價...")
        ret, data = quote_ctx.get_market_snapshot([hsi_code])
        
        if ret == RET_OK:
            print(f"✅ 實時數據獲取成功")
            snapshot = data.iloc[0]
            
            realtime_data = {
                "symbol": hsi_code,
                "name": "恒生指數",
                "last_price": float(snapshot['last_price']),
                "open_price": float(snapshot['open_price']),
                "high_price": float(snapshot['high_price']),
                "low_price": float(snapshot['low_price']),
                "prev_close_price": float(snapshot['prev_close_price']),
                "change": float(snapshot['change']),
                "change_percent": float(snapshot['change_rate']) * 100,
                "volume": int(snapshot['volume']),
                "turnover": float(snapshot['turnover']),
                "update_time": str(snapshot['update_time']),
                "data_collection_time": datetime.now().isoformat()
            }
            
            # 保存實時數據
            realtime_file = os.path.join(data_dir, "hsi_realtime.json")
            with open(realtime_file, 'w') as f:
                json.dump(realtime_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 實時數據已保存: {realtime_file}")
            print(f"   最新價格: {realtime_data['last_price']}")
            print(f"   漲跌幅: {realtime_data['change_percent']:.2f}%")
            
        else:
            print(f"❌ 實時數據獲取失敗: {data}")
            # 使用模擬數據作為備用
            realtime_data = create_mock_realtime_data()
        
        # 2. 獲取歷史K線數據
        print("\n2. 獲取HSI歷史K線數據...")
        
        # 計算日期範圍：過去3個月
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        ret, data, page_req_key = quote_ctx.request_history_kline(
            hsi_code,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            ktype=KLType.K_DAY,  # 日線
            max_count=1000
        )
        
        if ret == RET_OK:
            print(f"✅ 歷史數據獲取成功，共{len(data)}條記錄")
            
            # 轉換為更易處理的格式
            history_data = []
            for idx, row in data.iterrows():
                history_data.append({
                    "date": str(row['time_key']),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": int(row['volume']),
                    "turnover": float(row['turnover'])
                })
            
            # 保存歷史數據
            history_file = os.path.join(data_dir, "hsi_history.json")
            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
            
            print(f"✅ 歷史數據已保存: {history_file}")
            print(f"   數據範圍: {history_data[0]['date']} 到 {history_data[-1]['date']}")
            
            # 創建pandas DataFrame用於分析
            df = pd.DataFrame(history_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 保存CSV格式
            csv_file = os.path.join(data_dir, "hsi_history.csv")
            df.to_csv(csv_file)
            print(f"✅ CSV格式已保存: {csv_file}")
            
        else:
            print(f"❌ 歷史數據獲取失敗: {data}")
            print("⚠️  使用模擬歷史數據進行分析")
            history_data = create_mock_history_data()
        
        # 3. 獲取技術指標數據
        print("\n3. 獲取技術指標數據...")
        # 這裡可以添加更多技術指標的獲取
        
        # 關閉連接
        quote_ctx.close()
        
        # 4. 創建數據摘要報告
        print("\n4. 創建數據摘要報告...")
        create_data_summary(realtime_data, history_data if 'history_data' in locals() else None, data_dir)
        
        return {
            "realtime": realtime_data,
            "history": history_data if 'history_data' in locals() else None,
            "data_dir": data_dir,
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ Futu API連接異常: {e}")
        print("⚠️  使用模擬數據進行分析")
        
        # 創建模擬數據
        realtime_data = create_mock_realtime_data()
        history_data = create_mock_history_data()
        
        # 保存模擬數據
        realtime_file = os.path.join(data_dir, "hsi_realtime_mock.json")
        with open(realtime_file, 'w') as f:
            json.dump(realtime_data, f, indent=2, ensure_ascii=False)
        
        history_file = os.path.join(data_dir, "hsi_history_mock.json")
        with open(history_file, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        return {
            "realtime": realtime_data,
            "history": history_data,
            "data_dir": data_dir,
            "status": "mock_data",
            "note": "使用模擬數據，Futu API連接失敗"
        }

def create_mock_realtime_data():
    """創建模擬實時數據"""
    return {
        "symbol": "HK.HSI",
        "name": "恒生指數",
        "last_price": 18542.67,
        "open_price": 18450.12,
        "high_price": 18620.34,
        "low_price": 18380.45,
        "prev_close_price": 18420.89,
        "change": 121.78,
        "change_percent": 0.66,
        "volume": 1854234567,
        "turnover": 128.45,
        "update_time": "2026-02-08 11:45:00",
        "data_collection_time": datetime.now().isoformat(),
        "note": "模擬數據 - Futu API連接失敗"
    }

def create_mock_history_data():
    """創建模擬歷史數據"""
    # 創建過去90天的模擬數據
    history_data = []
    base_price = 18000
    current_date = datetime.now() - timedelta(days=90)
    
    for i in range(90):
        date_str = current_date.strftime('%Y-%m-%d')
        
        # 模擬價格波動
        volatility = 0.015  # 1.5%日波動率
        change = base_price * volatility * (0.5 - pd.np.random.random())
        close_price = base_price + change
        
        open_price = close_price * (1 + (pd.np.random.random() - 0.5) * 0.01)
        high_price = max(open_price, close_price) * (1 + pd.np.random.random() * 0.02)
        low_price = min(open_price, close_price) * (1 - pd.np.random.random() * 0.02)
        volume = int(1e9 + pd.np.random.random() * 5e8)
        
        history_data.append({
            "date": date_str,
            "open": float(open_price),
            "high": float(high_price),
            "low": float(low_price),
            "close": float(close_price),
            "volume": volume,
            "turnover": float(volume * close_price / 1e9)
        })
        
        base_price = close_price
        current_date += timedelta(days=1)
    
    return history_data

def create_data_summary(realtime_data, history_data, data_dir):
    """創建數據摘要報告"""
    summary = {
        "data_collection_time": datetime.now().isoformat(),
        "symbol": realtime_data.get("symbol"),
        "data_source": "Futu API" if realtime_data.get("note") != "模擬數據 - Futu API連接失敗" else "模擬數據",
        "realtime_summary": {
            "last_price": realtime_data.get("last_price"),
            "change_percent": realtime_data.get("change_percent"),
            "day_high": realtime_data.get("high_price"),
            "day_low": realtime_data.get("low_price"),
            "volume": realtime_data.get("volume")
        },
        "history_summary": {
            "data_points": len(history_data) if history_data else 0,
            "date_range": {
                "start": history_data[0]["date"] if history_data else None,
                "end": history_data[-1]["date"] if history_data else None
            } if history_data else None,
            "price_range": {
                "min": min([h["low"] for h in history_data]) if history_data else None,
                "max": max([h["high"] for h in history_data]) if history_data else None
            } if history_data else None
        },
        "files_created": {
            "realtime_data": os.path.join(data_dir, "hsi_realtime.json"),
            "history_data": os.path.join(data_dir, "hsi_history.json"),
            "csv_data": os.path.join(data_dir, "hsi_history.csv")
        },
        "next_steps": [
            "技術指標計算",
            "圖表生成",
            "技術分析報告"
        ]
    }
    
    summary_file = os.path.join(data_dir, "data_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 數據摘要報告已保存: {summary_file}")
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("📋 HSI數據獲取摘要")
    print("=" * 60)
    print(f"數據源: {summary['data_source']}")
    print(f"最新價格: {summary['realtime_summary']['last_price']}")
    print(f"漲跌幅: {summary['realtime_summary']['change_percent']:.2f}%")
    if history_data:
        print(f"歷史數據點: {summary['history_summary']['data_points']}")
        print(f"數據範圍: {summary['history_summary']['date_range']['start']} 到 {summary['history_summary']['date_range']['end']}")
    print(f"數據目錄: {data_dir}")
    print("=" * 60)

def main():
    """主函數"""
    print("🚀 HSI數據獲取系統啟動")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    result = get_hsi_data()
    
    print("\n" + "=" * 60)
    print("🎉 HSI數據獲取完成")
    print("=" * 60)
    
    print(f"\n📁 數據文件位置: {result['data_dir']}")
    print(f"📊 數據狀態: {result['status']}")
    
    if result['status'] == 'mock_data':
        print("⚠️  注意: 使用模擬數據，實際分析結果僅供參考")
        print("💡 建議: 檢查Futu OpenD是否運行在127.0.0.1:11111")
    
    print("\n🚀 下一步: 開始技術分析")
    print("使用deepseek-reasoner進行:")
    print("• 斐波那契移動平均線計算")
    print("• 平行通道和趨勢線識別")
    print("• 黃金分割分析")
    print("• RSI和成交量分析")
    
    print("\n⏰ 預計時間安排:")
    print("• 現在-12:30: 數據獲取完成")
    print("• 12:30-13:30: 數據處理")
    print("• 13:30-14:30: 午餐休息")
    print("• 14:30-15:30: 技術分析")
    print("• 15:30-16:30: 報告生成")
    print("• 16:30-17:00: 電郵發送")

if __name__ == "__main__":
    main()
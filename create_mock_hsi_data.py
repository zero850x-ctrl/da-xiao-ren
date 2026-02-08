#!/usr/bin/env python3
"""
創建模擬HSI數據
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def create_mock_data():
    """創建模擬HSI數據"""
    print("🎮 創建模擬HSI數據")
    print("=" * 60)
    
    # 創建數據目錄
    data_dir = "/Users/gordonlui/.openclaw/workspace/hsi_data"
    os.makedirs(data_dir, exist_ok=True)
    
    # 1. 創建模擬實時數據
    print("\n1. 創建模擬實時數據...")
    
    realtime_data = {
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
        "note": "模擬數據 - 基於HSI典型市場特徵生成",
        "data_source": "simulated",
        "confidence": "high",
        "simulation_parameters": {
            "base_price": 18000,
            "daily_volatility": 0.015,
            "trend_slope": 0.001,
            "volume_mean": 1500000000,
            "volume_std": 500000000
        }
    }
    
    realtime_file = os.path.join(data_dir, "hsi_realtime.json")
    with open(realtime_file, 'w') as f:
        json.dump(realtime_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 實時數據已創建: {realtime_file}")
    print(f"   模擬價格: {realtime_data['last_price']}")
    print(f"   模擬漲幅: {realtime_data['change_percent']}%")
    
    # 2. 創建模擬歷史數據
    print("\n2. 創建模擬歷史數據...")
    
    # 創建過去90天的數據
    history_data = []
    base_price = 17500  # 起始價格
    current_date = datetime.now() - timedelta(days=89)  # 90天前
    
    # 添加一些趨勢和波動
    trend = 0.0012  # 每日平均上漲0.12%
    volatility = 0.015  # 每日波動率1.5%
    
    for i in range(90):
        date_str = current_date.strftime('%Y-%m-%d')
        
        # 計算基礎價格（帶趨勢）
        trend_price = base_price * (1 + trend * i)
        
        # 添加隨機波動
        random_factor = np.random.normal(0, volatility)
        close_price = trend_price * (1 + random_factor)
        
        # 生成OHLC數據
        open_price = close_price * (1 + np.random.normal(0, volatility * 0.3))
        high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, volatility * 0.5)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, volatility * 0.5)))
        
        # 確保高低價合理
        if high_price < max(open_price, close_price):
            high_price = max(open_price, close_price) * 1.01
        if low_price > min(open_price, close_price):
            low_price = min(open_price, close_price) * 0.99
        
        # 生成成交量
        volume_mean = 1500000000
        volume_std = 500000000
        volume = int(abs(np.random.normal(volume_mean, volume_std)))
        
        # 生成成交額
        turnover = volume * close_price / 1e9  # 十億為單位
        
        history_data.append({
            "date": date_str,
            "open": float(open_price),
            "high": float(high_price),
            "low": float(low_price),
            "close": float(close_price),
            "volume": int(volume),
            "turnover": float(turnover)
        })
        
        current_date += timedelta(days=1)
    
    # 保存歷史數據
    history_file = os.path.join(data_dir, "hsi_history.json")
    with open(history_file, 'w') as f:
        json.dump(history_data, f, indent=2)
    
    print(f"✅ 歷史數據已創建: {history_file}")
    print(f"   數據點數: {len(history_data)}")
    print(f"   時間範圍: {history_data[0]['date']} 到 {history_data[-1]['date']}")
    
    # 創建CSV格式
    df = pd.DataFrame(history_data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    csv_file = os.path.join(data_dir, "hsi_history.csv")
    df.to_csv(csv_file)
    print(f"✅ CSV格式已創建: {csv_file}")
    
    # 3. 創建數據摘要
    print("\n3. 創建數據摘要...")
    
    summary = {
        "data_creation_time": datetime.now().isoformat(),
        "data_type": "simulated",
        "symbol": "HK.HSI",
        "simulation_parameters": realtime_data["simulation_parameters"],
        "data_statistics": {
            "price_statistics": {
                "min_price": float(df['low'].min()),
                "max_price": float(df['high'].max()),
                "avg_price": float(df['close'].mean()),
                "current_price": realtime_data["last_price"],
                "total_return": (realtime_data["last_price"] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
            },
            "volume_statistics": {
                "avg_volume": int(df['volume'].mean()),
                "max_volume": int(df['volume'].max()),
                "min_volume": int(df['volume'].min())
            },
            "volatility_statistics": {
                "daily_volatility": float(df['close'].pct_change().std() * 100),
                "avg_daily_range": float(((df['high'] - df['low']) / df['close']).mean() * 100)
            }
        },
        "data_quality": {
            "missing_values": 0,
            "data_consistency": "high",
            "market_realism": "realistic",
            "note": "模擬數據基於HSI歷史波動特徵生成，適合技術分析練習"
        },
        "files_created": {
            "realtime_data": realtime_file,
            "history_data": history_file,
            "csv_data": csv_file
        }
    }
    
    summary_file = os.path.join(data_dir, "data_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 數據摘要已創建: {summary_file}")
    
    # 4. 打印數據概覽
    print("\n" + "=" * 60)
    print("📊 模擬HSI數據概覽")
    print("=" * 60)
    print(f"數據類型: {summary['data_type']}")
    print(f"當前價格: {summary['data_statistics']['price_statistics']['current_price']:.2f}")
    print(f"價格範圍: {summary['data_statistics']['price_statistics']['min_price']:.2f} - {summary['data_statistics']['price_statistics']['max_price']:.2f}")
    print(f"總回報率: {summary['data_statistics']['price_statistics']['total_return']:.2f}%")
    print(f"日均波動率: {summary['data_statistics']['volatility_statistics']['daily_volatility']:.2f}%")
    print(f"日均波幅: {summary['data_statistics']['volatility_statistics']['avg_daily_range']:.2f}%")
    print(f"數據目錄: {data_dir}")
    print("=" * 60)
    
    print("\n💡 模擬數據說明:")
    print("• 基於HSI歷史波動特徵生成")
    print("• 包含趨勢、波動、成交量等市場特徵")
    print("• 適合技術分析和算法測試")
    print("• 明確標註為模擬數據")
    
    print("\n🚀 下一步:")
    print("1. 運行技術分析系統")
    print("2. 使用deepseek-reasoner進行推理分析")
    print("3. 生成技術分析報告")

def main():
    """主函數"""
    print("🎯 創建模擬HSI數據用於技術分析")
    create_mock_data()

if __name__ == "__main__":
    main()
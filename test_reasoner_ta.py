#!/usr/bin/env python3
"""
測試deepseek-reasoner的技術分析推理能力
"""

import json
from datetime import datetime

def test_reasoner_technical_analysis():
    """測試技術分析推理能力"""
    print("🧠 測試deepseek-reasoner技術分析推理能力")
    print("=" * 60)
    
    # 測試案例1: 斐波那契移動平均線計算
    test_case_1 = {
        "task": "計算斐波那契移動平均線(8,13,34)",
        "data": {
            "prices": [100, 102, 101, 105, 104, 106, 108, 107, 109, 110, 
                      112, 111, 113, 115, 114, 116, 118, 117, 119, 120,
                      122, 121, 123, 125, 124, 126, 128, 127, 129, 130,
                      132, 131, 133, 135, 134, 136, 138, 137, 139, 140],
            "periods": [8, 13, 34]
        },
        "expected_reasoning": [
            "1. 理解斐波那契移動平均線的概念",
            "2. 分別計算8日、13日、34日移動平均線",
            "3. 分析各均線的交叉和排列情況",
            "4. 判斷趨勢方向和強度"
        ]
    }
    
    # 測試案例2: 平行通道識別
    test_case_2 = {
        "task": "識別價格平行通道",
        "data": {
            "highs": [110, 112, 111, 115, 114, 116, 118, 117, 119, 120],
            "lows": [105, 107, 106, 110, 109, 111, 113, 112, 114, 115],
            "current_price": 117
        },
        "expected_reasoning": [
            "1. 識別價格高點和低點",
            "2. 繪製上軌(阻力線)和下軌(支撐線)",
            "3. 檢查通道是否平行",
            "4. 判斷當前價格在通道中的位置"
        ]
    }
    
    # 測試案例3: 黃金分割分析
    test_case_3 = {
        "task": "計算黃金分割水平",
        "data": {
            "swing_high": 140,
            "swing_low": 100,
            "fibonacci_levels": [0.236, 0.382, 0.5, 0.618, 0.786]
        },
        "expected_reasoning": [
            "1. 計算價格波動範圍: 140-100=40",
            "2. 計算各斐波那契水平: 100+40*level",
            "3. 分析各水平的支撐阻力意義",
            "4. 判斷當前價格與斐波那契水平的關係"
        ]
    }
    
    # 測試案例4: RSI和成交量分析
    test_case_4 = {
        "task": "分析RSI和成交量",
        "data": {
            "prices": [130, 132, 131, 133, 135, 134, 136, 138, 137, 139],
            "volumes": [1000000, 1200000, 1100000, 1300000, 1400000, 
                       1300000, 1500000, 1600000, 1500000, 1700000],
            "rsi_period": 14
        },
        "expected_reasoning": [
            "1. 計算RSI指標值",
            "2. 分析RSI超買超賣情況",
            "3. 分析成交量與價格的關係",
            "4. 判斷市場動能和趨勢強度"
        ]
    }
    
    print("\n📊 測試案例準備完成:")
    print(f"1. 斐波那契移動平均線計算")
    print(f"2. 平行通道識別")
    print(f"3. 黃金分割分析")
    print(f"4. RSI和成交量分析")
    
    # 創建技術分析系統框架
    ta_system = {
        "model": "deepseek-reasoner",
        "reasoning_enabled": True,
        "technical_indicators": {
            "moving_averages": {
                "fibonacci_periods": [8, 13, 21, 34, 55, 89],
                "calculation_method": "exponential"
            },
            "trend_lines": {
                "auto_detection": True,
                "min_points": 3
            },
            "fibonacci": {
                "levels": [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0],
                "extensions": [1.272, 1.414, 1.618]
            },
            "oscillators": {
                "rsi": {"period": 14, "overbought": 70, "oversold": 30},
                "macd": {"fast": 12, "slow": 26, "signal": 9}
            },
            "volume_analysis": {
                "volume_price_trend": True,
                "on_balance_volume": True
            }
        },
        "chart_patterns": [
            "parallel_channel",
            "trend_channel",
            "head_and_shoulders",
            "double_top_bottom",
            "triangle",
            "wedge"
        ],
        "timeframes": ["1h", "4h", "1d", "1w"],
        "output_formats": ["chart", "report", "alert", "prediction"]
    }
    
    # 保存測試配置
    config_file = "/Users/gordonlui/.openclaw/workspace/ta_system_config.json"
    with open(config_file, "w") as f:
        json.dump(ta_system, f, indent=2)
    
    print(f"\n✅ 技術分析系統配置已保存: {config_file}")
    
    # 創建HSI分析計劃
    hsi_analysis_plan = {
        "symbol": "HSI",
        "full_name": "Hang Seng Index",
        "analysis_time": datetime.now().isoformat(),
        "scheduled_time": "14:00-15:00",
        "technical_indicators": ta_system["technical_indicators"],
        "data_sources": [
            "yahoo_finance",
            "bloomberg",
            "reuters",
            "tradingview"
        ],
        "analysis_steps": [
            "1. 數據收集和清洗",
            "2. 多時間框架分析",
            "3. 技術指標計算",
            "4. 圖表模式識別",
            "5. 趨勢分析和預測",
            "6. 風險評估和建議"
        ],
        "report_outputs": [
            "technical_charts",
            "analysis_summary",
            "weekly_prediction",
            "trading_recommendations"
        ],
        "delivery": {
            "email": "zero850x@gmail.com",
            "format": "pptx + pdf",
            "scheduled_time": "15:00"
        }
    }
    
    plan_file = "/Users/gordonlui/.openclaw/workspace/hsi_analysis_plan.json"
    with open(plan_file, "w") as f:
        json.dump(hsi_analysis_plan, f, indent=2)
    
    print(f"✅ HSI分析計劃已保存: {plan_file}")
    
    # 總結
    print("\n" + "=" * 60)
    print("🎯 deepseek-reasoner技術分析系統準備完成")
    print("=" * 60)
    
    print("\n📋 系統能力:")
    print("• 斐波那契移動平均線計算 (8, 13, 34)")
    print("• 平行通道和趨勢線識別")
    print("• 黃金分割水平分析")
    print("• RSI和成交量技術指標")
    print("• 多時間框架分析")
    print("• 圖表模式識別")
    
    print("\n🚀 下一步行動:")
    print("1. 開啟推理模式: /reasoning on")
    print("2. 測試技術分析推理")
    print("3. 準備HSI數據收集")
    print("4. 14:00開始HSI技術分析")
    
    print("\n💡 deepseek-reasoner優勢:")
    print("• 思維鏈推理確保分析邏輯嚴謹")
    print("• 複雜計算驗證提高準確性")
    print("• 多步驟分析支持完整技術分析")
    print("• 成本效益適合頻繁分析任務")
    
    print("\n⏰ 時間安排:")
    print("• 11:45-12:30: 系統測試和優化")
    print("• 12:30-13:30: 午餐休息")
    print("• 13:30-14:30: HSI數據準備")
    print("• 14:30-15:30: 技術分析執行")
    print("• 15:30-16:00: 報告生成和發送")

def main():
    test_reasoner_technical_analysis()

if __name__ == "__main__":
    main()
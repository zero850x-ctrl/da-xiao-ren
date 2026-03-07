#!/usr/bin/env python3
"""
黃金交易風險自動計算器
最大每注限制: 0.01手
"""

def calculate_gold_risk_auto():
    """自動計算黃金交易風險"""
    print("=" * 60)
    print("💰 黃金交易風險計算器 (最大每注: 0.01手)")
    print("=" * 60)
    
    # 賬戶信息
    account_balance = 1000.0  # 美元
    max_lot_size = 0.01  # 最大每注手數
    
    print(f"\n📊 賬戶信息:")
    print(f"   賬戶餘額: ${account_balance:.2f}")
    print(f"   最大每注限制: {max_lot_size}手")
    
    # 黃金交易參數
    print(f"\n💰 黃金交易參數:")
    print(f"   交易對: XAUUSD (現貨黃金)")
    print(f"   合約大小: 100盎司/標準手")
    print(f"   每點價值: $0.10 (0.1手)")
    print(f"   0.01手每點價值: $0.01")
    
    # 風險計算示例
    print(f"\n🎯 風險計算示例 (0.01手):")
    
    # 示例1: 保守交易
    print(f"\n1. 保守交易策略:")
    print(f"   手數: 0.01手")
    print(f"   止損: 50點")
    print(f"   風險: $0.50 (0.05% 賬戶)")
    print(f"   止盈: 100點 (1:2風險回報)")
    print(f"   潛在盈利: $1.00 (0.10% 賬戶)")
    
    # 示例2: 中等交易
    print(f"\n2. 中等交易策略:")
    print(f"   手數: 0.01手")
    print(f"   止損: 100點")
    print(f"   風險: $1.00 (0.10% 賬戶)")
    print(f"   止盈: 200點 (1:2風險回報)")
    print(f"   潛在盈利: $2.00 (0.20% 賬戶)")
    
    # 示例3: 激進交易
    print(f"\n3. 激進交易策略:")
    print(f"   手數: 0.01手")
    print(f"   止損: 200點")
    print(f"   風險: $2.00 (0.20% 賬戶)")
    print(f"   止盈: 400點 (1:2風險回報)")
    print(f"   潛在盈利: $4.00 (0.40% 賬戶)")
    
    # 盈利目標計算
    print(f"\n📈 盈利目標分析 (0.01手):")
    
    daily_scenarios = [
        {"trades": 1, "win_rate": 60, "risk_per_trade": 0.50},
        {"trades": 2, "win_rate": 55, "risk_per_trade": 0.50},
        {"trades": 3, "win_rate": 50, "risk_per_trade": 0.50},
    ]
    
    for scenario in daily_scenarios:
        trades = scenario["trades"]
        win_rate = scenario["win_rate"] / 100
        risk = scenario["risk_per_trade"]
        reward = risk * 2  # 1:2風險回報
        
        # 計算期望值
        expected_value = (win_rate * reward) - ((1 - win_rate) * risk)
        daily_expected = expected_value * trades
        
        print(f"\n   每日{trades}筆交易 (勝率{scenario['win_rate']}%):")
        print(f"     每筆風險: ${risk:.2f}")
        print(f"     每筆潛在盈利: ${reward:.2f}")
        print(f"     每筆期望值: ${expected_value:.2f}")
        print(f"     每日期望盈利: ${daily_expected:.2f}")
        print(f"     每月期望盈利 (20天): ${daily_expected * 20:.2f}")
    
    # 資金管理規則
    print(f"\n💡 0.01手限制下的資金管理:")
    print(f"   1. 單筆最大損失: $2.00 (200點止損)")
    print(f"   2. 每日最大損失: $10.00 (5筆虧損)")
    print(f"   3. 每日盈利目標: $2-5")
    print(f"   4. 每月盈利目標: $40-100")
    print(f"   5. 連續虧損2次後: 降低手數或暫停")
    
    # 交易心理建議
    print(f"\n🧠 交易心理建議:")
    print(f"   1. 接受小額盈利，積少成多")
    print(f"   2. 重點提高勝率，而非單筆盈利")
    print(f"   3. 保持耐心，等待高質量機會")
    print(f"   4. 記錄每筆交易，分析改進")
    print(f"   5. 定期覆盤，優化策略")
    
    # 技術分析重點
    print(f"\n📊 技術分析重點 (0.01手策略):")
    print(f"   1. 主要時間框架: H1, H4")
    print(f"   2. 關鍵支撐阻力位")
    print(f"   3. 移動平均線交叉 (SMA20/50)")
    print(f"   4. RSI超買超賣 (30/70)")
    print(f"   5. 價格行為模式")
    
    print(f"\n" + "=" * 60)
    print(f"✅ 風險計算完成")
    print(f"=" * 60)


def generate_trading_plan():
    """生成交易計劃"""
    print(f"\n\n" + "=" * 60)
    print(f"📋 0.01手黃金交易計劃模板")
    print(f"=" * 60)
    
    plan = """
交易對: XAUUSD (現貨黃金)
最大手數: 0.01手
賬戶資金: $1000

風險管理:
- 單筆風險: ≤$2.00 (≤0.2%)
- 每日風險: ≤$10.00 (≤1%)
- 每月風險: ≤$200.00 (≤20%)
- 風險回報比: ≥1:2

交易規則:
1. 交易時間: 主要交易時段 (倫敦/紐約開盤)
2. 交易次數: ≤3次/日
3. 最小止損: 50點
4. 最小止盈: 100點
5. 持倉時間: ≤24小時

技術分析:
- 主要時間框架: H4 (趨勢), H1 (入場)
- 次要時間框架: M15 (精確入場)
- 關鍵指標: SMA20/50, RSI(14), 支撐阻力位

交易策略:
1. 趨勢跟隨:
   - H4趨勢向上 + H1回調至支撐 + RSI超賣 → 買入
   - H4趨勢向下 + H1反彈至阻力 + RSI超買 → 賣出

2. 區間交易:
   - 價格在明確區間內 + 觸及區間邊界 → 反向交易

3. 突破交易:
   - 關鍵水平突破 + 回踩確認 → 順勢交易

交易日誌:
- 記錄每筆交易: 時間、價格、手數、原因
- 記錄盈虧: 實際結果 vs 預期
- 每周覆盤: 分析勝率、盈虧比、改進點

心態管理:
- 盈利不驕，虧損不餒
- 嚴格止損，不抗單
- 連續虧損2次後暫停
- 每日盈利達標後停止
"""
    
    print(plan)
    
    print(f"\n" + "=" * 60)
    print(f"🎯 開始行動:")
    print(f"=" * 60)
    print(f"1. 複製此交易計劃")
    print(f"2. 根據實際情況調整")
    print(f"3. 嚴格執行至少30天")
    print(f"4. 每月評估和優化")
    print(f"5. 逐步增加經驗和信心")


def main():
    """主函數"""
    calculate_gold_risk_auto()
    generate_trading_plan()
    
    print(f"\n" + "=" * 60)
    print(f"🚀 下一步行動建議")
    print(f"=" * 60)
    print(f"\n短期 (第1周):")
    print(f"   ✓ 學習黃金市場基礎")
    print(f"   ✓ 練習技術分析")
    print(f"   ✓ 模擬交易10筆")
    
    print(f"\n中期 (第2-4周):")
    print(f"   ✓ 實盤交易0.01手")
    print(f"   ✓ 完善交易日誌")
    print(f"   ✓ 優化交易策略")
    
    print(f"\n長期 (1-3月):")
    print(f"   ✓ 穩定盈利後考慮調整手數")
    print(f"   ✓ 學習更多交易策略")
    print(f"   ✓ 考慮自動化交易")


if __name__ == "__main__":
    main()
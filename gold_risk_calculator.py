#!/usr/bin/env python3
"""
黃金交易風險計算器
最大每注限制: 0.01手
"""

def calculate_gold_risk():
    """計算黃金交易風險"""
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
    
    # 風險計算
    print(f"\n🎯 風險計算 (0.01手限制):")
    
    # 不同止損點數的風險
    stop_loss_options = [20, 30, 50, 100]  # 點數
    
    for sl_pips in stop_loss_options:
        # 0.01手的最大可能損失
        max_loss = sl_pips * 0.01  # 0.01手每點$0.01
        
        # 佔賬戶百分比
        loss_percent = (max_loss / account_balance) * 100
        
        print(f"\n   止損 {sl_pips} 點:")
        print(f"     最大損失: ${max_loss:.2f}")
        print(f"     佔賬戶: {loss_percent:.2f}%")
        
        if loss_percent <= 2:
            print(f"     ✅ 安全 (≤2%)")
        elif loss_percent <= 5:
            print(f"     ⚠️  警告 (2-5%)")
        else:
            print(f"     ❌ 危險 (>5%)")
    
    # 不同風險比例下的建議止損
    print(f"\n🔍 不同風險比例下的建議止損:")
    
    risk_percentages = [0.5, 1.0, 2.0]  # 風險百分比
    
    for risk_percent in risk_percentages:
        risk_amount = account_balance * (risk_percent / 100)
        
        # 計算最大允許止損點數 (0.01手)
        max_allowed_sl = risk_amount / 0.01  # 0.01手每點$0.01
        
        print(f"\n   風險比例 {risk_percent}%:")
        print(f"     風險金額: ${risk_amount:.2f}")
        print(f"     最大止損: {max_allowed_sl:.0f} 點")
        
        if max_allowed_sl >= 100:
            print(f"     ✅ 足夠空間 (≥100點)")
        elif max_allowed_sl >= 50:
            print(f"     ⚠️  中等空間 (50-100點)")
        else:
            print(f"     ❌ 空間不足 (<50點)")
    
    # 交易示例
    print(f"\n📝 交易示例 (0.01手):")
    
    examples = [
        {"entry": 2000.0, "sl": 1995.0, "tp": 2010.0, "description": "保守交易"},
        {"entry": 2000.0, "sl": 1990.0, "tp": 2020.0, "description": "中等交易"},
        {"entry": 2000.0, "sl": 1980.0, "tp": 2040.0, "description": "寬幅交易"},
    ]
    
    for ex in examples:
        sl_pips = (ex["entry"] - ex["sl"]) * 10  # 黃金1點=0.10，所以乘以10
        tp_pips = (ex["tp"] - ex["entry"]) * 10
        
        risk = sl_pips * 0.01  # 0.01手
        reward = tp_pips * 0.01
        
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        print(f"\n   {ex['description']}:")
        print(f"     入場: ${ex['entry']:.2f}")
        print(f"     止損: ${ex['sl']:.2f} ({sl_pips:.0f}點)")
        print(f"     止盈: ${ex['tp']:.2f} ({tp_pips:.0f}點)")
        print(f"     風險: ${risk:.2f}")
        print(f"     潛在盈利: ${reward:.2f}")
        print(f"     風險回報比: 1:{risk_reward_ratio:.1f}")
    
    # 資金管理建議
    print(f"\n💡 資金管理建議 (0.01手限制):")
    print(f"   1. 單筆風險 ≤ 1% (約$10)")
    print(f"   2. 每日最大損失 ≤ 5% (約$50)")
    print(f"   3. 每月最大損失 ≤ 20% (約$200)")
    print(f"   4. 使用至少 1:2 風險回報比")
    print(f"   5. 連續虧損3次後暫停交易")
    
    # 交易計劃模板
    print(f"\n📋 交易計劃模板:")
    print(f"   交易對: XAUUSD")
    print(f"   最大手數: 0.01手")
    print(f"   單筆風險: $___ (≤1%)")
    print(f"   止損點數: ___ 點")
    print(f"   止盈點數: ___ 點 (≥2倍止損)")
    print(f"   每日交易次數: ≤3次")
    print(f"   交易時間: ___")
    print(f"   交易策略: ___")
    
    print(f"\n" + "=" * 60)
    print(f"✅ 風險計算完成")
    print(f"=" * 60)


def calculate_position_size_with_limit():
    """計算帶有限制的倉位大小"""
    print(f"\n\n" + "=" * 60)
    print(f"🔧 倉位大小計算器")
    print(f"=" * 60)
    
    while True:
        try:
            print(f"\n輸入參數 (輸入0退出):")
            
            balance = float(input("   賬戶餘額 ($): "))
            if balance == 0:
                break
                
            risk_percent = float(input("   風險比例 (%): "))
            stop_loss_pips = float(input("   止損點數: "))
            max_lot_size = 0.01  # 固定限制
            
            # 計算風險金額
            risk_amount = balance * (risk_percent / 100)
            
            # 計算理論手數
            pip_value_per_0_1_lot = 0.10  # 0.1手每點$0.10
            pip_value_per_lot = 1.0  # 1手每點$1.0
            
            theoretical_lot = risk_amount / (stop_loss_pips * pip_value_per_0_1_lot)
            
            # 應用限制
            actual_lot = min(theoretical_lot, max_lot_size)
            
            # 計算實際風險
            actual_risk = actual_lot * stop_loss_pips * pip_value_per_0_1_lot * 10
            actual_risk_percent = (actual_risk / balance) * 100
            
            print(f"\n📊 計算結果:")
            print(f"   賬戶餘額: ${balance:.2f}")
            print(f"   風險比例: {risk_percent}%")
            print(f"   理論風險: ${risk_amount:.2f}")
            print(f"   止損點數: {stop_loss_pips}點")
            print(f"   最大限制: {max_lot_size}手")
            print(f"   理論手數: {theoretical_lot:.4f}手")
            print(f"   實際手數: {actual_lot:.4f}手")
            print(f"   實際風險: ${actual_risk:.2f}")
            print(f"   實際風險比例: {actual_risk_percent:.2f}%")
            
            if actual_lot < theoretical_lot:
                print(f"   ⚠️  注意: 受0.01手限制，實際風險低於設定")
                print(f"   建議: 可考慮調整止損為 {risk_amount/(actual_lot * pip_value_per_0_1_lot * 10):.0f} 點")
            
        except ValueError:
            print("❌ 輸入錯誤，請輸入數字")
        except ZeroDivisionError:
            print("❌ 止損點數不能為0")


def main():
    """主函數"""
    calculate_gold_risk()
    calculate_position_size_with_limit()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 總結: 0.01手限制下的黃金交易")
    print(f"=" * 60)
    print(f"\n關鍵要點:")
    print(f"   1. 每筆交易最大損失約 $0.01-0.10")
    print(f"   2. 需要較寬止損 (建議50-100點)")
    print(f"   3. 適合小資金賬戶 ($100-$1000)")
    print(f"   4. 需要耐心，盈利積少成多")
    print(f"   5. 重點學習技術分析提高勝率")
    
    print(f"\n📈 盈利目標 (0.01手):")
    print(f"   每日目標: $1-2 (10-20點)")
    print(f"   每月目標: $20-40 (200-400點)")
    print(f"   年化目標: $240-480 (2400-4800點)")
    
    print(f"\n💪 心態建議:")
    print(f"   1. 接受小額盈利")
    print(f"   2. 注重交易質量而非數量")
    print(f"   3. 保持紀律，嚴格止損")
    print(f"   4. 記錄每筆交易，持續學習")


if __name__ == "__main__":
    main()
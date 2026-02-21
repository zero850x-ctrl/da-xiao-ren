#!/usr/bin/env python3
"""
測試交易信號生成
"""

import numpy as np
from datetime import datetime

def test_signal_generation():
    """測試信號生成"""
    print("🧪 測試交易信號生成")
    
    # 測試不同的市場情況
    test_cases = [
        {
            'name': 'RSI超賣情況',
            'price': 2000,
            'sma_short': 1990,
            'sma_long': 2010,
            'rsi': 25,  # 超賣
            'expected_signal': 'BUY',
            'expected_strength': 0.4
        },
        {
            'name': 'RSI超買情況',
            'price': 2000,
            'sma_short': 2010,
            'sma_long': 1990,
            'rsi': 75,  # 超買
            'expected_signal': 'SELL',
            'expected_strength': 0.4
        },
        {
            'name': 'SMA黃金交叉',
            'price': 2000,
            'sma_short': 2010,  # 剛剛上穿
            'sma_long': 1990,
            'rsi': 50,
            'expected_signal': 'BUY',
            'expected_strength': 0.3
        },
        {
            'name': 'SMA死亡交叉',
            'price': 2000,
            'sma_short': 1990,  # 剛剛下穿
            'sma_long': 2010,
            'rsi': 50,
            'expected_signal': 'SELL',
            'expected_strength': 0.3
        },
        {
            'name': '混合信號（強）',
            'price': 2000,
            'sma_short': 2010,  # 黃金交叉
            'sma_long': 1990,
            'rsi': 25,  # 超賣
            'expected_signal': 'BUY',
            'expected_strength': 0.7  # 0.3 + 0.4
        }
    ]
    
    for test in test_cases:
        print(f"\n🔍 {test['name']}:")
        print(f"   價格: ${test['price']:.2f}")
        print(f"   SMA短: ${test['sma_short']:.2f}, SMA長: ${test['sma_long']:.2f}")
        print(f"   RSI: {test['rsi']:.1f}")
        
        # 計算信號強度
        strength = 0.0
        signal = None
        
        # SMA信號
        if test['sma_short'] > test['sma_long']:
            diff = test['sma_short'] - test['sma_long']
            if diff > 5:
                strength += 0.3
                signal = 'BUY'
        elif test['sma_long'] > test['sma_short']:
            diff = test['sma_long'] - test['sma_short']
            if diff > 5:
                strength += 0.3
                signal = 'SELL'
        
        # RSI信號
        if test['rsi'] < 30:
            strength += 0.4
            signal = 'BUY'
        elif test['rsi'] > 70:
            strength += 0.4
            signal = 'SELL'
        
        # 檢查閾值
        threshold = 0.5
        if strength >= threshold:
            print(f"   ✅ 生成信號: {signal} (強度: {strength:.2f})")
            
            # 計算手數
            max_lot = 0.01
            lot_size = max_lot * strength
            lot_size = max(0.01, min(max_lot, lot_size))
            
            print(f"   計算手數: {lot_size:.3f}手")
            
            # 計算風險
            stop_loss = 60  # 點
            risk_amount = stop_loss * lot_size * 0.1
            print(f"   風險金額: ${risk_amount:.2f}")
            
            if signal == test['expected_signal'] and abs(strength - test['expected_strength']) < 0.1:
                print(f"   🎯 測試通過!")
            else:
                print(f"   ⚠️  預期: {test['expected_signal']} (強度: {test['expected_strength']})")
        else:
            print(f"   ⏸️  信號強度不足 ({strength:.2f} < {threshold})")
    
    print(f"\n📊 信號生成測試完成")
    print(f"\n💡 實際使用:")
    print(f"   1. 系統會每小時檢查市場條件")
    print(f"   2. 只有信號強度 ≥ 0.5 才會交易")
    print(f"   3. 手數根據信號強度調整 (0.01手×強度)")
    print(f"   4. 每日最多3筆交易")

if __name__ == "__main__":
    test_signal_generation()
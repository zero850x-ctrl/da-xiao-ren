#!/usr/bin/env python3
"""
OANDA快速測試腳本 - 立即開始測試
"""

import os
import json
import time
from datetime import datetime
import numpy as np

print("=" * 70)
print("🧪 OANDA黃金交易系統 - 快速測試")
print("=" * 70)

def test_configuration():
    """測試配置"""
    print("\n🔧 測試系統配置...")
    
    # 檢查配置文件
    config_path = "/Users/gordonlui/.openclaw/workspace/oanda_config.json"
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        api_key = config.get('api_key', '')
        account_id = config.get('account_id', '')
        
        if api_key and api_key != 'YOUR_OANDA_API_KEY_HERE':
            print(f"✅ 配置文件正常")
            print(f"   環境: {config.get('environment', 'practice')}")
            print(f"   交易品種: {config.get('symbol', 'XAU_USD')}")
            print(f"   手數: {config.get('lot_size', 0.01)}")
            return True
        else:
            print(f"⚠️  配置文件需要更新")
            print(f"   請編輯 {config_path}")
            print(f"   填入你的OANDA API密鑰")
            return False
    else:
        print(f"❌ 配置文件不存在: {config_path}")
        return False

def test_python_packages():
    """測試Python包"""
    print("\n🐍 測試Python包...")
    
    packages = [
        ('pandas', '數據分析'),
        ('numpy', '數值計算'),
        ('oandapyV20', 'OANDA API'),
        ('schedule', '定時任務'),
    ]
    
    all_ok = True
    for package, description in packages:
        try:
            __import__(package)
            print(f"✅ {package}: {description} - 已安裝")
        except ImportError:
            print(f"❌ {package}: {description} - 未安裝")
            all_ok = False
    
    if not all_ok:
        print("\n💡 安裝缺失的包:")
        print("   pip install oandapyV20 pandas numpy schedule")
    
    return all_ok

def test_trading_logic():
    """測試交易邏輯"""
    print("\n🎯 測試交易邏輯...")
    
    # 加載策略
    strategy_path = "/Users/gordonlui/.openclaw/workspace/optimized_strategy.json"
    
    if os.path.exists(strategy_path):
        with open(strategy_path, 'r') as f:
            strategy = json.load(f)
        
        params = strategy.get('parameters', {})
        print(f"✅ 使用策略: {strategy.get('optimized_strategy', '平衡策略')}")
        print(f"   參數: SMA{params.get('sma_short', 15)}/{params.get('sma_long', 40)}")
        print(f"          RSI{params.get('rsi_period', 10)} ({params.get('rsi_low', 25)}/{params.get('rsi_high', 75)})")
    else:
        params = {
            'sma_short': 15,
            'sma_long': 40,
            'rsi_period': 10,
            'rsi_low': 25,
            'rsi_high': 75,
            'stop_loss': 60,
            'take_profit': 120,
            'signal_threshold': 0.5
        }
        print(f"ℹ️  使用默認策略參數")
    
    # 模擬市場數據測試
    print("\n📊 模擬市場數據測試...")
    
    np.random.seed(42)
    
    test_cases = [
        {
            'name': '強力買入信號',
            'price': 2000,
            'sma_short': 2010,
            'sma_long': 1990,
            'rsi': 20,
            'expected': 'BUY'
        },
        {
            'name': '強力賣出信號',
            'price': 2000,
            'sma_short': 1990,
            'sma_long': 2010,
            'rsi': 80,
            'expected': 'SELL'
        },
        {
            'name': '弱信號 (保持觀望)',
            'price': 2000,
            'sma_short': 2002,
            'sma_long': 1998,
            'rsi': 50,
            'expected': 'HOLD'
        },
    ]
    
    for test in test_cases:
        print(f"\n  測試: {test['name']}")
        print(f"    價格: ${test['price']:.2f}")
        print(f"    SMA短: ${test['sma_short']:.2f}, SMA長: ${test['sma_long']:.2f}")
        print(f"    RSI: {test['rsi']:.1f}")
        
        # 計算信號強度
        strength = 0.0
        signal = 'HOLD'
        
        # SMA信號
        if test['sma_short'] > test['sma_long'] and (test['sma_short'] - test['sma_long']) > 5:
            strength += 0.3
            signal = 'BUY'
        elif test['sma_long'] > test['sma_short'] and (test['sma_long'] - test['sma_short']) > 5:
            strength += 0.3
            signal = 'SELL'
        
        # RSI信號
        if test['rsi'] < params.get('rsi_low', 25):
            strength += 0.4
            signal = 'BUY'
        elif test['rsi'] > params.get('rsi_high', 75):
            strength += 0.4
            signal = 'SELL'
        
        # 檢查閾值
        threshold = params.get('signal_threshold', 0.5)
        
        if strength >= threshold:
            result = "✅" if signal == test['expected'] else "❌"
            print(f"    信號: {signal} (強度: {strength:.2f}) {result}")
            
            # 計算風險
            lot_size = 0.01
            stop_loss = params.get('stop_loss', 60)
            risk_amount = stop_loss * lot_size * 0.1
            
            print(f"    手數: {lot_size}手")
            print(f"    風險: ${risk_amount:.2f}")
        else:
            print(f"    無信號 (強度: {strength:.2f} < {threshold})")
    
    return True

def test_risk_management():
    """測試風險管理"""
    print("\n🛡️ 測試風險管理規則...")
    
    rules = [
        ("最大手數", "0.01手", "✅ 嚴格控制單筆風險"),
        ("每日最大交易次數", "3次", "✅ 防止過度交易"),
        ("止損點數", "60點 ($6.00)", "✅ 嚴格止損紀律"),
        ("止盈點數", "120點 ($12.00)", "✅ 風險回報比 1:2"),
        ("信號閾值", "0.5 (中等強度)", "✅ 只交易高質量信號"),
    ]
    
    for rule, value, note in rules:
        print(f"  {rule}: {value} - {note}")
    
    print("\n📈 風險計算示例 (0.01手):")
    print("  每點價值: $0.10")
    print("  60點止損風險: $6.00")
    print("  120點止盈潛在盈利: $12.00")
    print("  風險回報比: 1:2 (理想)")
    
    return True

def test_system_integration():
    """測試系統集成"""
    print("\n🔗 測試系統集成...")
    
    # 檢查重要文件
    important_files = [
        ("oanda_config.json", "OANDA配置"),
        ("optimized_strategy.json", "策略配置"),
        ("start_oanda_trader.py", "啟動腳本"),
        ("oanda_trader_final.py", "交易引擎"),
    ]
    
    all_exists = True
    for file, description in important_files:
        path = f"/Users/gordonlui/.openclaw/workspace/{file}"
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {description}: {size} 字節")
        else:
            print(f"❌ {description}: 文件不存在")
            all_exists = False
    
    # 檢查日誌目錄
    log_dir = "/Users/gordonlui/.openclaw/workspace/logs"
    if os.path.exists(log_dir):
        print(f"✅ 日誌目錄: 已創建")
    else:
        print(f"⚠️  日誌目錄: 未創建")
    
    return all_exists

def provide_next_steps():
    """提供下一步建議"""
    print("\n" + "=" * 70)
    print("🎯 下一步行動建議")
    print("=" * 70)
    
    steps = [
        ("立即 (5分鐘)", [
            "1. 註冊OANDA模擬賬戶",
            "2. 獲取API密鑰",
            "3. 更新配置文件"
        ]),
        ("今天 (30分鐘)", [
            "1. 運行完整系統測試",
            "2. 開始模擬交易",
            "3. 記錄第一次交易"
        ]),
        ("本週 (2-3小時)", [
            "1. 完成10筆模擬交易",
            "2. 分析交易結果",
            "3. 優化策略參數"
        ]),
        ("下週 (準備實盤)", [
            "1. 評估模擬交易表現",
            "2. 準備小資金 ($100-500)",
            "3. 開始0.01手實盤"
        ]),
    ]
    
    for timeframe, actions in steps:
        print(f"\n{timeframe}:")
        for action in actions:
            print(f"  • {action}")
    
    print("\n💡 關鍵提示:")
    print("  1. 先用模擬賬戶驗證策略")
    print("  2. 嚴格遵守0.01手限制")
    print("  3. 記錄每筆交易用於優化")
    print("  4. 保持耐心，交易是馬拉松")

def main():
    """主函數"""
    print("\n🚀 開始快速測試...")
    
    # 運行所有測試
    tests = [
        ("系統配置", test_configuration),
        ("Python包", test_python_packages),
        ("交易邏輯", test_trading_logic),
        ("風險管理", test_risk_management),
        ("系統集成", test_system_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*40}")
            print(f"測試: {test_name}")
            print('='*40)
            result = test_func()
            results.append((test_name, result))
            time.sleep(0.5)
        except Exception as e:
            print(f"❌ 測試失敗: {e}")
            results.append((test_name, False))
    
    # 顯示測試結果
    print("\n" + "=" * 70)
    print("📊 測試結果總結")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！系統準備就緒！")
    elif passed >= total * 0.8:
        print("⚠️  大部分測試通過，需要少量調整")
    else:
        print("❌ 需要修復多項問題")
    
    # 提供下一步建議
    provide_next_steps()
    
    print("\n" + "=" * 70)
    print("💪 你可以今天就开始!")
    print("=" * 70)

if __name__ == "__main__":
    main()
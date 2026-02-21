#!/usr/bin/env python3
"""
測試自動交易系統
"""

import subprocess
import time
from datetime import datetime

print("=" * 70)
print("🧪 測試自動交易系統")
print("=" * 70)

def run_test(script_name, description):
    """運行測試"""
    print(f"\n🔧 測試: {description}")
    print(f"   腳本: {script_name}")
    print(f"   時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        result = subprocess.run(
            ['python3', script_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"   ✅ 測試成功")
            # 顯示部分輸出
            lines = result.stdout.split('\n')
            for line in lines[:10]:  # 只顯示前10行
                if line.strip():
                    print(f"      {line}")
            if len(lines) > 10:
                print(f"      ... (共{len(lines)}行)")
        else:
            print(f"   ❌ 測試失敗 (返回碼: {result.returncode})")
            print(f"      錯誤: {result.stderr[:200]}...")
            
    except subprocess.TimeoutExpired:
        print(f"   ⏱️  測試超時 (30秒)")
    except Exception as e:
        print(f"   ❌ 測試異常: {e}")

def main():
    """主測試函數"""
    
    print("📋 測試列表:")
    print("1. 價格突破檢測系統")
    print("2. 聯想集團監控系統")
    print("3. 自動交易系統")
    print("4. 快速預測系統")
    
    # 測試1: 價格突破檢測
    run_test(
        '/Users/gordonlui/.openclaw/workspace/check_price_breakout.py',
        '價格突破檢測系統'
    )
    
    # 測試2: 聯想集團監控
    run_test(
        '/Users/gordonlui/.openclaw/workspace/execute_992_updated.py',
        '聯想集團監控系統'
    )
    
    # 測試3: 自動交易系統 (簡化模式)
    print(f"\n🔧 測試: 自動交易系統 (簡化)")
    print(f"   時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 創建簡化測試
    test_code = """
import sys
sys.path.append('/Users/gordonlui/.openclaw/workspace')

try:
    from auto_trading_system import AutoTradingSystem
    system = AutoTradingSystem()
    
    # 測試獲取價格
    price = system.get_real_time_price('00992')
    print(f"✅ 價格獲取成功: ${price:.2f}")
    
    # 測試預測
    prediction = system.run_xgboost_prediction('00992')
    print(f"✅ 預測成功: {prediction['signal']} (概率: {prediction['probability_up']:.3f})")
    
    print("✅ 自動交易系統核心功能正常")
    
except Exception as e:
    print(f"❌ 測試失敗: {e}")
    import traceback
    traceback.print_exc()
"""
    
    with open('/tmp/test_auto_trading.py', 'w') as f:
        f.write(test_code)
    
    run_test('/tmp/test_auto_trading.py', '自動交易系統核心功能')
    
    # 測試4: 快速預測
    run_test(
        '/Users/gordonlui/.openclaw/workspace/quick_992_predict.py',
        '快速預測系統'
    )
    
    print(f"\n{'='*70}")
    print(f"📊 測試結果總結")
    print(f"{'='*70}")
    
    print(f"\n✅ 已創建的系統文件:")
    print(f"   1. auto_trading_system.py - 完整自動交易系統")
    print(f"   2. check_price_breakout.py - 價格突破檢測")
    print(f"   3. setup_trading_cron.py - Cron任務配置")
    print(f"   4. execute_992_updated.py - 聯想專用監控")
    print(f"   5. quick_992_predict.py - 快速預測")
    
    print(f"\n🎯 下一步行動:")
    print(f"   1. 設置Cron任務:")
    print(f"      python3 setup_trading_cron.py")
    print(f"      openclaw cron add --job trading_cron_config.json")
    
    print(f"   2. 測試定時任務:")
    print(f"      openclaw cron list")
    print(f"      openclaw cron run <jobId>")
    
    print(f"   3. 修改配置:")
    print(f"      /Users/gordonlui/.openclaw/workspace/trading_config.json")
    
    print(f"   4. 監控結果:")
    print(f"      /Users/gordonlui/.openclaw/workspace/trading_results/")
    print(f"      /Users/gordonlui/.openclaw/workspace/breakout_detection/")
    
    print(f"\n💡 重要提醒:")
    print(f"   1. 系統使用模擬數據，需要連接富途API獲取真實數據")
    print(f"   2. 實際交易前請進行充分測試")
    print(f"   3. 投資有風險，請謹慎決策")
    
    print(f"\n✅ 測試完成")
    print("=" * 70)

if __name__ == "__main__":
    main()
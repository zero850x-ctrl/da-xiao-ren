#!/usr/bin/env python3
"""
測試富途連接
"""

import sys
import json
from datetime import datetime

def main():
    """主函數"""
    print("🚀 富途連接測試")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    try:
        # 嘗試導入futu
        print("1. 📦 檢查futu庫...")
        try:
            import futu
            print(f"   ✅ futu版本: {futu.__version__}")
        except ImportError:
            print("   ❌ futu未安裝")
            print("     請運行: pip install futu-api")
            return
        
        # 測試連接
        print("\n2. 🔌 測試API連接...")
        try:
            from futu import OpenQuoteContext, RET_OK
            
            # 創建連接
            quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
            print("   ✅ 成功創建連接")
            
            # 測試獲取數據
            print("\n3. 📈 測試獲取股票數據...")
            test_stocks = ['HK.00992', 'HK.00700']
            
            ret, data = quote_ctx.get_market_snapshot(test_stocks)
            if ret == RET_OK:
                print(f"   ✅ 成功獲取{len(data)}隻股票數據")
                for _, row in data.iterrows():
                    print(f"      {row['code']}: HKD {row['last_price']:.2f}")
            else:
                print(f"   ❌ 獲取數據失敗")
            
            # 關閉連接
            quote_ctx.close()
            print("\n4. 🔌 關閉連接...")
            print("   ✅ 連接已關閉")
            
            status = "SUCCESS"
            error = None
            
        except Exception as e:
            print(f"   ❌ 連接失敗: {e}")
            status = "CONNECTION_FAILED"
            error = str(e)
        
    except Exception as e:
        print(f"❌ 系統錯誤: {e}")
        status = "SYSTEM_ERROR"
        error = str(e)
    
    # 報告
    print(f"\n{'='*70}")
    print(f"📋 測試結果")
    print(f"{'='*70}")
    
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': status,
        'error': error
    }
    
    if status == "SUCCESS":
        print("✅ 富途連接測試成功!")
        print("   可以獲取股票數據")
        print("\n💡 下一步:")
        print("   1. 確保富途OpenD運行中")
        print("   2. 登錄模擬賬戶")
        print("   3. 運行真實交易系統")
    else:
        print(f"❌ 測試失敗: {status}")
        if error:
            print(f"   錯誤: {error}")
        print("\n🔧 故障排除:")
        print("   1. 檢查富途OpenD是否運行")
        print("   2. 檢查端口11111是否開放")
        print("   3. 確認網絡連接正常")
    
    # 保存報告
    report_file = f"/Users/gordonlui/.openclaw/workspace/futu_test_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 報告已保存: {report_file}")
    except Exception as e:
        print(f"❌ 保存失敗: {e}")
    
    print(f"\n{'='*70}")
    print(f"✅ 測試完成")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
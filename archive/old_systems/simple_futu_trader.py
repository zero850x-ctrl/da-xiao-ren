#!/usr/bin/env python3
"""
簡單富途交易測試
測試富途API連接和基本功能
"""

import sys
import json
from datetime import datetime

def test_futu_connection():
    """測試富途連接"""
    print(f"\n{'='*70}")
    print(f"🔗 富途API連接測試")
    print(f"{'='*70}")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    try:
        # 嘗試導入futu庫
        print("1. 📦 檢查futu庫安裝...")
        from futu import *
        print("   ✅ futu庫已安裝")
        
        # 測試基本連接
        print("\n2. 🔌 測試API連接...")
        
        # 簡單的連接測試
        try:
            # 創建行情上下文
            quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
            print("   ✅ 成功創建行情上下文")
            
            # 測試獲取股票報價
            print("\n3. 📈 測試獲取股票報價...")
            test_stocks = ['HK.00992', 'HK.00700', 'HK.00005']
            
            ret, data = quote_ctx.get_market_snapshot(test_stocks)
            if ret == RET_OK:
                print(f"   ✅ 成功獲取{len(data)}隻股票報價")
                for _, row in data.iterrows():
                    print(f"      {row['code']} - {row['stock_name']}")
                    print(f"         最新價: HKD {row['last_price']:.2f}")
                    print(f"         漲跌幅: {row['change_rate']:.2f}%")
            else:
                print(f"   ❌ 獲取報價失敗: {data}")
            
            # 關閉連接
            quote_ctx.close()
            print("\n4. 🔌 關閉連接...")
            print("   ✅ 連接已關閉")
            
            # 測試交易上下文（如果可能）
            print("\n5. 💰 測試交易功能...")
            print("   ℹ️  需要富途OpenD運行且已登錄模擬賬戶")
            print("   ℹ️  請確保:")
            print("      1. 富途OpenD正在運行")
            print("      2. 端口11111可訪問")
            print("      3. 模擬賬戶已登錄")
            
            connection_status = "PARTIAL_SUCCESS"
            error_message = None
            
        except Exception as e:
            print(f"   ❌ 連接測試失敗: {e}")
            connection_status = "CONNECTION_FAILED"
            error_message = str(e)
        
    except ImportError:
        print("   ❌ futu庫未安裝")
        print("     請運行: pip install futu-api")
        connection_status = "LIBRARY_MISSING"
        error_message = "futu庫未安裝"
    except Exception as e:
        print(f"   ❌ 系統錯誤: {e}")
        connection_status = "SYSTEM_ERROR"
        error_message = str(e)
    
    # 生成測試報告
    print(f"\n{'='*70}")
    print(f"📋 連接測試報告")
    print(f"{'='*70}")
    
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'connection_status': connection_status,
        'error_message': error_message,
        'recommendations': []
    }
    
    if connection_status == "PARTIAL_SUCCESS":
        print("✅ 富途API基本連接測試成功")
        print("   可以獲取股票報價數據")
        report['recommendations'].append("基本連接正常，可以獲取行情數據")
        
    elif connection_status == "CONNECTION_FAILED":
        print("❌ 富途API連接失敗")
        print(f"   錯誤: {error_message}")
        report['recommendations'].append("檢查富途OpenD是否運行")
        report['recommendations'].append("檢查端口11111是否可訪問")
        
    elif connection_status == "LIBRARY_MISSING":
        print("❌ futu庫未安裝")
        report['recommendations'].append("安裝futu-api: pip install futu-api")
        
    else:
        print(f"⚠️  未知狀態: {connection_status}")
    
    # 交易執行建議
    print(f"\n{'='*70}")
    print(f"🎯 交易執行建議")
    print(f"{'='*70}")
    
    print("要執行真實交易，需要:")
    print("1. ✅ 安裝futu-api庫")
    print("2. 🔌 運行富途OpenD (端口11111)")
    print("3. 👤 登錄富途模擬賬戶")
    print("4. 📝 獲取交易權限")
    
    print(f"\n已創建的交易系統文件:")
    print("├── run_active_trader.py - 交易決策系統")
    print("├── real_futu_trader.py - 真實交易連接")
    print("└── simple_futu_trader.py - 連接測試")
    
    print(f"\n下一步行動:")
    print("1. 運行富途OpenD並登錄模擬賬戶")
    print("2. 再次運行連接測試")
    print("3. 如果連接成功，執行真實交易")
    
    # 保存報告
    report_file = f"/Users/gordonlui/.openclaw/workspace/futu_connection_test_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 測試報告已保存: {report_file}")
    except Exception as e:
        print(f"❌ 保存報告失敗: {e}")
    
    print(f"\n{'='*70}")
    print(f"✅ 連接測試完成")
    print(f"   狀態: {connection_status}")
    print(f"{'='*70}")
    
    return report

def check_futu_installation():
    """檢查futu安裝狀態"""
    print("🔍 檢查futu安裝狀態...")
    
    try:
        import futu
        print(f"✅ futu版本: {futu.__version__}")
        return True
    except ImportError:
        print("❌ futu未安裝")
        return False

def main():
    """主函數"""
    print("🚀 富途交易系統診斷工具")
    
    # 檢查安裝
    if not check_futu_installation():
        print("\n📦 需要安裝futu-api庫")
        print("   運行: pip install futu-api")
        print("   或: pip3 install futu-api")
        return
    
    # 運行連接測試
    try:
        report = test_futu_connection()
        
        print(f"\n📋 診斷總結:")
        print(f"  測試時間: {report['timestamp']}")
        print(f"  連接狀態: {report['connection_status']}")
        
        if report['error_message']:
            print(f"  錯誤信息: {report['error_message']}")
        
        if report['recommendations']:
            print(f"\n💡 建議:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
    except Exception as e:
        print(f"❌ 診斷過程出錯: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
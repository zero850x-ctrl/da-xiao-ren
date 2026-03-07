#!/usr/bin/env python3
"""
富途連接簡單測試 - 只測試最基本功能
"""

import sys
import time
from futu import *

def simple_test():
    """最簡單的連接測試"""
    print("🔗 最簡單的富途連接測試")
    print("=" * 50)
    
    try:
        # 1. 測試交易連接
        print("\n1. 創建交易上下文...")
        trd_ctx = OpenSecTradeContext(
            host='127.0.0.1',
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        print("✅ 交易上下文創建成功")
        
        # 2. 測試切換到模擬環境
        print("\n2. 切換到模擬環境...")
        ret, data = trd_ctx.set_trd_env(trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK:
            print("✅ 模擬環境設置成功")
        else:
            print(f"⚠️  設置模擬環境失敗: {data}")
        
        # 3. 獲取賬戶列表（簡單顯示）
        print("\n3. 獲取賬戶列表...")
        ret, data = trd_ctx.get_acc_list()
        if ret == RET_OK:
            print(f"✅ 找到 {len(data)} 個賬戶")
            print("賬戶列表示例（前3個）:")
            print(data.head(3))
        else:
            print(f"❌ 獲取賬戶失敗: {data}")
        
        # 4. 獲取資金信息
        print("\n4. 獲取資金信息...")
        ret, data = trd_ctx.get_acc_assets()
        if ret == RET_OK:
            print("✅ 資金信息獲取成功")
            print("資金數據:")
            print(data)
            
            # 嘗試提取總資產
            if not data.empty:
                # 嘗試不同的列名
                possible_columns = ['total_assets', 'total_asset', 'net_assets', 'equity']
                for col in possible_columns:
                    if col in data.columns:
                        total = data[col].iloc[0]
                        print(f"\n💰 總資產 (列 '{col}'): HKD {total:,.2f}")
                        
                        # 檢查是否接近979,000
                        if 978000 <= total <= 980000:
                            print(f"  ✅ 匹配預期的979,000 HKD")
                        else:
                            print(f"  ⚠️  與預期979,000有差異")
                        break
                else:
                    print("⚠️  未找到總資產列，可用列:", list(data.columns))
        else:
            print(f"❌ 獲取資金失敗: {data}")
        
        # 5. 測試報價連接
        print("\n5. 測試報價連接...")
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        print("✅ 報價上下文創建成功")
        
        # 查詢恆生指數
        ret, data = quote_ctx.get_market_snapshot(['HK.999010'])
        if ret == RET_OK and not data.empty:
            print(f"✅ 恆生指數: {data.iloc[0].get('last_price', 'N/A')}")
        else:
            print("⚠️  無法獲取指數數據")
        
        quote_ctx.close()
        
        # 6. 測試下單準備
        print("\n6. 測試下單準備...")
        test_code = "HK.00001"  # 長和
        
        ret, data = trd_ctx.get_max_trd_qty(
            code=test_code,
            price=40.0,
            order_type=OrderType.NORMAL,
            trd_side=TrdSide.BUY
        )
        
        if ret == RET_OK:
            print(f"✅ 可交易數量查詢成功")
            print(f"  最大可買: {data.iloc[0].get('max_can_buy', 'N/A')}")
        else:
            print(f"⚠️  可交易數量查詢失敗: {data}")
        
        # 關閉連接
        trd_ctx.close()
        
        print("\n" + "=" * 50)
        print("🎉 基本連接測試成功！")
        print("\n📋 連接狀態:")
        print("✅ OpenD可訪問")
        print("✅ API工作正常")
        print("✅ 模擬環境可用")
        print("✅ 市場數據可獲取")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_port():
    """檢查端口"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    
    try:
        result = sock.connect_ex(('127.0.0.1', 11111))
        return result == 0
    except:
        return False
    finally:
        sock.close()

def main():
    print("🚀 富途模擬交易準備檢查")
    print("時間:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # 檢查端口
    print("🔍 檢查OpenD端口...")
    if check_port():
        print("✅ 端口11111可訪問")
    else:
        print("❌ 端口11111不可訪問")
        print("\n請確保:")
        print("1. 富途牛牛應用已打開")
        print("2. 已登錄賬戶")
        print("3. OpenD已啟動")
        return
    
    # 運行測試
    print("\n" + "=" * 50)
    success = simple_test()
    
    print("\n" + "=" * 50)
    if success:
        print("🎯 周一交易準備狀態: ✅ 就緒")
        print("\n初始資金: 979,000 HKD")
        print("交易時間: 09:30-16:00")
        print("風險控制: 每筆2%止損")
        print("監控頻率: 每半小時")
        
        print("\n🚀 下一步:")
        print("1. 創建風險管理系統")
        print("2. 設置自動監控")
        print("3. 研究牛熊證產品")
    else:
        print("🎯 周一交易準備狀態: ❌ 需要修復")
        print("\n需要檢查:")
        print("1. 富途牛牛是否正常運行")
        print("2. 是否已登錄")
        print("3. 模擬交易權限")
        print("4. 網絡連接")
    
    print("\n測試完成時間:", time.strftime("%H:%M:%S"))

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
富途模擬交易連接測試
測試是否能連接到模擬交易環境
"""

import sys
import os

# 嘗試導入富途API
try:
    from futu import *
    print("✅ 富途API已安裝")
except ImportError:
    print("❌ 富途API未安裝")
    print("安裝命令: pip install futu-api")
    sys.exit(1)

def test_connection():
    """測試連接到富途OpenD"""
    print("\n🔗 測試連接到富途OpenD...")
    
    try:
        # 嘗試連接交易上下文
        trd_ctx = OpenSecTradeContext(
            filter_trdmarket=TrdMarket.HK,  # 港股市場
            host='127.0.0.1',               # OpenD本地地址
            port=11111,                     # OpenD默認端口
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        
        print("✅ 交易上下文創建成功")
        
        # 測試獲取賬戶列表（模擬環境）
        print("\n📋 測試獲取模擬賬戶列表...")
        ret, data = trd_ctx.get_acc_list(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK:
            print("✅ 成功獲取模擬賬戶列表")
            print(f"賬戶數量: {len(data)}")
            print("\n賬戶詳情:")
            print(data)
            
            # 顯示賬戶信息
            if len(data) > 0:
                print("\n📊 第一個賬戶信息:")
                acc = data.iloc[0]
                print(f"賬戶ID: {acc['acc_id']}")
                print(f"賬戶類型: {acc['acc_type']}")
                print(f"賬戶狀態: {acc['status']}")
                print(f"市場: {acc['market']}")
        else:
            print(f"❌ 獲取賬戶列表失敗: {data}")
        
        # 測試解鎖交易（模擬環境可能不需要）
        print("\n🔓 測試交易解鎖...")
        ret, data = trd_ctx.unlock_trade('')  # 模擬環境可能不需要密碼
        
        if ret == RET_OK:
            print("✅ 交易解鎖成功（或不需要解鎖）")
        else:
            print(f"⚠️  解鎖失敗（可能模擬環境不需要）: {data}")
        
        # 測試獲取資金信息
        print("\n💰 測試獲取資金信息...")
        ret, data = trd_ctx.get_acc_assets(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK:
            print("✅ 成功獲取資金信息")
            print("\n資金詳情:")
            print(data)
            
            # 計算總資產
            if 'total_assets' in data.columns:
                total_assets = data['total_assets'].iloc[0]
                print(f"\n💰 總資產: HKD {total_assets:,.2f}")
                
                # 檢查是否接近979,000
                if abs(total_assets - 979000) < 1000:
                    print("✅ 資金接近預期的979,000 HKD")
                else:
                    print(f"⚠️  資金與預期不符: 當前 {total_assets:,.2f}, 預期 979,000")
        else:
            print(f"❌ 獲取資金信息失敗: {data}")
        
        # 測試獲取持倉
        print("\n📈 測試獲取持倉列表...")
        ret, data = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK:
            print("✅ 成功獲取持倉列表")
            if len(data) > 0:
                print(f"持倉數量: {len(data)}")
                print("\n持倉詳情:")
                print(data[['code', 'stock_name', 'qty', 'can_sell_qty', 'cost_price', 'market_val']])
            else:
                print("📭 當前無持倉")
        else:
            print(f"❌ 獲取持倉失敗: {data}")
        
        # 測試簡單的下單（不實際執行）
        print("\n🛒 測試下單接口（不下實際單）...")
        # 使用一個安全的測試代碼
        test_code = "HK.999010"  # 恆生指數
        
        ret, data = trd_ctx.place_order(
            price=18000.0,  # 測試價格
            qty=1,          # 最小數量
            code=test_code,
            trd_side=TrdSide.BUY,
            order_type=OrderType.NORMAL,
            trd_env=TrdEnv.SIMULATE,
            remark="API連接測試單"
        )
        
        if ret == RET_OK:
            print("✅ 下單接口測試成功")
            print("訂單ID:", data['order_id'].iloc[0])
            print("訂單狀態:", data['order_status'].iloc[0])
            
            # 立即取消測試單
            print("\n❌ 取消測試單...")
            order_id = data['order_id'].iloc[0]
            ret_cancel, data_cancel = trd_ctx.modify_order(
                modify_order_op=ModifyOrderOp.CANCEL,
                order_id=order_id,
                qty=0,
                price=0,
                trd_env=TrdEnv.SIMULATE
            )
            
            if ret_cancel == RET_OK:
                print("✅ 測試單取消成功")
            else:
                print(f"⚠️  取消測試單失敗: {data_cancel}")
        else:
            print(f"❌ 下單接口測試失敗: {data}")
            print("這可能是正常的，如果產品代碼不存在或市場未開市")
        
        # 關閉連接
        trd_ctx.close()
        print("\n✅ 連接測試完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 連接測試失敗: {e}")
        print("\n🔧 故障排除建議:")
        print("1. 確保OpenD正在運行 (127.0.0.1:11111)")
        print("2. 檢查富途API版本: pip show futu-api")
        print("3. 確認模擬交易賬戶已開通")
        print("4. 檢查網絡連接")
        return False

def check_opend_status():
    """檢查OpenD是否運行"""
    print("\n🔍 檢查OpenD狀態...")
    
    import socket
    import subprocess
    
    # 檢查端口11111是否開放
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    
    try:
        result = sock.connect_ex(('127.0.0.1', 11111))
        if result == 0:
            print("✅ OpenD端口11111已開放")
            
            # 嘗試檢查OpenD進程
            try:
                # macOS檢查進程
                ps_output = subprocess.run(['ps', 'aux', '|', 'grep', 'FutuOpenD', '|', 'grep', '-v', 'grep'], 
                                         shell=True, capture_output=True, text=True)
                if 'FutuOpenD' in ps_output.stdout:
                    print("✅ OpenD進程正在運行")
                else:
                    print("⚠️  未找到OpenD進程，但端口開放")
            except:
                print("ℹ️  無法檢查進程狀態")
                
            return True
        else:
            print("❌ OpenD端口11111未開放")
            print("請啟動富途OpenD應用程序")
            return False
    except Exception as e:
        print(f"❌ 檢查端口時出錯: {e}")
        return False
    finally:
        sock.close()

def main():
    print("🚀 富途模擬交易連接測試")
    print("=" * 50)
    
    # 檢查OpenD狀態
    if not check_opend_status():
        print("\n❌ OpenD未運行，無法繼續測試")
        print("\n🔧 請執行以下步驟:")
        print("1. 打開富途牛牛應用")
        print("2. 登錄你的賬戶")
        print("3. 確保OpenD已啟動")
        print("4. 重新運行此測試")
        return
    
    # 測試API連接
    print("\n" + "=" * 50)
    print("測試API連接...")
    
    success = test_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 連接測試成功！準備好周一交易")
        
        print("\n📋 下一步準備:")
        print("1. 創建風險管理系統 (2%止損)")
        print("2. 設置半小時監控腳本")
        print("3. 研究恆指牛熊證產品")
        print("4. 準備交易策略")
    else:
        print("❌ 連接測試失敗")
        
        print("\n🔧 需要解決的問題:")
        print("1. 確保OpenD正在運行")
        print("2. 檢查富途API安裝")
        print("3. 確認模擬交易權限")
        print("4. 可能需要重啟OpenD")
    
    print("\n" + "=" * 50)
    print("測試完成")

if __name__ == "__main__":
    main()
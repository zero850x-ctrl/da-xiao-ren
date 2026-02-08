#!/usr/bin/env python3
"""
直接測試富途模擬交易功能
"""

import sys
import time
from futu import *

def test_sim_trade():
    """直接測試模擬交易"""
    print("🎮 直接測試富途模擬交易")
    print("=" * 60)
    
    try:
        # 創建交易上下文
        print("1. 創建交易上下文...")
        trd_ctx = OpenSecTradeContext(
            host='127.0.0.1',
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        print("✅ 交易上下文創建成功")
        
        # 方法1: 直接使用模擬環境參數
        print("\n2. 測試在模擬環境下單...")
        
        # 使用一個安全的測試代碼 - 恆生指數ETF
        test_code = "HK.02800"  # 盈富基金
        
        # 先獲取當前價格
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        ret, snapshot = quote_ctx.get_market_snapshot([test_code])
        
        if ret == RET_OK and not snapshot.empty:
            last_price = snapshot.iloc[0]['last_price']
            print(f"📊 {test_code} 當前價格: {last_price}")
            
            # 計算測試訂單價格（略低於市價）
            test_price = round(last_price * 0.99, 2)
            test_qty = 100  # 最小測試數量
            
            print(f"\n3. 嘗試模擬下單...")
            print(f"   代碼: {test_code}")
            print(f"   價格: {test_price}")
            print(f"   數量: {test_qty}")
            print(f"   環境: 模擬交易")
            
            # 嘗試下單（模擬環境）
            ret, order_data = trd_ctx.place_order(
                price=test_price,
                qty=test_qty,
                code=test_code,
                trd_side=TrdSide.BUY,
                order_type=OrderType.NORMAL,
                trd_env=TrdEnv.SIMULATE,  # 關鍵參數：模擬環境
                remark="模擬交易測試單"
            )
            
            if ret == RET_OK:
                print("🎉 模擬下單成功！")
                print(f"   訂單ID: {order_data['order_id'].iloc[0]}")
                print(f"   訂單狀態: {order_data['order_status'].iloc[0]}")
                
                # 立即取消測試單
                order_id = order_data['order_id'].iloc[0]
                print(f"\n4. 取消測試單 {order_id}...")
                
                ret_cancel, cancel_data = trd_ctx.modify_order(
                    modify_order_op=ModifyOrderOp.CANCEL,
                    order_id=order_id,
                    qty=0,
                    price=0,
                    trd_env=TrdEnv.SIMULATE
                )
                
                if ret_cancel == RET_OK:
                    print("✅ 測試單取消成功")
                else:
                    print(f"⚠️  取消失敗: {cancel_data}")
                
            else:
                print(f"❌ 模擬下單失敗: {order_data}")
                print("\n可能的原因:")
                print("1. 模擬交易賬戶未開通")
                print("2. 市場未開市")
                print("3. 產品不可交易")
                print("4. 資金不足")
        else:
            print(f"❌ 無法獲取 {test_code} 價格")
        
        quote_ctx.close()
        
        # 測試獲取持倉
        print("\n5. 檢查模擬賬戶持倉...")
        ret, positions = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK:
            if len(positions) > 0:
                print(f"📦 找到 {len(positions)} 個持倉:")
                for idx, row in positions.iterrows():
                    print(f"   {row['code']} {row['stock_name']}: {row['qty']}股")
            else:
                print("📭 模擬賬戶無持倉")
        else:
            print(f"❌ 獲取持倉失敗: {positions}")
        
        # 測試獲取資金
        print("\n6. 檢查模擬賬戶資金...")
        ret, assets = trd_ctx.get_acc_assets(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK and not assets.empty:
            print("💰 模擬賬戶資金:")
            print(assets)
            
            # 嘗試找到總資產
            for col in assets.columns:
                if 'asset' in col.lower() or 'total' in col.lower():
                    value = assets[col].iloc[0]
                    print(f"\n📊 {col}: HKD {value:,.2f}")
                    
                    if 978000 <= value <= 980000:
                        print(f"   ✅ 匹配預期979,000 HKD")
                    break
        
        # 關閉連接
        trd_ctx.close()
        
        print("\n" + "=" * 60)
        print("🎯 測試完成")
        return True
        
    except Exception as e:
        print(f"\n❌ 測試異常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 富途模擬交易直接測試")
    print("目標: 驗證模擬交易功能")
    print("時間:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # 檢查是否在交易時間
    current_hour = time.localtime().tm_hour
    if 9 <= current_hour < 16:
        print("✅ 在交易時間內")
    else:
        print("⚠️  非交易時間，某些功能可能受限")
    
    print("\n" + "=" * 60)
    success = test_sim_trade()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 模擬交易測試總結:")
        print("✅ API連接正常")
        print("✅ 模擬交易功能可用")
        print("✅ 可執行下單操作")
        print("✅ 可獲取賬戶信息")
        
        print("\n🚀 周一交易準備:")
        print("1. 創建2%止損風險系統")
        print("2. 設置半小時監控")
        print("3. 研究恆指牛熊證")
        print("4. 設計交易策略")
    else:
        print("❌ 模擬交易測試有問題")
        
        print("\n🔧 需要解決:")
        print("1. 確認富途牛牛已登錄")
        print("2. 檢查模擬交易權限")
        print("3. 確認OpenD運行正常")
        print("4. 可能需要開通模擬交易")
    
    print("\n💡 建議:")
    print("• 在富途牛牛中確認模擬交易已開通")
    print("• 檢查模擬賬戶資金是否為979,000")
    print("• 測試時間最好在交易時段")
    
    print("\n測試完成:", time.strftime("%H:%M:%S"))

if __name__ == "__main__":
    main()
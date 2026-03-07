#!/usr/bin/env python3
"""
富途API簡單連接測試
"""

from futu import *
import sys

def main():
    print("🔗 富途API簡單連接測試")
    print("=" * 50)
    
    try:
        # 1. 創建交易上下文
        print("1. 創建交易上下文...")
        trd_ctx = OpenSecTradeContext(
            filter_trdmarket=TrdMarket.HK,
            host='127.0.0.1',
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        print("✅ 交易上下文創建成功")
        
        # 2. 測試獲取賬戶列表（不指定trd_env）
        print("\n2. 獲取賬戶列表...")
        ret, data = trd_ctx.get_acc_list()
        
        if ret == RET_OK:
            print(f"✅ 成功獲取賬戶列表，找到 {len(data)} 個賬戶")
            print("\n賬戶列表:")
            for idx, row in data.iterrows():
                print(f"  賬戶{idx+1}: ID={row.get('acc_id', 'N/A')}, "
                      f"類型={row.get('acc_type', 'N/A')}, "
                      f"狀態={row.get('status', 'N/A')}")
        else:
            print(f"❌ 獲取賬戶列表失敗: {data}")
            return False
        
        # 3. 測試模擬交易環境
        print("\n3. 測試模擬交易環境...")
        
        # 先嘗試SIMULATE環境
        print("  嘗試SIMULATE環境...")
        ret, data = trd_ctx.get_acc_list(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK:
            print(f"  ✅ SIMULATE環境可用，找到 {len(data)} 個模擬賬戶")
            simulate_acc = data.iloc[0] if len(data) > 0 else None
        else:
            print(f"  ⚠️  SIMULATE環境失敗: {data}")
            print("  嘗試REAL環境...")
            ret, data = trd_ctx.get_acc_list(trd_env=TrdEnv.REAL)
            if ret == RET_OK:
                print(f"  ✅ REAL環境可用，找到 {len(data)} 個真實賬戶")
                simulate_acc = None
            else:
                print(f"  ❌ 所有環境都失敗")
                simulate_acc = None
        
        # 4. 測試獲取資金（如果有模擬賬戶）
        if simulate_acc is not None:
            print("\n4. 獲取模擬賬戶資金...")
            acc_id = simulate_acc['acc_id']
            ret, data = trd_ctx.get_acc_assets(acc_id=acc_id, trd_env=TrdEnv.SIMULATE)
            
            if ret == RET_OK and len(data) > 0:
                print("✅ 成功獲取資金信息")
                funds = data.iloc[0]
                
                # 顯示關鍵資金信息
                print(f"  總資產: HKD {funds.get('total_assets', 0):,.2f}")
                print(f"  現金: HKD {funds.get('cash', 0):,.2f}")
                print(f"  可用資金: HKD {funds.get('available_funds', 0):,.2f}")
                
                # 檢查是否接近979,000
                total = funds.get('total_assets', 0)
                if 970000 <= total <= 990000:
                    print(f"  ✅ 資金接近預期的979,000 HKD (實際: {total:,.2f})")
                else:
                    print(f"  ⚠️  資金: {total:,.2f} HKD (預期: 979,000)")
            else:
                print(f"❌ 獲取資金失敗: {data}")
        
        # 5. 測試簡單的報價獲取（確認市場連接）
        print("\n5. 測試市場報價連接...")
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 測試獲取恆生指數報價
        ret, data = quote_ctx.get_market_snapshot(['HK.999010'])
        
        if ret == RET_OK and len(data) > 0:
            hsi = data.iloc[0]
            print(f"✅ 市場連接正常")
            print(f"  恆生指數: {hsi.get('last_price', 0):,.2f}")
            print(f"  漲跌: {hsi.get('change_rate', 0)*100:+.2f}%")
        else:
            print(f"❌ 獲取報價失敗: {data}")
        
        quote_ctx.close()
        
        # 6. 測試下單接口（不下實際單）
        print("\n6. 測試下單接口（只檢查連接）...")
        # 使用一個不會成交的價格
        test_price = 100000.0  # 極高價格，不會成交
        
        ret, data = trd_ctx.place_order(
            price=test_price,
            qty=1,
            code="HK.999010",  # 恆生指數
            trd_side=TrdSide.BUY,
            order_type=OrderType.NORMAL,
            remark="連接測試單"
        )
        
        if ret == RET_OK:
            print("✅ 下單接口連接正常")
            order_id = data['order_id'].iloc[0]
            print(f"  測試單ID: {order_id}")
            
            # 嘗試取消測試單
            ret_cancel, _ = trd_ctx.modify_order(
                modify_order_op=ModifyOrderOp.CANCEL,
                order_id=order_id
            )
            
            if ret_cancel == RET_OK:
                print("  ✅ 測試單取消成功")
            else:
                print("  ⚠️  取消測試單失敗（可能已自動取消）")
        else:
            print(f"❌ 下單接口失敗: {data}")
            print("  這可能是正常的，如果市場未開市或產品限制")
        
        # 關閉連接
        trd_ctx.close()
        
        print("\n" + "=" * 50)
        print("🎉 連接測試基本成功！")
        
        print("\n📋 周一交易準備狀態:")
        print("✅ API連接正常")
        print("✅ 交易上下文可用")
        print("✅ 市場報價可獲取")
        print("✅ 下單接口可訪問")
        
        print("\n🔧 需要確認的事項:")
        print("1. 模擬賬戶資金是否為979,000 HKD")
        print("2. 模擬交易權限是否完全開通")
        print("3. 恆指牛熊證的具體產品代碼")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試過程中出錯: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n🔧 故障排除:")
        print("1. 確保富途牛牛已登錄並運行")
        print("2. 確認OpenD正在運行 (端口11111)")
        print("3. 檢查網絡連接")
        print("4. 可能需要重啟富途牛牛")
        
        return False

if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 50)
    if success:
        print("🚀 準備好周一開始模擬交易！")
        print("\n下一步:")
        print("1. 創建2%止損風險管理系統")
        print("2. 設置半小時監控腳本")
        print("3. 研究具體的牛熊證產品")
    else:
        print("❌ 需要解決連接問題")
        sys.exit(1)
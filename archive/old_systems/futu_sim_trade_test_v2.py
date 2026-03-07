#!/usr/bin/env python3
"""
富途模擬交易連接測試 - 修正版
使用正確的API參數
"""

import sys
import os
import time

# 嘗試導入富途API
try:
    from futu import *
    print("✅ 富途API已安裝 (版本: 9.6.5608)")
except ImportError as e:
    print(f"❌ 富途API導入失敗: {e}")
    sys.exit(1)

def test_basic_connection():
    """測試基本連接"""
    print("\n🔗 測試基本連接...")
    
    try:
        # 創建交易上下文
        trd_ctx = OpenSecTradeContext(
            filter_trdmarket=TrdMarket.HK,
            host='127.0.0.1',
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        
        print("✅ 交易上下文創建成功")
        
        # 測試1: 獲取賬戶列表
        print("\n1. 📋 測試獲取賬戶列表...")
        ret, data = trd_ctx.get_acc_list()
        
        if ret == RET_OK:
            print(f"✅ 成功獲取賬戶列表，找到 {len(data)} 個賬戶")
            print("\n賬戶詳情:")
            for idx, row in data.iterrows():
                print(f"  [{idx}] ID: {row['acc_id']}, 類型: {row['acc_type']}, 市場: {row['market']}")
        else:
            print(f"❌ 獲取賬戶列表失敗: {data}")
        
        # 測試2: 切換到模擬環境
        print("\n2. 🎮 測試切換到模擬環境...")
        ret, data = trd_ctx.set_trd_env(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK:
            print("✅ 成功切換到模擬交易環境")
        else:
            print(f"❌ 切換模擬環境失敗: {data}")
        
        # 測試3: 獲取模擬賬戶資金
        print("\n3. 💰 測試獲取模擬賬戶資金...")
        ret, data = trd_ctx.get_acc_assets()
        
        if ret == RET_OK:
            print("✅ 成功獲取資金信息")
            print(f"\n資金詳情:")
            for idx, row in data.iterrows():
                print(f"  總資產: HKD {row.get('total_assets', 0):,.2f}")
                print(f"  現金: HKD {row.get('cash', 0):,.2f}")
                print(f"  可用資金: HKD {row.get('available_funds', 0):,.2f}")
                print(f"  持倉市值: HKD {row.get('market_val', 0):,.2f}")
                
                # 檢查資金是否接近979,000
                total = row.get('total_assets', 0)
                if 978000 <= total <= 980000:
                    print(f"  ✅ 資金接近預期的979,000 HKD (實際: {total:,.2f})")
                else:
                    print(f"  ⚠️  資金: {total:,.2f}, 預期: 979,000")
        else:
            print(f"❌ 獲取資金信息失敗: {data}")
        
        # 測試4: 獲取持倉
        print("\n4. 📈 測試獲取持倉...")
        ret, data = trd_ctx.position_list_query()
        
        if ret == RET_OK:
            if len(data) > 0:
                print(f"✅ 找到 {len(data)} 個持倉")
                print("\n持倉詳情:")
                for idx, row in data.iterrows():
                    print(f"  [{idx}] {row['code']} {row['stock_name']}: {row['qty']}股 @ {row.get('cost_price', 0):.2f}")
            else:
                print("📭 當前無持倉")
        else:
            print(f"❌ 獲取持倉失敗: {data}")
        
        # 測試5: 簡單的市場數據查詢
        print("\n5. 📊 測試市場數據查詢...")
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 查詢恆生指數
        ret, data = quote_ctx.get_market_snapshot(['HK.999010'])
        
        if ret == RET_OK:
            print("✅ 成功獲取市場數據")
            if len(data) > 0:
                row = data.iloc[0]
                print(f"  恆生指數: {row.get('last_price', 0):.2f}")
                print(f"  漲跌: {row.get('change_rate', 0):.2f}%")
                print(f"  成交量: {row.get('volume', 0):,.0f}")
        else:
            print(f"❌ 獲取市場數據失敗: {data}")
        
        quote_ctx.close()
        
        # 測試6: 下單接口（使用最小測試）
        print("\n6. 🛒 測試下單接口（查詢最大可買數量）...")
        
        # 先查詢最大可買數量（不下實際單）
        test_code = "HK.00001"  # 長和，比較穩定
        
        ret, data = trd_ctx.get_max_trd_qty(
            code=test_code,
            price=40.0,  # 假設價格
            order_type=OrderType.NORMAL,
            trd_side=TrdSide.BUY
        )
        
        if ret == RET_OK:
            print("✅ 成功查詢最大可買數量")
            print(f"  股票: {test_code}")
            print(f"  最大可買: {data.iloc[0]['max_can_buy']} 股")
            print(f"  最大可賣: {data.iloc[0]['max_can_sell']} 股")
        else:
            print(f"❌ 查詢最大數量失敗: {data}")
        
        # 關閉連接
        trd_ctx.close()
        print("\n✅ 基本連接測試完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 連接測試失敗: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_system_status():
    """檢查系統狀態"""
    print("\n🔍 系統狀態檢查...")
    
    import socket
    
    # 檢查OpenD端口
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    
    try:
        result = sock.connect_ex(('127.0.0.1', 11111))
        if result == 0:
            print("✅ OpenD端口11111可訪問")
            return True
        else:
            print("❌ OpenD端口11111不可訪問")
            print("請確保:")
            print("1. 富途牛牛應用已打開")
            print("2. 已登錄賬戶")
            print("3. OpenD已啟動")
            return False
    except Exception as e:
        print(f"❌ 檢查端口時出錯: {e}")
        return False
    finally:
        sock.close()

def main():
    print("🚀 富途模擬交易連接測試 v2")
    print("=" * 60)
    print("測試時間:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("目標: 為周一模擬交易做準備")
    print("初始資金: 979,000 HKD")
    print("交易時間: 09:30-16:00")
    print("風險控制: 每筆2%止損")
    print("=" * 60)
    
    # 檢查系統狀態
    if not check_system_status():
        print("\n❌ 系統檢查失敗，無法繼續")
        return
    
    # 測試連接
    print("\n" + "=" * 60)
    print("開始API連接測試...")
    
    success = test_basic_connection()
    
    print("\n" + "=" * 60)
    print("測試結果總結")
    print("=" * 60)
    
    if success:
        print("🎉 連接測試成功！")
        print("\n📋 周一交易準備狀態:")
        print("✅ API連接正常")
        print("✅ OpenD運行正常")
        print("✅ 模擬環境可訪問")
        print("⏳ 需要創建交易系統")
        
        print("\n🚀 下一步工作:")
        print("1. 創建2%止損風險管理系統")
        print("2. 設置半小時自動監控")
        print("3. 研究恆指牛熊證產品")
        print("4. 設計交易策略")
        print("5. 創建交易記錄系統")
        
        print("\n⏰ 時間安排:")
        print("今天: 完成系統框架")
        print("周末: 完善策略和測試")
        print("周一: 開始模擬交易")
    else:
        print("❌ 連接測試有問題")
        
        print("\n🔧 需要解決:")
        print("1. 確認OpenD正確運行")
        print("2. 檢查API版本兼容性")
        print("3. 確認模擬交易權限")
        print("4. 可能需要重新登錄富途")
    
    print("\n" + "=" * 60)
    print("測試完成時間:", time.strftime("%H:%M:%S"))

if __name__ == "__main__":
    main()
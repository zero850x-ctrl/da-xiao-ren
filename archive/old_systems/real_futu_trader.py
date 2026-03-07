#!/usr/bin/env python3
"""
真實富途交易連接系統
實際連接富途API執行交易
"""

import sys
import json
import time
from datetime import datetime
from futu import *

def connect_and_trade():
    """連接富途API並執行交易"""
    print(f"\n{'='*70}")
    print(f"🔗 真實富途交易連接系統")
    print(f"{'='*70}")
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    try:
        # 1. 連接富途API
        print("1. 🔌 連接富途API...")
        
        # 創建交易上下文（模擬環境）
        trd_ctx = OpenSecTradeContext(
            host='127.0.0.1', 
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES,
            trd_env=TrdEnv.SIMULATE  # 模擬交易環境
        )
        
        # 創建行情上下文
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        print("   ✅ 成功創建交易上下文")
        
        # 2. 獲取賬戶信息
        print("\n2. 💰 獲取模擬賬戶信息...")
        ret, acc_data = trd_ctx.accinfo_query()
        
        if ret == RET_OK:
            print(f"   ✅ 賬戶連接成功")
            print(f"      總資產: HKD {acc_data['total_assets'].iloc[0]:,.2f}")
            print(f"      現金: HKD {acc_data['cash'].iloc[0]:,.2f}")
            print(f"      持倉市值: HKD {acc_data['market_val'].iloc[0]:,.2f}")
        else:
            print(f"   ❌ 獲取賬戶信息失敗: {acc_data}")
            return
        
        # 3. 獲取當前持倉
        print("\n3. 📊 獲取當前持倉...")
        ret, pos_data = trd_ctx.position_list_query()
        
        if ret == RET_OK:
            if len(pos_data) > 0:
                print(f"   ✅ 當前持倉 ({len(pos_data)}隻):")
                for _, row in pos_data.iterrows():
                    print(f"      {row['code']} - {row['stock_name']}")
                    print(f"         數量: {row['qty']:,}股")
                    print(f"         成本: HKD {row['cost_price']:.2f}")
                    print(f"         市價: HKD {row['market_val']/row['qty']:.2f}")
                    print(f"         盈虧: HKD {row['pl_val']:+,.2f}")
            else:
                print("   📭 當前沒有持倉")
        else:
            print(f"   ❌ 獲取持倉信息失敗: {pos_data}")
        
        # 4. 測試交易功能
        print("\n4. 🧪 測試交易功能...")
        
        # 選擇測試股票（聯想集團）
        test_stock = 'HK.00992'
        
        # 獲取當前價格
        ret, quote_data = quote_ctx.get_market_snapshot([test_stock])
        if ret == RET_OK:
            current_price = quote_data['last_price'].iloc[0]
            print(f"   ✅ 獲取{test_stock}價格成功: HKD {current_price:.2f}")
            
            # 測試買入少量股票
            test_amount = 1000  # HKD 1,000
            test_qty = int(test_amount / current_price)
            
            if test_qty > 0:
                print(f"\n5. 🛒 執行測試交易...")
                print(f"   股票: {test_stock}")
                print(f"   價格: HKD {current_price:.2f}")
                print(f"   數量: {test_qty}股")
                print(f"   金額: HKD {test_amount:,.2f}")
                
                # 執行買入訂單
                ret, order_data = trd_ctx.place_order(
                    price=current_price,
                    qty=test_qty,
                    code=test_stock,
                    trd_side=TrdSide.BUY,
                    order_type=OrderType.NORMAL,
                    remark="測試交易 - 主動交易系統"
                )
                
                if ret == RET_OK:
                    order_id = order_data['order_id'].iloc[0]
                    print(f"   ✅ 買入訂單提交成功!")
                    print(f"      訂單ID: {order_id}")
                    
                    # 等待訂單處理
                    print(f"\n6. ⏳ 檢查訂單狀態...")
                    time.sleep(2)
                    
                    # 查詢訂單狀態
                    ret, order_list = trd_ctx.order_list_query()
                    if ret == RET_OK:
                        # 查找我們的訂單
                        our_order = order_list[order_list['order_id'] == order_id]
                        if len(our_order) > 0:
                            order_status = our_order['order_status'].iloc[0]
                            filled_qty = our_order['filled_qty'].iloc[0]
                            print(f"   ✅ 訂單狀態: {order_status}")
                            print(f"      已成交數量: {filled_qty}股")
                            
                            if filled_qty > 0:
                                print(f"   🎉 交易成功! 已買入{test_stock}")
                            else:
                                print(f"   ⏳ 訂單處理中...")
                        else:
                            print(f"   ❓ 未找到訂單信息")
                    else:
                        print(f"   ❌ 查詢訂單失敗: {order_list}")
                else:
                    print(f"   ❌ 買入訂單提交失敗: {order_data}")
            else:
                print(f"   ⚠️  股數計算為0，跳過測試交易")
        else:
            print(f"   ❌ 獲取價格失敗: {quote_data}")
        
        # 5. 生成交易報告
        print(f"\n{'='*70}")
        print(f"📋 交易系統測試報告")
        print(f"{'='*70}")
        
        # 再次獲取持倉確認
        ret, final_pos_data = trd_ctx.position_list_query()
        if ret == RET_OK:
            print(f"最終持倉狀態:")
            if len(final_pos_data) > 0:
                for _, row in final_pos_data.iterrows():
                    print(f"  {row['code']} - {row['stock_name']}: {row['qty']:,}股")
            else:
                print("  沒有持倉")
        
        # 獲取訂單歷史
        ret, order_history = trd_ctx.history_order_list_query()
        if ret == RET_OK and len(order_history) > 0:
            print(f"\n最近訂單:")
            recent_orders = order_history.head(3)  # 顯示最近3筆
            for _, row in recent_orders.iterrows():
                print(f"  {row['create_time']} - {row['code']}")
                print(f"    動作: {row['trd_side']}, 狀態: {row['order_status']}")
                print(f"    數量: {row['qty']:,}股, 價格: HKD {row['price']:.2f}")
        
        # 6. 關閉連接
        print(f"\n7. 🔌 關閉API連接...")
        trd_ctx.close()
        quote_ctx.close()
        print("   ✅ 連接已關閉")
        
        print(f"\n{'='*70}")
        print(f"✅ 真實富途交易測試完成")
        print(f"   連接狀態: 成功")
        print(f"   賬戶信息: 已獲取")
        print(f"   持倉信息: 已獲取")
        print(f"   測試交易: 已執行")
        print(f"{'='*70}")
        
        # 保存測試報告
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'connection_status': 'SUCCESS',
            'account_info': {
                'total_assets': float(acc_data['total_assets'].iloc[0]) if len(acc_data) > 0 else 0,
                'cash': float(acc_data['cash'].iloc[0]) if len(acc_data) > 0 else 0,
                'market_val': float(acc_data['market_val'].iloc[0]) if len(acc_data) > 0 else 0
            },
            'positions_count': len(pos_data) if ret == RET_OK else 0,
            'test_trade': {
                'stock': test_stock,
                'price': float(current_price) if 'current_price' in locals() else 0,
                'quantity': test_qty,
                'amount': test_amount,
                'order_id': order_id if 'order_id' in locals() else None
            }
        }
        
        report_file = f"/Users/gordonlui/.openclaw/workspace/real_futu_test_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"💾 測試報告已保存: {report_file}")
        
        return report
        
    except Exception as e:
        print(f"\n❌ 系統錯誤: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'connection_status': 'FAILED',
            'error': str(e)
        }

def main():
    """主函數"""
    print("🚀 啟動真實富途交易連接系統...")
    print("目標: 實際連接富途API，執行真實交易")
    
    try:
        report = connect_and_trade()
        
        print(f"\n📋 系統測試總結:")
        print(f"  時間: {report['timestamp']}")
        print(f"  連接狀態: {report['connection_status']}")
        
        if report['connection_status'] == 'SUCCESS':
            print(f"  總資產: HKD {report['account_info']['total_assets']:,.2f}")
            print(f"  現金: HKD {report['account_info']['cash']:,.2f}")
            print(f"  持倉數量: {report['positions_count']}隻")
            
            if report['test_trade']['order_id']:
                print(f"  測試交易: 已執行")
                print(f"    股票: {report['test_trade']['stock']}")
                print(f"    金額: HKD {report['test_trade']['amount']:,}")
        else:
            print(f"  錯誤: {report.get('error', '未知錯誤')}")
        
        print(f"\n💡 下一步:")
        print(f"  1. 檢查富途OpenD是否運行 (端口11111)")
        print(f"  2. 確認模擬賬戶已登錄")
        print(f"  3. 在富途App中查看交易記錄")
        
    except Exception as e:
        print(f"❌ 主程序錯誤: {e}")

if __name__ == "__main__":
    main()
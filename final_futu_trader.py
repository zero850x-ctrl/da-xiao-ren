#!/usr/bin/env python3
"""
最終富途交易執行
簡單可靠的交易執行
"""

import sys
import json
import time
from datetime import datetime
from futu import *

def execute_simple_trade():
    """執行簡單交易"""
    print(f"\n{'='*70}")
    print(f"💰 富途模擬交易執行")
    print(f"{'='*70}")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    try:
        # 連接API
        print("1. 🔌 連接富途API...")
        trd_ctx = OpenSecTradeContext(host='127.0.0.1', port=11111)
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        print("   ✅ 連接成功")
        
        # 檢查賬戶
        print("\n2. 💳 檢查模擬賬戶...")
        ret, acc_data = trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK:
            cash = acc_data['cash'].iloc[0]
            print(f"   ✅ 現金: HKD {cash:,.2f}")
        else:
            print(f"   ❌ 獲取賬戶失敗")
            return
        
        # 選擇一隻股票執行簡單交易
        print("\n3. 🎯 選擇交易股票...")
        
        # 小鵬汽車-W (09868) - 每手100股
        stock_code = 'HK.09868'
        stock_name = '小鵬汽車-W'
        
        # 獲取價格
        ret, quote_data = quote_ctx.get_market_snapshot([stock_code])
        if ret != RET_OK:
            print(f"   ❌ 獲取價格失敗")
            return
        
        current_price = quote_data['last_price'].iloc[0]
        print(f"   📈 {stock_code} - {stock_name}")
        print(f"      當前價格: HKD {current_price:.2f}")
        print(f"      每手股數: 100股")
        
        # 計算購買1手
        quantity = 100  # 1手
        trade_amount = quantity * current_price
        
        if trade_amount > cash:
            print(f"   ❌ 現金不足")
            return
        
        print(f"      計劃購買: 1手 (100股)")
        print(f"      交易金額: HKD {trade_amount:,.2f}")
        
        # 執行交易
        print(f"\n4. ⚡ 執行買入交易...")
        
        ret, order_data = trd_ctx.place_order(
            price=current_price,
            qty=quantity,
            code=stock_code,
            trd_side=TrdSide.BUY,
            order_type=OrderType.NORMAL,
            trd_env=TrdEnv.SIMULATE,
            remark="主動交易系統測試"
        )
        
        if ret == RET_OK:
            order_id = order_data['order_id'].iloc[0]
            print(f"   ✅ 訂單提交成功!")
            print(f"      訂單ID: {order_id}")
            
            # 等待訂單處理
            print(f"\n5. ⏳ 等待訂單處理...")
            time.sleep(3)
            
            # 檢查訂單狀態
            ret, order_list = trd_ctx.order_list_query(trd_env=TrdEnv.SIMULATE)
            if ret == RET_OK:
                # 查找我們的訂單
                order_found = False
                for _, row in order_list.iterrows():
                    if str(row['order_id']) == str(order_id):
                        order_found = True
                        print(f"   📋 訂單狀態:")
                        print(f"      訂單ID: {row['order_id']}")
                        print(f"      狀態: {row['order_status']}")
                        print(f"      股票: {row['code']}")
                        print(f"      數量: {row['qty']}股")
                        print(f"      價格: HKD {row['price']:.2f}")
                        break
                
                if not order_found:
                    print(f"   ❓ 未找到訂單信息")
            else:
                print(f"   ❌ 查詢訂單失敗")
            
        else:
            print(f"   ❌ 訂單提交失敗: {order_data}")
        
        # 檢查最終持倉
        print(f"\n6. 📊 檢查最終持倉...")
        ret, pos_data = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK:
            print(f"   持倉股票: {len(pos_data)}隻")
            if len(pos_data) > 0:
                # 檢查是否有小鵬汽車
                xpeng_pos = pos_data[pos_data['code'] == stock_code]
                if len(xpeng_pos) > 0:
                    print(f"   🎉 成功買入{stock_code}!")
                    qty = xpeng_pos['qty'].iloc[0]
                    cost = xpeng_pos['cost_price'].iloc[0]
                    print(f"      數量: {qty:,}股")
                    print(f"      成本: HKD {cost:.2f}")
                else:
                    print(f"   ⚠️  未找到{stock_code}持倉")
        
        # 關閉連接
        print(f"\n7. 🔌 關閉API連接...")
        trd_ctx.close()
        quote_ctx.close()
        print("   ✅ 連接已關閉")
        
        # 生成報告
        print(f"\n{'='*70}")
        print(f"📋 交易執行報告")
        print(f"{'='*70}")
        
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stock': stock_code,
            'stock_name': stock_name,
            'price': float(current_price),
            'quantity': quantity,
            'amount': trade_amount,
            'order_id': order_id if 'order_id' in locals() else None,
            'cash_before': float(cash),
            'status': 'SUBMITTED'
        }
        
        print(f"交易詳情:")
        print(f"   股票: {report['stock']} - {report['stock_name']}")
        print(f"   價格: HKD {report['price']:.2f}")
        print(f"   數量: {report['quantity']}股")
        print(f"   金額: HKD {report['amount']:,.2f}")
        print(f"   訂單ID: {report['order_id']}")
        print(f"   執行時間: {report['timestamp']}")
        
        # 保存報告
        report_file = f"/Users/gordonlui/.openclaw/workspace/final_trade_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 交易報告已保存: {report_file}")
        
        print(f"\n{'='*70}")
        print(f"✅ 交易執行完成")
        print(f"   請在富途App中查看交易記錄")
        print(f"{'='*70}")
        
        return report
        
    except Exception as e:
        print(f"\n❌ 交易錯誤: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'ERROR',
            'error': str(e)
        }

def main():
    """主函數"""
    print("🚀 富途模擬交易執行系統")
    print("執行簡單可靠的交易測試")
    
    try:
        report = execute_simple_trade()
        
        print(f"\n📋 執行總結:")
        print(f"   時間: {report['timestamp']}")
        
        if 'error' in report:
            print(f"   狀態: 錯誤")
            print(f"   錯誤: {report['error']}")
        else:
            print(f"   狀態: 已提交")
            print(f"   股票: {report['stock']}")
            print(f"   金額: HKD {report['amount']:,}")
            print(f"   訂單ID: {report['order_id']}")
        
        print(f"\n💡 下一步:")
        print(f"   1. 打開富途App")
        print(f"   2. 查看模擬賬戶交易記錄")
        print(f"   3. 確認持倉是否更新")
        print(f"   4. 檢查訂單狀態")
        
    except Exception as e:
        print(f"❌ 系統錯誤: {e}")

if __name__ == "__main__":
    main()
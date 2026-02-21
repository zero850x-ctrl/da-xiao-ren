#!/usr/bin/env python3
"""
執行真實富途交易
在模擬賬戶中實際買賣股票
"""

import sys
import json
import time
from datetime import datetime
from futu import *

def execute_real_trade():
    """執行真實交易"""
    print(f"\n{'='*70}")
    print(f"💰 執行真實富途交易")
    print(f"{'='*70}")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"環境: 模擬交易")
    print(f"{'='*70}")
    
    try:
        # 1. 連接富途交易API
        print("1. 🔌 連接富途交易API...")
        
        # 創建交易上下文
        trd_ctx = OpenSecTradeContext(
            host='127.0.0.1', 
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        
        # 創建行情上下文
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        print("   ✅ API連接成功")
        
        # 2. 檢查賬戶狀態
        print("\n2. 💳 檢查模擬賬戶...")
        ret, acc_data = trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK:
            print(f"   ✅ 賬戶信息獲取成功")
            cash = acc_data['cash'].iloc[0]
            total_assets = acc_data['total_assets'].iloc[0]
            print(f"      現金: HKD {cash:,.2f}")
            print(f"      總資產: HKD {total_assets:,.2f}")
        else:
            print(f"   ❌ 獲取賬戶信息失敗: {acc_data}")
            return
        
        # 3. 檢查當前持倉
        print("\n3. 📊 檢查當前持倉...")
        ret, pos_data = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK:
            if len(pos_data) > 0:
                print(f"   ✅ 當前持倉 ({len(pos_data)}隻):")
                for _, row in pos_data.iterrows():
                    profit_pct = (row['pl_val'] / (row['cost_price'] * row['qty'])) * 100
                    print(f"      {row['code']} - {row['stock_name']}")
                    print(f"         數量: {row['qty']:,}股")
                    print(f"         成本: HKD {row['cost_price']:.2f}")
                    print(f"         盈虧: HKD {row['pl_val']:+,.2f} ({profit_pct:+.2f}%)")
            else:
                print("   📭 當前沒有持倉")
        else:
            print(f"   ❌ 獲取持倉失敗: {pos_data}")
        
        # 4. 選擇交易股票
        print(f"\n4. 🎯 選擇交易股票...")
        
        # 根據之前的分析選擇股票
        trade_candidates = [
            {
                'code': 'HK.09868',
                'name': '小鵬汽車-W',
                'reason': '技術突破，動能強勁',
                'strategy': 'MOMENTUM',
                'amount': 5000  # HKD 5,000
            },
            {
                'code': 'HK.00883', 
                'name': '中國海洋石油',
                'reason': '高股息率6.5%，收息投資',
                'strategy': 'DIVIDEND',
                'amount': 5000  # HKD 5,000
            }
        ]
        
        print(f"   候選股票 ({len(trade_candidates)}隻):")
        for stock in trade_candidates:
            print(f"      {stock['code']} - {stock['name']}")
            print(f"         策略: {stock['strategy']}")
            print(f"         金額: HKD {stock['amount']:,}")
            print(f"         理由: {stock['reason']}")
        
        # 5. 執行交易
        print(f"\n5. 🛒 執行交易...")
        
        executed_trades = []
        
        for stock in trade_candidates:
            stock_code = stock['code']
            trade_amount = stock['amount']
            
            print(f"\n   📈 處理 {stock_code} - {stock['name']}...")
            
            # 獲取當前價格
            ret, quote_data = quote_ctx.get_market_snapshot([stock_code])
            if ret != RET_OK:
                print(f"      ❌ 獲取價格失敗: {quote_data}")
                continue
            
            current_price = quote_data['last_price'].iloc[0]
            quantity = int(trade_amount / current_price)
            
            if quantity <= 0:
                print(f"      ⚠️  股數為0，跳過")
                continue
            
            print(f"      當前價格: HKD {current_price:.2f}")
            print(f"      計劃買入: {quantity:,}股")
            print(f"      交易金額: HKD {trade_amount:,}")
            
            # 確認執行
            print(f"      ⚡ 執行買入訂單...")
            
            ret, order_data = trd_ctx.place_order(
                price=current_price,
                qty=quantity,
                code=stock_code,
                trd_side=TrdSide.BUY,
                order_type=OrderType.NORMAL,
                trd_env=TrdEnv.SIMULATE,
                remark=f"主動交易系統 - {stock['strategy']}策略"
            )
            
            if ret == RET_OK:
                order_id = order_data['order_id'].iloc[0]
                print(f"      ✅ 訂單提交成功!")
                print(f"         訂單ID: {order_id}")
                
                # 記錄交易
                trade_record = {
                    'order_id': order_id,
                    'stock_code': stock_code,
                    'stock_name': stock['name'],
                    'action': 'BUY',
                    'price': float(current_price),
                    'quantity': quantity,
                    'amount': trade_amount,
                    'strategy': stock['strategy'],
                    'reason': stock['reason'],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                executed_trades.append(trade_record)
                
                # 等待一下讓訂單處理
                time.sleep(1)
                
            else:
                print(f"      ❌ 訂單提交失敗: {order_data}")
        
        # 6. 檢查訂單狀態
        print(f"\n6. 📋 檢查訂單狀態...")
        
        if executed_trades:
            ret, order_list = trd_ctx.order_list_query(trd_env=TrdEnv.SIMULATE)
            if ret == RET_OK:
                for trade in executed_trades:
                    order_id = trade['order_id']
                    order_info = order_list[order_list['order_id'] == order_id]
                    
                    if len(order_info) > 0:
                        status = order_info['order_status'].iloc[0]
                        filled_qty = order_info['filled_qty'].iloc[0]
                        
                        print(f"   訂單 {order_id}:")
                        print(f"      狀態: {status}")
                        print(f"      已成交: {filled_qty}/{trade['quantity']}股")
                        
                        if filled_qty > 0:
                            trade['status'] = 'FILLED'
                            trade['filled_quantity'] = int(filled_qty)
                        else:
                            trade['status'] = status
                    else:
                        print(f"   ❓ 未找到訂單 {order_id}")
                        trade['status'] = 'UNKNOWN'
            else:
                print(f"   ❌ 查詢訂單失敗: {order_list}")
        else:
            print("   沒有執行交易")
        
        # 7. 最終持倉檢查
        print(f"\n7. 📊 最終持倉檢查...")
        
        ret, final_pos = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK:
            print(f"   持倉股票: {len(final_pos)}隻")
            if len(final_pos) > 0:
                for _, row in final_pos.iterrows():
                    print(f"      {row['code']} - {row['stock_name']}: {row['qty']:,}股")
        
        # 8. 關閉連接
        print(f"\n8. 🔌 關閉API連接...")
        trd_ctx.close()
        quote_ctx.close()
        print("   ✅ 連接已關閉")
        
        # 9. 生成交易報告
        print(f"\n{'='*70}")
        print(f"📋 交易執行報告")
        print(f"{'='*70}")
        
        total_trades = len(executed_trades)
        successful_trades = len([t for t in executed_trades if t.get('status') == 'FILLED'])
        
        print(f"交易總結:")
        print(f"   計劃交易: {total_trades} 筆")
        print(f"   成功交易: {successful_trades} 筆")
        
        if executed_trades:
            print(f"\n詳細交易記錄:")
            for trade in executed_trades:
                print(f"   {trade['stock_code']} - {trade['stock_name']}")
                print(f"      動作: {trade['action']}")
                print(f"      價格: HKD {trade['price']:.2f}")
                print(f"      數量: {trade['quantity']}股")
                print(f"      金額: HKD {trade['amount']:,}")
                print(f"      策略: {trade['strategy']}")
                print(f"      狀態: {trade.get('status', 'UNKNOWN')}")
                print(f"      時間: {trade['timestamp']}")
                print()
        
        # 保存詳細報告
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'account_info': {
                'cash': float(cash),
                'total_assets': float(total_assets)
            },
            'trades_executed': executed_trades,
            'summary': {
                'total_trades': total_trades,
                'successful_trades': successful_trades,
                'total_amount': sum(t['amount'] for t in executed_trades)
            }
        }
        
        report_file = f"/Users/gordonlui/.openclaw/workspace/real_trade_execution_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 交易報告已保存: {report_file}")
        
        print(f"\n{'='*70}")
        print(f"✅ 真實交易執行完成")
        print(f"   請在富途App中查看交易記錄")
        print(f"{'='*70}")
        
        return report
        
    except Exception as e:
        print(f"\n❌ 交易執行錯誤: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'ERROR',
            'error': str(e)
        }

def main():
    """主函數"""
    print("🚀 啟動真實富途交易執行系統")
    print("警告: 這將在模擬賬戶中執行真實交易!")
    
    # 確認
    print(f"\n⚠️  確認執行真實交易?")
    print(f"   環境: 富途模擬交易")
    print(f"   金額: 每隻股票約HKD 5,000")
    print(f"   股票: 小鵬汽車-W, 中國海洋石油")
    
    # 在實際環境中，這裡應該有用戶確認
    # 但由於這是模擬環境，我們直接執行
    
    try:
        report = execute_real_trade()
        
        print(f"\n📋 執行總結:")
        print(f"   時間: {report['timestamp']}")
        
        if 'account_info' in report:
            print(f"   現金: HKD {report['account_info']['cash']:,.2f}")
            print(f"   交易筆數: {report['summary']['total_trades']}")
            print(f"   成功筆數: {report['summary']['successful_trades']}")
            print(f"   總金額: HKD {report['summary']['total_amount']:,}")
        
        print(f"\n💡 下一步:")
        print(f"   1. 打開富途App查看交易記錄")
        print(f"   2. 檢查持倉是否更新")
        print(f"   3. 監控交易表現")
        
    except Exception as e:
        print(f"❌ 系統錯誤: {e}")

if __name__ == "__main__":
    main()
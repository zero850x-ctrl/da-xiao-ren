#!/usr/bin/env python3
"""
大規模交易執行
根據97萬資產規模進行交易
"""

import sys
import json
import time
from datetime import datetime
from futu import *

def execute_large_scale_trade():
    """執行大規模交易"""
    print(f"\n{'='*70}")
    print(f"💰 大規模交易執行 (97萬資產)")
    print(f"{'='*70}")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    try:
        # 連接API
        print("1. 🔌 連接富途API...")
        trd_ctx = OpenSecTradeContext(host='127.0.0.1', port=11111)
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        print("   ✅ 連接成功")
        
        # 獲取賬戶信息
        print("\n2. 💳 檢查賬戶資產...")
        ret, acc_data = trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE)
        if ret != RET_OK:
            print("   ❌ 獲取賬戶失敗")
            return
        
        total_assets = acc_data['total_assets'].iloc[0]
        cash = acc_data['cash'].iloc[0]
        
        print(f"   📊 賬戶總資產: HKD {total_assets:,.2f}")
        print(f"   💰 可用現金: HKD {cash:,.2f}")
        
        # 計算交易規模
        print("\n3. 📈 計算交易規模...")
        
        # 基於總資產的百分比
        trade_percentages = {
            'conservative': 0.03,  # 3%
            'moderate': 0.05,      # 5%
            'aggressive': 0.08     # 8%
        }
        
        selected_percentage = trade_percentages['moderate']  # 使用中等規模
        trade_amount = total_assets * selected_percentage
        
        print(f"   交易策略: 中等規模 ({selected_percentage*100:.0f}%)")
        print(f"   計劃交易金額: HKD {trade_amount:,.2f}")
        
        if trade_amount > cash:
            print(f"   ⚠️  現金不足，調整為可用現金")
            trade_amount = cash * 0.8  # 使用80%現金
        
        print(f"   實際交易金額: HKD {trade_amount:,.2f}")
        
        # 選擇交易股票
        print("\n4. 🎯 選擇交易股票...")
        
        trade_candidates = [
            {
                'code': 'HK.09868',
                'name': '小鵬汽車-W',
                'reason': '技術突破，動能強勁',
                'strategy': 'MOMENTUM',
                'lot_size': 100,
                'weight': 0.4  # 40%資金
            },
            {
                'code': 'HK.00883',
                'name': '中國海洋石油',
                'reason': '高股息率6.5%，收息投資',
                'strategy': 'DIVIDEND',
                'lot_size': 1000,
                'weight': 0.3  # 30%資金
            },
            {
                'code': 'HK.02020',
                'name': '安踏體育',
                'reason': '行業龍頭，估值合理',
                'strategy': 'VALUE',
                'lot_size': 200,
                'weight': 0.3  # 30%資金
            }
        ]
        
        print(f"   候選股票 ({len(trade_candidates)}隻):")
        
        executed_trades = []
        
        for stock in trade_candidates:
            stock_code = stock['code']
            stock_weight = stock['weight']
            lot_size = stock['lot_size']
            
            # 計算該股票的投資金額
            stock_amount = trade_amount * stock_weight
            
            print(f"\n   📊 分析 {stock_code} - {stock['name']}...")
            
            # 獲取當前價格
            ret, quote_data = quote_ctx.get_market_snapshot([stock_code])
            if ret != RET_OK:
                print(f"      ❌ 獲取價格失敗")
                continue
            
            current_price = quote_data['last_price'].iloc[0]
            
            # 計算整手數量
            target_lots = int(stock_amount / (current_price * lot_size))
            
            if target_lots <= 0:
                print(f"      ⚠️  金額不足購買1手，跳過")
                continue
            
            quantity = target_lots * lot_size
            actual_amount = quantity * current_price
            
            print(f"      當前價格: HKD {current_price:.2f}")
            print(f"      每手股數: {lot_size:,}股")
            print(f"      計劃購買: {target_lots}手 ({quantity:,}股)")
            print(f"      交易金額: HKD {actual_amount:,.2f}")
            print(f"      佔總資金: {(actual_amount/total_assets*100):.1f}%")
            print(f"      交易策略: {stock['strategy']}")
            print(f"      交易理由: {stock['reason']}")
            
            # 確認執行
            confirm = True  # 在實際環境中應該有用戶確認
            
            if confirm:
                print(f"      ⚡ 執行買入訂單...")
                
                ret, order_data = trd_ctx.place_order(
                    price=current_price,
                    qty=quantity,
                    code=stock_code,
                    trd_side=TrdSide.BUY,
                    order_type=OrderType.NORMAL,
                    trd_env=TrdEnv.SIMULATE,
                    remark=f"大規模交易 - {stock['strategy']}"
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
                        'lots': target_lots,
                        'quantity': quantity,
                        'amount': actual_amount,
                        'strategy': stock['strategy'],
                        'reason': stock['reason'],
                        'weight_percentage': (actual_amount/total_assets*100),
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    executed_trades.append(trade_record)
                    
                    time.sleep(1)  # 等待訂單處理
                    
                else:
                    print(f"      ❌ 訂單提交失敗: {order_data}")
        
        # 檢查訂單狀態
        print(f"\n5. 📋 檢查訂單狀態...")
        
        if executed_trades:
            ret, order_list = trd_ctx.order_list_query(trd_env=TrdEnv.SIMULATE)
            if ret == RET_OK:
                for trade in executed_trades:
                    order_id = trade['order_id']
                    # 在訂單列表中查找
                    order_found = False
                    for _, row in order_list.iterrows():
                        if str(row['order_id']) == str(order_id):
                            order_found = True
                            status = row['order_status']
                            print(f"   訂單 {order_id}:")
                            print(f"      狀態: {status}")
                            print(f"      股票: {row['code']}")
                            print(f"      數量: {row['qty']}股")
                            print(f"      價格: HKD {row['price']:.2f}")
                            
                            if status in ['FILLED', 'PARTIAL_FILLED']:
                                trade['status'] = 'FILLED'
                                print(f"      🎉 交易成功!")
                            else:
                                trade['status'] = status
                            break
                    
                    if not order_found:
                        print(f"   ❓ 未找到訂單 {order_id}")
                        trade['status'] = 'UNKNOWN'
        
        # 最終持倉檢查
        print(f"\n6. 📊 最終持倉檢查...")
        ret, final_pos = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK:
            print(f"   總持倉: {len(final_pos)}隻股票")
            if len(final_pos) > 0:
                # 顯示新買入的股票
                new_stocks = [t['stock_code'] for t in executed_trades]
                for stock_code in new_stocks:
                    stock_pos = final_pos[final_pos['code'] == stock_code]
                    if len(stock_pos) > 0:
                        row = stock_pos.iloc[0]
                        print(f"      {row['code']} - {row['stock_name']}: {row['qty']:,}股")
        
        # 關閉連接
        trd_ctx.close()
        quote_ctx.close()
        print(f"\n7. 🔌 關閉API連接...")
        print("   ✅ 連接已關閉")
        
        # 生成報告
        print(f"\n{'='*70}")
        print(f"📋 大規模交易報告")
        print(f"{'='*70}")
        
        if executed_trades:
            total_trades = len(executed_trades)
            total_amount = sum(t['amount'] for t in executed_trades)
            successful_trades = len([t for t in executed_trades if t.get('status') == 'FILLED'])
            
            print(f"交易總結:")
            print(f"   總資產: HKD {total_assets:,.2f}")
            print(f"   計劃交易: {total_trades} 筆")
            print(f"   成功交易: {successful_trades} 筆")
            print(f"   總交易金額: HKD {total_amount:,.2f}")
            print(f"   佔總資產: {(total_amount/total_assets*100):.1f}%")
            
            print(f"\n詳細交易記錄:")
            for trade in executed_trades:
                print(f"   {trade['stock_code']} - {trade['stock_name']}")
                print(f"      策略: {trade['strategy']}")
                print(f"      價格: HKD {trade['price']:.2f}")
                print(f"      數量: {trade['lots']}手 ({trade['quantity']:,}股)")
                print(f"      金額: HKD {trade['amount']:,.2f}")
                print(f"      佔比: {trade['weight_percentage']:.1f}%")
                print(f"      狀態: {trade.get('status', 'UNKNOWN')}")
                print()
        else:
            print("沒有執行交易")
        
        # 保存報告
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'account_info': {
                'total_assets': float(total_assets),
                'cash': float(cash)
            },
            'trade_strategy': {
                'percentage': selected_percentage,
                'planned_amount': float(trade_amount)
            },
            'trades_executed': executed_trades,
            'summary': {
                'total_trades': len(executed_trades),
                'successful_trades': len([t for t in executed_trades if t.get('status') == 'FILLED']),
                'total_amount': sum(t['amount'] for t in executed_trades),
                'percentage_of_assets': (sum(t['amount'] for t in executed_trades) / total_assets * 100) if executed_trades else 0
            }
        }
        
        report_file = f"/Users/gordonlui/.openclaw/workspace/large_scale_trade_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 交易報告已保存: {report_file}")
        
        print(f"\n{'='*70}")
        print(f"✅ 大規模交易執行完成")
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
    print("🚀 啟動大規模交易執行系統")
    print("基於97萬資產規模進行交易")
    
    try:
        report = execute_large_scale_trade()
        
        print(f"\n📋 執行總結:")
        print(f"   時間: {report['timestamp']}")
        
        if 'error' in report:
            print(f"   狀態: 錯誤")
            print(f"   錯誤: {report['error']}")
        else:
            print(f"   總資產: HKD {report['account_info']['total_assets']:,.2f}")
            print(f"   交易策略: {report['trade_strategy']['percentage']*100:.0f}% 資產")
            print(f"   執行交易: {report['summary']['total_trades']} 筆")
            print(f"   總金額: HKD {report['summary']['total_amount']:,}")
            print(f"   佔資產: {report['summary']['percentage_of_assets']:.1f}%")
        
        print(f"\n💡 下一步:")
        print(f"   1. 打開富途App查看交易記錄")
        print(f"   2. 檢查持倉是否更新")
        print(f"   3. 監控新買入股票的表現")
        print(f"   4. 考慮設置止損訂單")
        
    except Exception as e:
        print(f"❌ 系統錯誤: {e}")

if __name__ == "__main__":
    main()
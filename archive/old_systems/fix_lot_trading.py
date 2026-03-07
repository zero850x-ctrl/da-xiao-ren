#!/usr/bin/env python3
"""
修正碎股問題，執行整手交易
"""

import sys
import json
import time
from datetime import datetime
from futu import *

def get_lot_size(stock_code):
    """獲取股票每手股數"""
    # 常見港股的每手股數
    lot_sizes = {
        'HK.00700': 100,   # 騰訊
        'HK.00992': 1000,  # 聯想
        'HK.00005': 400,   # 匯豐
        'HK.09868': 100,   # 小鵬汽車
        'HK.00883': 1000,  # 中海油
        'HK.02020': 200,   # 安踏
        'HK.09988': 100,   # 阿里
        'HK.09618': 50,    # 京東
        'HK.02800': 500,   # 盈富基金
        'HK.01398': 1000,  # 工行
        'HK.02638': 500,   # 港燈
    }
    
    return lot_sizes.get(stock_code, 100)  # 默認100股

def execute_proper_trade():
    """執行正確的整手交易"""
    print(f"\n{'='*70}")
    print(f"🔄 修正碎股問題，執行整手交易")
    print(f"{'='*70}")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    try:
        # 連接API
        trd_ctx = OpenSecTradeContext(host='127.0.0.1', port=11111)
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        print("✅ API連接成功")
        
        # 獲取賬戶信息
        ret, acc_data = trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE)
        if ret != RET_OK:
            print("❌ 獲取賬戶信息失敗")
            return
        
        cash = acc_data['cash'].iloc[0]
        print(f"💰 可用現金: HKD {cash:,.2f}")
        
        # 選擇交易股票（調整為整手）
        trade_candidates = [
            {
                'code': 'HK.09868',  # 小鵬汽車-W
                'name': '小鵬汽車-W',
                'reason': '技術突破，動能強勁',
                'strategy': 'MOMENTUM',
                'target_amount': 10000,  # HKD 10,000
                'lot_size': 100  # 每手100股
            },
            {
                'code': 'HK.00883',  # 中國海洋石油
                'name': '中國海洋石油', 
                'reason': '高股息率6.5%，收息投資',
                'strategy': 'DIVIDEND',
                'target_amount': 10000,  # HKD 10,000
                'lot_size': 1000  # 每手1000股
            }
        ]
        
        print(f"\n🎯 計劃交易 ({len(trade_candidates)}隻):")
        
        executed_trades = []
        
        for stock in trade_candidates:
            stock_code = stock['code']
            lot_size = stock['lot_size']
            
            print(f"\n📈 分析 {stock_code} - {stock['name']}...")
            
            # 獲取當前價格
            ret, quote_data = quote_ctx.get_market_snapshot([stock_code])
            if ret != RET_OK:
                print(f"   ❌ 獲取價格失敗")
                continue
            
            current_price = quote_data['last_price'].iloc[0]
            
            # 計算整手數量
            target_lots = int(stock['target_amount'] / (current_price * lot_size))
            
            if target_lots <= 0:
                print(f"   ⚠️  金額不足購買1手，跳過")
                continue
            
            quantity = target_lots * lot_size
            trade_amount = quantity * current_price
            
            print(f"   當前價格: HKD {current_price:.2f}")
            print(f"   每手股數: {lot_size:,}股")
            print(f"   計劃購買: {target_lots}手 ({quantity:,}股)")
            print(f"   交易金額: HKD {trade_amount:,.2f}")
            print(f"   交易策略: {stock['strategy']}")
            print(f"   交易理由: {stock['reason']}")
            
            # 執行買入
            print(f"   ⚡ 執行買入訂單...")
            
            ret, order_data = trd_ctx.place_order(
                price=current_price,
                qty=quantity,
                code=stock_code,
                trd_side=TrdSide.BUY,
                order_type=OrderType.NORMAL,
                trd_env=TrdEnv.SIMULATE,
                remark=f"主動交易 - {stock['strategy']}"
            )
            
            if ret == RET_OK:
                order_id = order_data['order_id'].iloc[0]
                print(f"   ✅ 訂單提交成功!")
                print(f"      訂單ID: {order_id}")
                
                trade_record = {
                    'order_id': order_id,
                    'stock_code': stock_code,
                    'stock_name': stock['name'],
                    'action': 'BUY',
                    'price': float(current_price),
                    'lots': target_lots,
                    'quantity': quantity,
                    'amount': trade_amount,
                    'strategy': stock['strategy'],
                    'reason': stock['reason'],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                executed_trades.append(trade_record)
                
                time.sleep(1)  # 等待訂單處理
                
            else:
                print(f"   ❌ 訂單提交失敗: {order_data}")
        
        # 檢查訂單狀態
        print(f"\n📋 檢查訂單狀態...")
        
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
                            print(f"      🎉 交易成功!")
                        else:
                            trade['status'] = status
                    else:
                        print(f"   ❓ 未找到訂單 {order_id}")
                        trade['status'] = 'UNKNOWN'
        
        # 最終持倉檢查
        print(f"\n📊 最終持倉檢查...")
        ret, final_pos = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK:
            print(f"   總持倉: {len(final_pos)}隻股票")
            if len(final_pos) > 0:
                for _, row in final_pos.iterrows():
                    print(f"      {row['code']} - {row['stock_name']}: {row['qty']:,}股")
        
        # 關閉連接
        trd_ctx.close()
        quote_ctx.close()
        
        # 生成報告
        print(f"\n{'='*70}")
        print(f"📋 交易執行報告")
        print(f"{'='*70}")
        
        if executed_trades:
            print(f"執行交易: {len(executed_trades)} 筆")
            total_amount = sum(t['amount'] for t in executed_trades)
            print(f"總金額: HKD {total_amount:,.2f}")
            
            print(f"\n詳細記錄:")
            for trade in executed_trades:
                print(f"   {trade['stock_code']} - {trade['stock_name']}")
                print(f"      價格: HKD {trade['price']:.2f}")
                print(f"      數量: {trade['lots']}手 ({trade['quantity']:,}股)")
                print(f"      金額: HKD {trade['amount']:,.2f}")
                print(f"      狀態: {trade.get('status', 'UNKNOWN')}")
        else:
            print("沒有執行交易")
        
        # 保存報告
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cash_available': float(cash),
            'trades_executed': executed_trades,
            'summary': {
                'total_trades': len(executed_trades),
                'successful_trades': len([t for t in executed_trades if t.get('status') == 'FILLED']),
                'total_amount': sum(t['amount'] for t in executed_trades)
            }
        }
        
        report_file = f"/Users/gordonlui/.openclaw/workspace/fixed_lot_trading_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 報告已保存: {report_file}")
        
        print(f"\n{'='*70}")
        print(f"✅ 整手交易執行完成")
        print(f"{'='*70}")
        
        return report
        
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

def main():
    """主函數"""
    print("🚀 執行整手交易系統")
    print("解決碎股問題，執行合規交易")
    
    try:
        report = execute_proper_trade()
        
        if 'error' not in report:
            print(f"\n📋 總結:")
            print(f"   時間: {report['timestamp']}")
            print(f"   可用現金: HKD {report['cash_available']:,.2f}")
            print(f"   執行交易: {report['summary']['total_trades']}筆")
            print(f"   成功交易: {report['summary']['successful_trades']}筆")
            print(f"   總金額: HKD {report['summary']['total_amount']:,}")
            
            print(f"\n💡 下一步:")
            print(f"   1. 在富途App中查看交易記錄")
            print(f"   2. 確認持倉已更新")
            print(f"   3. 監控新買入股票的表現")
        
    except Exception as e:
        print(f"❌ 系統錯誤: {e}")

if __name__ == "__main__":
    main()
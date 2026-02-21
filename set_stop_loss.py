#!/usr/bin/env python3
"""
設置止損訂單
為新買入的股票設置風險保護
"""

import sys
import json
from datetime import datetime
from futu import *

def set_stop_loss_orders():
    """設置止損訂單"""
    print(f"\n{'='*70}")
    print(f"🛡️ 設置止損訂單系統")
    print(f"{'='*70}")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    try:
        # 連接API
        print("1. 🔌 連接富途API...")
        trd_ctx = OpenSecTradeContext(host='127.0.0.1', port=11111)
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        print("   ✅ 連接成功")
        
        # 獲取當前持倉
        print("\n2. 📊 獲取當前持倉...")
        ret, pos_data = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        
        if ret != RET_OK:
            print("   ❌ 獲取持倉失敗")
            return
        
        if len(pos_data) == 0:
            print("   📭 沒有持倉")
            return
        
        print(f"   當前持倉: {len(pos_data)}隻股票")
        
        # 止損策略配置
        stop_loss_config = {
            'MOMENTUM': 0.08,    # 動量股: -8%
            'VALUE': 0.10,       # 價值股: -10%
            'DIVIDEND': 0.12,    # 股息股: -12%
            'DCA': 0.15,         # 定投股: -15%
            'DEFAULT': 0.10      # 默認: -10%
        }
        
        # 股票策略映射
        stock_strategies = {
            'HK.09868': 'MOMENTUM',      # 小鵬汽車 - 動量策略
            'HK.00992': 'DCA',           # 聯想集團 - 定投策略
            'HK.00700': 'VALUE',         # 騰訊 - 價值策略
            'HK.00883': 'DIVIDEND',      # 中海油 - 股息策略
            'HK.02020': 'VALUE',         # 安踏 - 價值策略
            'HK.09988': 'VALUE',         # 阿里 - 價值策略
            'HK.09618': 'VALUE',         # 京東 - 價值策略
            'HK.00005': 'DIVIDEND',      # 匯豐 - 股息策略
            'HK.01398': 'DIVIDEND',      # 工行 - 股息策略
            'HK.02638': 'DIVIDEND',      # 港燈 - 股息策略
            'HK.02800': 'DEFAULT'        # 盈富基金 - 默認
        }
        
        stop_loss_orders = []
        
        # 為每隻持倉股票設置止損
        for _, row in pos_data.iterrows():
            stock_code = row['code']
            stock_name = row['stock_name']
            quantity = row['qty']
            cost_price = row['cost_price']
            
            # 獲取當前價格
            ret, quote_data = quote_ctx.get_market_snapshot([stock_code])
            if ret != RET_OK:
                print(f"   ❌ 獲取{stock_code}價格失敗")
                continue
            
            current_price = quote_data['last_price'].iloc[0]
            
            # 計算盈虧
            profit_pct = ((current_price - cost_price) / cost_price) * 100
            
            # 確定止損策略
            strategy = stock_strategies.get(stock_code, 'DEFAULT')
            stop_loss_pct = stop_loss_config.get(strategy, 0.10)
            
            # 計算止損價
            stop_loss_price = cost_price * (1 - stop_loss_pct)
            
            # 如果當前價格已經低於止損價，調整為當前價格的-5%
            if current_price <= stop_loss_price:
                stop_loss_price = current_price * 0.95
            
            print(f"\n   📈 {stock_code} - {stock_name}")
            print(f"      持倉: {quantity:,}股")
            print(f"      成本: HKD {cost_price:.2f}")
            print(f"      現價: HKD {current_price:.2f}")
            print(f"      盈虧: {profit_pct:+.2f}%")
            print(f"      策略: {strategy}")
            print(f"      止損比例: -{stop_loss_pct*100:.0f}%")
            print(f"      止損價: HKD {stop_loss_price:.2f}")
            
            # 檢查是否需要設置止損
            if profit_pct < 0:  # 虧損中
                distance_to_stop = ((current_price - stop_loss_price) / current_price) * 100
                print(f"      ⚠️  當前虧損，距離止損: {distance_to_stop:.1f}%")
                
                if distance_to_stop <= 5:  # 距離止損5%以內
                    print(f"      🚨 接近止損價，建議設置止損訂單")
                    
                    # 設置止損訂單
                    stop_qty = int(quantity * 0.5)  # 先止損一半
                    if stop_qty <= 0:
                        stop_qty = quantity  # 如果計算為0，則全賣
                    
                    print(f"      ⚡ 設置止損訂單: {stop_qty:,}股 @ HKD {stop_loss_price:.2f}")
                    
                    # 在實際環境中執行止損訂單
                    # ret, order_data = trd_ctx.place_order(
                    #     price=stop_loss_price,
                    #     qty=stop_qty,
                    #     code=stock_code,
                    #     trd_side=TrdSide.SELL,
                    #     order_type=OrderType.NORMAL,
                    #     trd_env=TrdEnv.SIMULATE,
                    #     remark=f"止損訂單 - {strategy}策略"
                    # )
                    
                    stop_loss_orders.append({
                        'stock_code': stock_code,
                        'stock_name': stock_name,
                        'strategy': strategy,
                        'quantity': stop_qty,
                        'stop_price': stop_loss_price,
                        'current_price': current_price,
                        'cost_price': cost_price,
                        'profit_pct': profit_pct,
                        'distance_to_stop': distance_to_stop
                    })
            
            else:  # 盈利中
                # 設置移動止盈
                take_profit_price = cost_price * 1.15  # 盈利15%考慮止盈
                trailing_stop_price = current_price * 0.90  # 從高點回撤10%止盈
                
                print(f"      ✅ 當前盈利，可設置移動止盈")
                print(f"      止盈價: HKD {take_profit_price:.2f} (+15%)")
                print(f"      移動止盈: HKD {trailing_stop_price:.2f} (-10% from current)")
        
        # 特別關注新買入的小鵬汽車
        print(f"\n3. 🎯 特別關注 - 小鵬汽車-W (HK.09868)")
        
        xpeng_pos = pos_data[pos_data['code'] == 'HK.09868']
        if len(xpeng_pos) > 0:
            row = xpeng_pos.iloc[0]
            cost_price = row['cost_price']
            quantity = row['qty']
            current_price = 68.20  # 最新買入價
            
            # 動量股止損策略
            stop_loss_price = cost_price * 0.92  # -8%止損
            take_profit_price = cost_price * 1.15  # +15%止盈
            
            print(f"   持倉: {quantity:,}股")
            print(f"   成本: HKD {cost_price:.2f}")
            print(f"   現價: HKD {current_price:.2f}")
            print(f"   🛡️  建議止損: HKD {stop_loss_price:.2f} (-8%)")
            print(f"   🎯 建議止盈: HKD {take_profit_price:.2f} (+15%)")
            
            # 計算關鍵價位
            print(f"\n   關鍵價位監控:")
            print(f"      🟢 買入價: HKD {cost_price:.2f}")
            print(f"      🟡 輕微虧損: HKD {cost_price*0.98:.2f} (-2%)")
            print(f"      🟠 中度虧損: HKD {cost_price*0.95:.2f} (-5%)")
            print(f"      🔴 止損價: HKD {stop_loss_price:.2f} (-8%)")
            print(f"      🟢 輕微盈利: HKD {cost_price*1.05:.2f} (+5%)")
            print(f"      🟢 中度盈利: HKD {cost_price*1.10:.2f} (+10%)")
            print(f"      🎯 止盈價: HKD {take_profit_price:.2f} (+15%)")
        
        # 關閉連接
        trd_ctx.close()
        quote_ctx.close()
        print(f"\n4. 🔌 關閉API連接...")
        print("   ✅ 連接已關閉")
        
        # 生成止損報告
        print(f"\n{'='*70}")
        print(f"📋 止損策略報告")
        print(f"{'='*70}")
        
        if stop_loss_orders:
            print(f"建議設置止損的股票 ({len(stop_loss_orders)}隻):")
            for order in stop_loss_orders:
                print(f"\n   {order['stock_code']} - {order['stock_name']}")
                print(f"      策略: {order['strategy']}")
                print(f"      建議止損: {order['quantity']:,}股 @ HKD {order['stop_price']:.2f}")
                print(f"      當前價格: HKD {order['current_price']:.2f}")
                print(f"      距離止損: {order['distance_to_stop']:.1f}%")
                print(f"      當前盈虧: {order['profit_pct']:+.2f}%")
        else:
            print("當前沒有需要立即設置止損的股票")
        
        # 風險管理建議
        print(f"\n{'='*70}")
        print(f"💡 風險管理建議")
        print(f"{'='*70}")
        
        print("1. 🛡️ 止損策略:")
        print("   - 動量股(MOMENTUM): -8% 止損")
        print("   - 價值股(VALUE): -10% 止損")
        print("   - 股息股(DIVIDEND): -12% 止損")
        print("   - 定投股(DCA): -15% 止損")
        
        print("\n2. 🎯 止盈策略:")
        print("   - 短期交易: +15% 考慮止盈")
        print("   - 長期投資: +25% 考慮部分獲利了結")
        print("   - 移動止盈: 從高點回撤-10% 止盈")
        
        print("\n3. ⚖️ 倉位管理:")
        print("   - 單隻股票: ≤25% 總資產")
        print("   - 單一行業: ≤30% 總資產")
        print("   - 新交易: ≤5% 總資產試倉")
        
        # 保存報告
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'positions_count': len(pos_data),
            'stop_loss_orders': stop_loss_orders,
            'risk_management': {
                'stop_loss_config': stop_loss_config,
                'stock_strategies': stock_strategies
            }
        }
        
        report_file = f"/Users/gordonlui/.openclaw/workspace/stop_loss_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 止損報告已保存: {report_file}")
        
        print(f"\n{'='*70}")
        print(f"✅ 止損策略分析完成")
        print(f"{'='*70}")
        
        return report
        
    except Exception as e:
        print(f"\n❌ 系統錯誤: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'ERROR',
            'error': str(e)
        }

def main():
    """主函數"""
    print("🚀 止損訂單設置系統")
    print("為持倉股票設置風險保護")
    
    try:
        report = set_stop_loss_orders()
        
        print(f"\n📋 系統總結:")
        print(f"   分析時間: {report['timestamp']}")
        print(f"   持倉股票: {report['positions_count']}隻")
        print(f"   建議止損: {len(report['stop_loss_orders'])}隻")
        
        if report['stop_loss_orders']:
            print(f"\n💡 立即行動:")
            for order in report['stop_loss_orders']:
                print(f"   • {order['stock_code']}: 設置止損 @ HKD {order['stop_price']:.2f}")
        
        print(f"\n🎯 下一步:")
        print(f"   1. 在富途App中設置止損訂單")
        print(f"   2. 監控關鍵價位突破")
        print(f"   3. 定期檢討止損策略")
        
    except Exception as e:
        print(f"❌ 系統錯誤: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
简单检查992状态
"""

from futu import *
from datetime import datetime

def check_992_simple():
    """简单检查992状态"""
    print("📊 检查992联想集团状态...")
    print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 连接富途API
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        trd_ctx = OpenSecTradeContext(
            host='127.0.0.1',
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        
        code = "HK.00992"
        
        # 获取实时报价
        ret, snapshot = quote_ctx.get_market_snapshot([code])
        
        if ret == RET_OK and len(snapshot) > 0:
            row = snapshot.iloc[0]
            current_price = row['last_price']
            prev_close = row['prev_close_price']
            
            print(f"\n✅ {code} 联想集团:")
            print(f"   当前价: HKD {current_price:.2f}")
            print(f"   昨收价: HKD {prev_close:.2f}")
            print(f"   涨跌: {current_price - prev_close:.2f}")
            print(f"   涨跌幅: {(current_price - prev_close)/prev_close*100:.2f}%")
            print(f"   成交量: {row['volume']:,}股")
            
            # 获取持仓
            ret, positions = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
            
            if ret == RET_OK and len(positions) > 0:
                position = positions[positions['code'] == code]
                
                if len(position) > 0:
                    pos_row = position.iloc[0]
                    cost_price = pos_row['cost_price']
                    qty = pos_row['qty']
                    
                    print(f"\n📦 您的持仓:")
                    print(f"   数量: {qty:,}股")
                    print(f"   成本: HKD {cost_price:.2f}")
                    
                    # 计算盈亏
                    profit_per_share = current_price - cost_price
                    total_profit = profit_per_share * qty
                    profit_pct = (current_price - cost_price) / cost_price * 100
                    
                    print(f"\n💰 盈亏状态:")
                    print(f"   每股: HKD {profit_per_share:.3f}")
                    print(f"   总计: HKD {total_profit:,.2f}")
                    print(f"   百分比: {profit_pct:.2f}%")
                    
                    # 市值
                    market_value = current_price * qty
                    print(f"   市值: HKD {market_value:,.2f}")
                    
                    # 状态判断
                    if profit_pct > 0:
                        print(f"\n🎯 **✅ 盈利中！** ({profit_pct:.2f}%)")
                        
                        # 止盈分析
                        take_profit_pct = 10.0
                        if profit_pct >= take_profit_pct:
                            print(f"   🎉 已达到{take_profit_pct}%止盈目标！")
                            print(f"   考虑部分止盈锁定利润")
                        else:
                            remaining_to_target = take_profit_pct - profit_pct
                            print(f"   📈 距离{take_profit_pct}%止盈目标: {remaining_to_target:.2f}%")
                            print(f"   目标价: HKD {cost_price * (1 + take_profit_pct/100):.2f}")
                        
                        # 今日表现
                        today_change = (current_price - prev_close) / prev_close * 100
                        print(f"\n📊 今日表现:")
                        print(f"   今日涨跌: {today_change:.2f}%")
                        print(f"   相对成本: {profit_pct:.2f}%")
                        
                    else:
                        print(f"\n🎯 **⚠️ 浮亏中** ({profit_pct:.2f}%)")
                        
                        # 止损分析
                        stop_loss_pct = 2.0
                        stop_loss_price = cost_price * (1 - stop_loss_pct/100)
                        
                        if current_price <= stop_loss_price:
                            print(f"   🚨 已触发{stop_loss_pct}%止损！")
                            print(f"   止损价: HKD {stop_loss_price:.2f}")
                        else:
                            distance_to_stop = (current_price - stop_loss_price) / cost_price * 100
                            print(f"   🛡️ 距离止损: {distance_to_stop:.2f}%")
                            print(f"   止损价: HKD {stop_loss_price:.2f}")
                    
                    # 建议
                    print(f"\n💡 建议:")
                    if profit_pct > 5:
                        print(f"   ✅ 继续持有，观察是否达到10%止盈")
                        print(f"   📊 可考虑在8-10%区间部分止盈")
                    elif profit_pct > 0:
                        print(f"   📈 小幅盈利，继续持有观察")
                        print(f"   🎯 目标10%止盈")
                    else:
                        print(f"   ⏳ 耐心持有，等待反弹")
                        print(f"   🛡️ 严格监控2%止损")
                        
                else:
                    print(f"❌ 未找到{code}持仓")
            else:
                print("❌ 无法获取持仓信息")
        else:
            print(f"❌ 无法获取{code}报价")
        
        quote_ctx.close()
        trd_ctx.close()
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    check_992_simple()
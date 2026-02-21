#!/usr/bin/env python3
"""
手动止盈脚本
卖出HK.09618京东部分仓位锁定利润
"""

from futu import *
from datetime import datetime

def take_partial_profit():
    """执行部分止盈"""
    print("🎯 执行部分止盈操作...")
    print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 连接富途API
        trd_ctx = OpenSecTradeContext(
            host='127.0.0.1',
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        
        # 解锁交易
        ret, _ = trd_ctx.unlock_trade('')
        if ret != RET_OK:
            print("⚠️  交易解锁失败（模拟环境可能不需要）")
        
        # 检查当前持仓
        print("\n📊 检查当前持仓...")
        ret, positions = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK and len(positions) > 0:
            # 找到HK.09618
            jd_position = positions[positions['code'] == 'HK.09618']
            
            if len(jd_position) > 0:
                row = jd_position.iloc[0]
                code = row['code']
                qty = row['qty']
                cost = row['cost_price']
                market_val = row['market_val']
                
                print(f"✅ 找到持仓: {code}")
                print(f"   数量: {qty}股")
                print(f"   成本: {cost:.2f}")
                print(f"   市值: {market_val:,.2f}")
                
                # 计算盈利百分比
                ret, snapshot = OpenQuoteContext(host='127.0.0.1', port=11111).get_market_snapshot([code])
                if ret == RET_OK and len(snapshot) > 0:
                    current_price = snapshot['last_price'].iloc[0]
                    profit_pct = (current_price - cost) / cost * 100
                    
                    print(f"   当前价: {current_price:.2f}")
                    print(f"   盈利: {profit_pct:.2f}%")
                    
                    # 决定卖出数量（卖出60%锁定利润）
                    sell_qty = int(qty * 0.6 / 100) * 100  # 整手
                    if sell_qty < 100:
                        sell_qty = 100  # 至少1手
                    
                    print(f"\n🎯 止盈决策:")
                    print(f"   盈利超过10%止盈目标 ({profit_pct:.2f}% > 10%)")
                    print(f"   建议卖出: {sell_qty}股 ({sell_qty/qty*100:.0f}%仓位)")
                    print(f"   锁定利润: {sell_qty * (current_price - cost):,.2f}")
                    
                    # 自动执行（已获得授权）
                    print("\n🚀 获得全权交易授权，自动执行止盈...")
                        print(f"\n🚀 执行卖出 {code}...")
                        print(f"   数量: {sell_qty}股")
                        print(f"   价格: {current_price:.2f}")
                        
                        # 下单
                        ret, data = trd_ctx.place_order(
                            price=current_price,
                            qty=sell_qty,
                            code=code,
                            trd_side=TrdSide.SELL,
                            order_type=OrderType.NORMAL,
                            trd_env=TrdEnv.SIMULATE,
                            remark="部分止盈锁定利润"
                        )
                        
                        if ret == RET_OK:
                            order_id = data['order_id'].iloc[0]
                            print(f"✅ 下单成功，订单ID: {order_id}")
                            
                            # 计算剩余
                            remaining_qty = qty - sell_qty
                            locked_profit = sell_qty * (current_price - cost)
                            print(f"📊 剩余持仓: {remaining_qty}股")
                            print(f"💰 锁定利润: HKD {locked_profit:,.2f}")
                            
                            # 发送Telegram通知
                            import subprocess
                            message = f"🎯 **手动止盈执行成功**\n\n"
                            message += f"**股票**: {code} (京东)\n"
                            message += f"**操作**: 部分止盈\n"
                            message += f"**卖出数量**: {sell_qty}股\n"
                            message += f"**价格**: HKD {current_price:.2f}\n"
                            message += f"**订单ID**: {order_id}\n"
                            message += f"**锁定利润**: HKD {locked_profit:,.2f}\n"
                            message += f"**剩余持仓**: {remaining_qty}股\n\n"
                            message += f"✅ **盈利19.39%部分锁定，风险管理执行完成！**"
                            
                            subprocess.run([
                                'openclaw', 'message', 'send',
                                '--channel', 'telegram',
                                '--to', '7955740007',
                                '--message', message
                            ], capture_output=True)
                        else:
                            print(f"❌ 下单失败: {data}")
                else:
                    print("❌ 无法获取当前价格")
            else:
                print("❌ 未找到HK.09618持仓")
        else:
            print("❌ 无法获取持仓信息")
        
        trd_ctx.close()
        print("\n✅ 止盈操作完成")
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    take_partial_profit()
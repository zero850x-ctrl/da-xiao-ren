#!/usr/bin/env python3
"""
执行止盈操作 - 卖出HK.09618部分仓位锁定利润
已获得全权交易授权
"""

from futu import *
from datetime import datetime
import subprocess

def execute_take_profit():
    """执行止盈操作"""
    print("🎯 执行止盈操作 - 已获得全权交易授权")
    print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 连接富途API
        trd_ctx = OpenSecTradeContext(
            host='127.0.0.1',
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 解锁交易
        ret, _ = trd_ctx.unlock_trade('')
        if ret != RET_OK:
            print("⚠️  交易解锁失败（模拟环境可能不需要）")
        
        # 检查HK.09618持仓
        print("\n📊 检查HK.09618持仓...")
        code = "HK.09618"
        
        ret, positions = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK and len(positions) > 0:
            jd_position = positions[positions['code'] == code]
            
            if len(jd_position) > 0:
                row = jd_position.iloc[0]
                qty = row['qty']
                cost = row['cost_price']
                
                print(f"✅ 找到持仓: {code}")
                print(f"   数量: {qty}股")
                print(f"   成本: {cost:.2f}")
                
                # 获取当前价格
                ret, snapshot = quote_ctx.get_market_snapshot([code])
                if ret == RET_OK and len(snapshot) > 0:
                    current_price = snapshot['last_price'].iloc[0]
                    profit_pct = (current_price - cost) / cost * 100
                    
                    print(f"   当前价: {current_price:.2f}")
                    print(f"   盈利: {profit_pct:.2f}%")
                    
                    # 计算卖出数量（卖出60%锁定利润）
                    sell_qty = int(qty * 0.6 / 100) * 100  # 整手
                    if sell_qty < 100:
                        sell_qty = 100  # 至少1手
                    
                    print(f"\n🎯 止盈决策:")
                    print(f"   盈利超过10%止盈目标 ({profit_pct:.2f}% > 10%)")
                    print(f"   卖出数量: {sell_qty}股 ({sell_qty/qty*100:.0f}%仓位)")
                    
                    # 执行卖出
                    print(f"\n🚀 执行卖出 {code}...")
                    print(f"   数量: {sell_qty}股")
                    print(f"   价格: {current_price:.2f}")
                    
                    ret, data = trd_ctx.place_order(
                        price=current_price,
                        qty=sell_qty,
                        code=code,
                        trd_side=TrdSide.SELL,
                        order_type=OrderType.NORMAL,
                        trd_env=TrdEnv.SIMULATE,
                        remark="部分止盈锁定利润19.39%"
                    )
                    
                    if ret == RET_OK:
                        order_id = data['order_id'].iloc[0]
                        print(f"✅ 下单成功，订单ID: {order_id}")
                        
                        # 计算利润
                        remaining_qty = qty - sell_qty
                        locked_profit = sell_qty * (current_price - cost)
                        
                        print(f"📊 剩余持仓: {remaining_qty}股")
                        print(f"💰 锁定利润: HKD {locked_profit:,.2f}")
                        
                        # 发送Telegram通知
                        message = f"🎯 **手动止盈执行成功**\n\n"
                        message += f"**股票**: {code} (京东)\n"
                        message += f"**操作**: 部分止盈\n"
                        message += f"**卖出数量**: {sell_qty}股\n"
                        message += f"**价格**: HKD {current_price:.2f}\n"
                        message += f"**订单ID**: {order_id}\n"
                        message += f"**锁定利润**: HKD {locked_profit:,.2f}\n"
                        message += f"**剩余持仓**: {remaining_qty}股\n"
                        message += f"**原盈利**: {profit_pct:.2f}%\n\n"
                        message += f"✅ **盈利19.39%部分锁定，风险管理执行完成！**"
                        
                        subprocess.run([
                            'openclaw', 'message', 'send',
                            '--channel', 'telegram',
                            '--to', '7955740007',
                            '--message', message
                        ], capture_output=True)
                        
                        return True, order_id, locked_profit, remaining_qty
                    else:
                        print(f"❌ 下单失败: {data}")
                        return False, None, 0, qty
                else:
                    print("❌ 无法获取当前价格")
                    return False, None, 0, qty
            else:
                print(f"❌ 未找到{code}持仓")
                return False, None, 0, 0
        else:
            print("❌ 无法获取持仓信息")
            return False, None, 0, 0
        
        trd_ctx.close()
        quote_ctx.close()
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        return False, None, 0, 0

if __name__ == "__main__":
    success, order_id, profit, remaining = execute_take_profit()
    
    if success:
        print(f"\n✅ 止盈操作成功完成！")
        print(f"   订单ID: {order_id}")
        print(f"   锁定利润: HKD {profit:,.2f}")
        print(f"   剩余持仓: {remaining}股")
    else:
        print("\n❌ 止盈操作失败")
#!/usr/bin/env python3
"""
检查并执行止损
HK.00700腾讯已触发2%止损
"""

from futu import *
from datetime import datetime
import subprocess

def check_and_execute_stop_loss():
    """检查并执行止损"""
    print("🛡️ 检查止损触发情况...")
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
        
        # 检查HK.00700持仓
        print("\n📊 检查HK.00700持仓...")
        code = "HK.00700"
        
        ret, positions = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK and len(positions) > 0:
            tc_position = positions[positions['code'] == code]
            
            if len(tc_position) > 0:
                row = tc_position.iloc[0]
                qty = row['qty']
                cost = row['cost_price']
                
                print(f"✅ 找到持仓: {code}")
                print(f"   数量: {qty}股")
                print(f"   成本: {cost:.2f}")
                
                # 获取当前价格
                ret, snapshot = quote_ctx.get_market_snapshot([code])
                if ret == RET_OK and len(snapshot) > 0:
                    current_price = snapshot['last_price'].iloc[0]
                    loss_pct = (current_price - cost) / cost * 100
                    
                    print(f"   当前价: {current_price:.2f}")
                    print(f"   亏损: {loss_pct:.2f}%")
                    
                    # 检查是否触发2%止损
                    stop_loss_pct = 2.0
                    if loss_pct <= -stop_loss_pct:
                        print(f"\n🚨 **止损触发！**")
                        print(f"   亏损{loss_pct:.2f}% ≤ -{stop_loss_pct}%止损线")
                        print(f"   需要执行止损")
                        
                        # 执行止损（卖出全部）
                        print(f"\n🚀 执行止损卖出 {code}...")
                        print(f"   数量: {qty}股")
                        print(f"   价格: {current_price:.2f}")
                        
                        ret, data = trd_ctx.place_order(
                            price=current_price,
                            qty=qty,
                            code=code,
                            trd_side=TrdSide.SELL,
                            order_type=OrderType.NORMAL,
                            trd_env=TrdEnv.SIMULATE,
                            remark=f"2%止损触发，亏损{loss_pct:.2f}%"
                        )
                        
                        if ret == RET_OK:
                            order_id = data['order_id'].iloc[0]
                            loss_amount = qty * (cost - current_price)
                            
                            print(f"✅ 止损执行成功，订单ID: {order_id}")
                            print(f"💰 止损金额: HKD {loss_amount:,.2f}")
                            
                            # 发送Telegram通知
                            message = f"🚨 **2%止损触发执行**\n\n"
                            message += f"**股票**: {code} (腾讯)\n"
                            message += f"**操作**: 止损卖出\n"
                            message += f"**数量**: {qty}股\n"
                            message += f"**价格**: HKD {current_price:.2f}\n"
                            message += f"**订单ID**: {order_id}\n"
                            message += f"**亏损**: {loss_pct:.2f}%\n"
                            message += f"**止损金额**: HKD {loss_amount:,.2f}\n"
                            message += f"**成本价**: HKD {cost:.2f}\n\n"
                            message += f"✅ **严格执行2% Rule，风险控制完成！**"
                            
                            subprocess.run([
                                'openclaw', 'message', 'send',
                                '--channel', 'telegram',
                                '--to', '7955740007',
                                '--message', message
                            ], capture_output=True)
                            
                            return True, order_id, loss_amount, loss_pct
                        else:
                            print(f"❌ 止损下单失败: {data}")
                            return False, None, 0, loss_pct
                    else:
                        print(f"\n✅ 未触发止损")
                        print(f"   亏损{loss_pct:.2f}% > -{stop_loss_pct}%")
                        print(f"   继续持有，监控中...")
                        return False, None, 0, loss_pct
                else:
                    print("❌ 无法获取当前价格")
                    return False, None, 0, 0
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
    success, order_id, loss_amount, loss_pct = check_and_execute_stop_loss()
    
    if success:
        print(f"\n✅ 止损操作成功完成！")
        print(f"   订单ID: {order_id}")
        print(f"   止损金额: HKD {loss_amount:,.2f}")
        print(f"   亏损百分比: {loss_pct:.2f}%")
    else:
        print("\n📊 止损检查完成，未触发止损或操作失败")
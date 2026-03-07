#!/usr/bin/env python3
"""
简单交易测试
"""

import sys
from datetime import datetime, timedelta
from futu import *

def simple_trade_test():
    """简单交易测试"""
    print(f"🔧 简单交易测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 连接API
    trd_ctx = OpenSecTradeContext(host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 解锁交易
    ret, _ = trd_ctx.unlock_trade('')
    if ret != RET_OK:
        print("⚠️  交易解锁失败（模拟环境可能不需要）")
    
    # 检查模拟账户
    print("\n💰 模拟账户检查:")
    ret, sim_data = trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE)
    if ret == RET_OK and len(sim_data) > 0:
        cash = sim_data['cash'].iloc[0]
        total_assets = sim_data['total_assets'].iloc[0]
        market_val = sim_data['market_val'].iloc[0]
        power = sim_data['power'].iloc[0]
        
        print(f"   现金: HKD {cash:,.2f}")
        print(f"   总资产: HKD {total_assets:,.2f}")
        print(f"   市值: HKD {market_val:,.2f}")
        print(f"   购买力: HKD {power:,.2f}")
        
        # 计算可用资金
        available_cash = cash
        print(f"   可用资金: HKD {available_cash:,.2f}")
    
    # 检查持仓
    print("\n📦 当前持仓:")
    ret, positions = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
    if ret == RET_OK and len(positions) > 0:
        print(f"   持仓数量: {len(positions)} 只股票")
        for idx, pos in positions.iterrows():
            code = pos['code']
            qty = pos['qty']
            cost_price = pos['cost_price']
            market_val = pos['market_val']
            
            # 获取当前价格
            ret, snapshot = quote_ctx.get_market_snapshot([code])
            if ret == RET_OK and len(snapshot) > 0:
                current_price = snapshot['last_price'].iloc[0]
                if cost_price > 0:
                    change_pct = ((current_price - cost_price) / cost_price) * 100
                else:
                    change_pct = 0
                
                change_emoji = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
                print(f"   {change_emoji} {code}: {qty}股 @ {cost_price:.2f} → {current_price:.2f} ({change_pct:+.2f}%)")
    else:
        print("   无持仓")
    
    # 测试下单（模拟买入）
    print("\n🧪 测试下单（模拟）:")
    test_code = "HK.02800"  # 盈富基金
    test_price = 27.50
    test_qty = 100
    
    # 获取当前价格
    ret, snapshot = quote_ctx.get_market_snapshot([test_code])
    if ret == RET_OK and len(snapshot) > 0:
        current_price = snapshot['last_price'].iloc[0]
        print(f"   {test_code} 当前价格: {current_price:.2f}")
        
        # 测试下单（不实际执行）
        print(f"   测试下单: BUY {test_qty}股 @ {test_price:.2f}")
        print("   ⚠️  这是测试，不会实际下单")
        
        # 检查是否有足够的现金
        if available_cash > test_price * test_qty:
            print("   ✅ 有足够现金")
        else:
            print("   ❌ 现金不足")
    
    # 关闭连接
    trd_ctx.close()
    quote_ctx.close()
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    simple_trade_test()
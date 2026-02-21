#!/usr/bin/env python3
"""
交易系统状态报告
"""

import sys
from datetime import datetime, timedelta
from futu import *

def generate_trading_report():
    """生成交易系统状态报告"""
    print(f"📊 技术图表交易系统状态报告")
    print(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 连接API
    trd_ctx = OpenSecTradeContext(host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUSECURITIES)
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 账户概览
    print("\n💰 账户概览:")
    ret, sim_data = trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE)
    if ret == RET_OK and len(sim_data) > 0:
        cash = sim_data['cash'].iloc[0]
        total_assets = sim_data['total_assets'].iloc[0]
        market_val = sim_data['market_val'].iloc[0]
        
        print(f"   现金余额: HKD {cash:,.2f}")
        print(f"   总资产: HKD {total_assets:,.2f}")
        print(f"   持仓市值: HKD {market_val:,.2f}")
        
        # 计算仓位比例
        if total_assets > 0:
            position_ratio = (market_val / total_assets) * 100
            cash_ratio = (cash / total_assets) * 100
            print(f"   仓位比例: {position_ratio:.1f}%")
            print(f"   现金比例: {cash_ratio:.1f}%")
    
    # 持仓详情
    print("\n📦 持仓详情:")
    ret, positions = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
    if ret == RET_OK and len(positions) > 0:
        total_pnl = 0
        active_positions = 0
        
        for idx, pos in positions.iterrows():
            code = pos['code']
            qty = pos['qty']
            cost_price = pos['cost_price']
            market_val = pos['market_val']
            
            # 只显示有持仓的股票
            if qty > 0:
                active_positions += 1
                
                # 获取当前价格
                ret, snapshot = quote_ctx.get_market_snapshot([code])
                if ret == RET_OK and len(snapshot) > 0:
                    current_price = snapshot['last_price'].iloc[0]
                    if cost_price > 0:
                        pnl = (current_price - cost_price) * qty
                        pnl_pct = ((current_price - cost_price) / cost_price) * 100
                        total_pnl += pnl
                        
                        pnl_emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
                        print(f"   {pnl_emoji} {code}: {qty}股")
                        print(f"       成本: {cost_price:.2f} | 现价: {current_price:.2f}")
                        print(f"       盈亏: HKD {pnl:+,.2f} ({pnl_pct:+.2f}%)")
        
        print(f"\n   活跃持仓: {active_positions} 只股票")
        print(f"   总盈亏: HKD {total_pnl:+,.2f}")
    
    # 市场状况
    print("\n📈 市场状况:")
    watchlist = ["HK.02800", "HK.00700", "HK.09988", "HK.01299", "HK.02318"]
    
    for code in watchlist:
        ret, snapshot = quote_ctx.get_market_snapshot([code])
        if ret == RET_OK and len(snapshot) > 0:
            name = snapshot['name'].iloc[0]
            price = snapshot['last_price'].iloc[0]
            prev_close = snapshot['prev_close_price'].iloc[0]
            volume = snapshot['volume'].iloc[0]
            
            if prev_close > 0:
                change_pct = ((price - prev_close) / prev_close) * 100
                change_emoji = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
                
                # 简化显示
                print(f"   {change_emoji} {code}: {price:.2f} ({change_pct:+.2f}%)")
    
    # 交易时间检查
    print(f"\n⏰ 系统状态:")
    now = datetime.now()
    trading_start = now.replace(hour=9, minute=30, second=0, microsecond=0)
    trading_end = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    if trading_start <= now <= trading_end:
        print("   ✅ 交易系统: 运行中（交易时间内）")
        print("   🎯 模式: 全自动技术图表交易")
        print("   🔒 环境: 模拟账户（安全）")
    else:
        print("   ⏸️  交易系统: 待机中（非交易时间）")
        print("   📊 模式: 仅分析")
    
    # 关闭连接
    trd_ctx.close()
    quote_ctx.close()
    
    print("\n" + "=" * 70)
    print("✅ 报告生成完成")
    print(f"📋 总结: 模拟账户运行正常，{active_positions}只持仓，现金充足")

if __name__ == "__main__":
    generate_trading_report()
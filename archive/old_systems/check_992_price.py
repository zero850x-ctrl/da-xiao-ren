#!/usr/bin/env python3
"""
检查992联想集团的详细价格信息
"""

from futu import *
from datetime import datetime

def check_992_price():
    """检查992当前价格和盈亏"""
    print("📊 检查992联想集团详细状态...")
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
        print(f"\n🔍 获取{code}实时报价...")
        ret, snapshot = quote_ctx.get_market_snapshot([code])
        
        if ret == RET_OK and len(snapshot) > 0:
            row = snapshot.iloc[0]
            
            print(f"✅ {code} 联想集团实时报价:")
            print(f"   最新价: {row['last_price']:.2f}")
            print(f"   开盘价: {row['open_price']:.2f}")
            print(f"   最高价: {row['high_price']:.2f}")
            print(f"   最低价: {row['low_price']:.2f}")
            print(f"   昨收价: {row['prev_close_price']:.2f}")
            print(f"   成交量: {row['volume']:,}")
            print(f"   成交额: HKD {row['turnover']:,.0f}")
            print(f"   涨跌幅: {row['change_rate']*100:.2f}%")
            print(f"   涨跌额: {row['change_value']:.2f}")
            
            # 获取持仓成本
            ret, positions = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
            
            if ret == RET_OK and len(positions) > 0:
                position = positions[positions['code'] == code]
                
                if len(position) > 0:
                    pos_row = position.iloc[0]
                    cost_price = pos_row['cost_price']
                    qty = pos_row['qty']
                    current_price = row['last_price']
                    
                    print(f"\n📦 持仓信息:")
                    print(f"   持仓数量: {qty:,}股")
                    print(f"   成本价格: HKD {cost_price:.2f}")
                    print(f"   当前价格: HKD {current_price:.2f}")
                    
                    # 计算盈亏
                    profit_per_share = current_price - cost_price
                    total_profit = profit_per_share * qty
                    profit_pct = (current_price - cost_price) / cost_price * 100
                    
                    print(f"\n💰 盈亏计算:")
                    print(f"   每股盈亏: HKD {profit_per_share:.3f}")
                    print(f"   总盈亏: HKD {total_profit:,.2f}")
                    print(f"   盈亏百分比: {profit_pct:.2f}%")
                    
                    # 计算市值
                    market_value = current_price * qty
                    print(f"   持仓市值: HKD {market_value:,.2f}")
                    
                    # 技术指标分析
                    print(f"\n📈 技术分析:")
                    
                    # 获取K线数据
                    ret, kline = quote_ctx.get_cur_kline(code, 100, KLType.K_1M, AuType.QFQ)
                    if ret == RET_OK and len(kline) > 0:
                        latest_close = kline['close'].iloc[-1]
                        prev_close = kline['close'].iloc[-2] if len(kline) > 1 else latest_close
                        
                        print(f"   最新收盘: HKD {latest_close:.2f}")
                        print(f"   前收盘: HKD {prev_close:.2f}")
                        
                        # 简单趋势判断
                        if latest_close > prev_close:
                            print(f"   短期趋势: ↗️ 上涨")
                        else:
                            print(f"   短期趋势: ↘️ 下跌")
                    
                    # 风险评估
                    print(f"\n🛡️ 风险管理:")
                    stop_loss_price = cost_price * 0.98  # 2%止损
                    take_profit_price = cost_price * 1.10  # 10%止盈
                    
                    print(f"   止损价: HKD {stop_loss_price:.2f} (2%止损)")
                    print(f"   止盈价: HKD {take_profit_price:.2f} (10%止盈)")
                    print(f"   当前价距离止损: {(current_price - stop_loss_price):.3f}")
                    print(f"   当前价距离止盈: {(take_profit_price - current_price):.3f}")
                    
                    # 状态判断
                    if profit_pct > 0:
                        print(f"\n🎯 当前状态: ✅ **盈利中** ({profit_pct:.2f}%)")
                        if profit_pct >= 10:
                            print(f"   ⚠️  已达到止盈目标，考虑部分止盈")
                        else:
                            print(f"   📊 继续持有，目标止盈10%")
                    else:
                        print(f"\n🎯 当前状态: ⚠️  **浮亏中** ({profit_pct:.2f}%)")
                        if current_price <= stop_loss_price:
                            print(f"   🚨 已触发止损价，需要止损")
                        else:
                            print(f"   📊 继续持有，止损价: {stop_loss_price:.2f}")
                    
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
    check_992_price()
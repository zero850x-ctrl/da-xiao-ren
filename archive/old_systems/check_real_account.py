#!/usr/bin/env python3
"""
检查真实交易账户状态
"""

import sys
from futu import *

def check_real_account():
    """检查真实账户状态"""
    print("🔍 检查真实交易账户状态...")
    
    try:
        # 连接富途API
        trd_ctx = OpenSecTradeContext(
            host='127.0.0.1',
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        
        # 检查真实交易环境
        print("\n📊 检查真实交易环境...")
        ret, acc_list = trd_ctx.get_acc_list()
        
        if ret == RET_OK:
            print(f"✅ 真实账户数量: {len(acc_list)}")
            for idx, row in acc_list.iterrows():
                print(f"   账户ID: {row['acc_id']}")
                print(f"   账户类型: {row['acc_type']}")
                print(f"   市场: {row['market']}")
                print(f"   状态: {row['status']}")
        else:
            print(f"❌ 获取真实账户失败: {acc_list}")
        
        # 检查真实账户资金
        print("\n💰 检查真实账户资金...")
        ret, assets = trd_ctx.accinfo_query()
        
        if ret == RET_OK and len(assets) > 0:
            print("✅ 真实账户资金信息:")
            for idx, row in assets.iterrows():
                print(f"   现金: HKD {row['cash']:,.2f}")
                print(f"   总资产: HKD {row['total_assets']:,.2f}")
                print(f"   持仓市值: HKD {row['market_val']:,.2f}")
                print(f"   可用资金: HKD {row['available_funds']:,.2f}")
        else:
            print(f"❌ 获取资金信息失败: {assets}")
        
        # 检查真实持仓
        print("\n📦 检查真实持仓...")
        ret, positions = trd_ctx.position_list_query()
        
        if ret == RET_OK:
            if len(positions) > 0:
                print(f"✅ 真实持仓数量: {len(positions)}")
                for idx, row in positions.iterrows():
                    print(f"   {row['code']}: {row['qty']}股")
                    print(f"     成本: {row['cost_price']:.2f}")
                    print(f"     市值: {row['market_val']:,.2f}")
                    print(f"     盈亏: {row.get('pl_ratio', 0):.2f}%")
            else:
                print("📭 真实账户无持仓")
        else:
            print(f"❌ 获取持仓失败: {positions}")
        
        # 检查模拟账户对比
        print("\n🔄 对比模拟账户...")
        ret, sim_assets = trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK and len(sim_assets) > 0:
            print("✅ 模拟账户资金信息:")
            for idx, row in sim_assets.iterrows():
                print(f"   现金: HKD {row['cash']:,.2f}")
                print(f"   总资产: HKD {row['total_assets']:,.2f}")
        
        trd_ctx.close()
        print("\n✅ 账户检查完成")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    check_real_account()
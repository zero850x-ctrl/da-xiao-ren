#!/usr/bin/env python3
"""
明确检查账户环境
区分真实账户和模拟账户
"""

from futu import *

def check_environments():
    """检查交易环境"""
    print("🔍 检查富途交易环境...")
    
    try:
        trd_ctx = OpenSecTradeContext(
            host='127.0.0.1',
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        
        # 检查真实环境
        print("\n📊 真实交易环境:")
        ret, real_acc = trd_ctx.accinfo_query()
        if ret == RET_OK and len(real_acc) > 0:
            print("✅ 真实账户存在")
            for idx, row in real_acc.iterrows():
                print(f"   现金: HKD {row['cash']:,.2f}")
                print(f"   总资产: HKD {row['total_assets']:,.2f}")
                print(f"   持仓市值: HKD {row['market_val']:,.2f}")
        else:
            print("❌ 无法获取真实账户信息")
        
        # 检查模拟环境
        print("\n🔄 模拟交易环境:")
        ret, sim_acc = trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK and len(sim_acc) > 0:
            print("✅ 模拟账户存在")
            for idx, row in sim_acc.iterrows():
                print(f"   现金: HKD {row['cash']:,.2f}")
                print(f"   总资产: HKD {row['total_assets']:,.2f}")
                print(f"   持仓市值: HKD {row['market_val']:,.2f}")
        else:
            print("❌ 无法获取模拟账户信息")
        
        # 检查真实持仓
        print("\n📦 真实账户持仓:")
        ret, real_pos = trd_ctx.position_list_query()
        if ret == RET_OK:
            if len(real_pos) > 0:
                print(f"✅ 真实持仓: {len(real_pos)}个")
                for idx, row in real_pos.iterrows():
                    print(f"   {row['code']}: {row['qty']}股")
            else:
                print("📭 真实账户无持仓")
        else:
            print("❌ 无法获取真实持仓")
        
        # 检查模拟持仓
        print("\n📦 模拟账户持仓:")
        ret, sim_pos = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK:
            if len(sim_pos) > 0:
                print(f"✅ 模拟持仓: {len(sim_pos)}个")
                for idx, row in sim_pos.iterrows():
                    print(f"   {row['code']}: {row['qty']}股")
            else:
                print("📭 模拟账户无持仓")
        else:
            print("❌ 无法获取模拟持仓")
        
        trd_ctx.close()
        print("\n✅ 环境检查完成")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    check_environments()
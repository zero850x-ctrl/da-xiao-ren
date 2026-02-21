#!/usr/bin/env python3
"""
富途自动交易脚本
基于简单策略执行自动买卖
"""

import sys
import time
import json
from datetime import datetime, time as dt_time
from futu import *

class AutoTrader:
    """自动交易器"""
    
    def __init__(self):
        self.trd_ctx = None
        self.quote_ctx = None
        self.trading_hours = {
            'start': dt_time(9, 30),   # 港股开盘
            'end': dt_time(16, 0)      # 港股收盘
        }
        
    def connect(self):
        """连接富途API"""
        print(f"🔗 [{datetime.now().strftime('%H:%M:%S')}] 连接富途API...")
        try:
            self.trd_ctx = OpenSecTradeContext(
                host='127.0.0.1',
                port=11111,
                security_firm=SecurityFirm.FUTUSECURITIES
            )
            
            self.quote_ctx = OpenQuoteContext(
                host='127.0.0.1',
                port=11111
            )
            
            # 解锁交易
            ret, _ = self.trd_ctx.unlock_trade('')
            if ret != RET_OK:
                print("⚠️  交易解锁失败（模拟环境可能不需要）")
            
            print("✅ 连接成功")
            return True
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def is_trading_hours(self):
        """检查是否在交易时间内"""
        now = datetime.now().time()
        return self.trading_hours['start'] <= now <= self.trading_hours['end']
    
    def get_account_balance(self):
        """获取账户余额"""
        # 使用正确的方法名
        ret, data = self.trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK and len(data) > 0:
            cash = data['cash'].iloc[0]
            total_assets = data['total_assets'].iloc[0]
            return cash, total_assets
        return 0, 0
    
    def get_current_positions(self):
        """获取当前持仓"""
        ret, positions = self.trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK:
            return positions
        return None
    
    def get_stock_price(self, code):
        """获取股票当前价格"""
        ret, data = self.quote_ctx.get_market_snapshot([code])
        if ret == RET_OK and len(data) > 0:
            return data['last_price'].iloc[0]
        return None
    
    def simple_trading_strategy(self):
        """简单交易策略示例"""
        print(f"\n🤖 [{datetime.now().strftime('%H:%M:%S')}] 执行交易策略...")
        
        # 获取账户信息
        cash, total_assets = self.get_account_balance()
        print(f"💰 可用现金: HKD {cash:,.2f}")
        print(f"📊 总资产: HKD {total_assets:,.2f}")
        
        # 获取当前持仓
        positions = self.get_current_positions()
        if positions is not None and len(positions) > 0:
            print(f"📦 当前持仓 ({len(positions)}个):")
            for idx, row in positions.iterrows():
                code = row['code']
                qty = row['qty']
                cost = row.get('cost_price', 0)
                pnl = row.get('pl_ratio', 0)
                print(f"  {code}: {qty}股, 成本: {cost:.2f}, 盈亏: {pnl:.2f}%")
        
        # 示例：简单的买入逻辑
        # 这里可以添加您的交易策略
        # 例如：技术指标分析、市场情绪分析等
        
        # 示例策略：如果有现金且没有持仓，买入少量测试
        if cash > 10000 and (positions is None or len(positions) == 0):
            print("💡 策略建议：买入测试")
            # 这里可以添加实际的下单逻辑
            # self.place_order(code="HK.02800", qty=100, side=TrdSide.BUY)
        
        # 示例策略：如果持仓有盈利超过20%，考虑卖出部分
        if positions is not None and len(positions) > 0:
            for idx, row in positions.iterrows():
                pnl = row.get('pl_ratio', 0)
                if pnl > 20:  # 盈利超过20%
                    print(f"💡 策略建议：{row['code']} 盈利{pnl:.1f}%，考虑卖出部分")
                    # 这里可以添加实际的下单逻辑
        
        print("✅ 策略分析完成")
    
    def place_order(self, code, qty, side, price=None):
        """下单"""
        if price is None:
            price = self.get_stock_price(code)
            if price is None:
                print(f"❌ 无法获取 {code} 的价格")
                return False
        
        print(f"🛒 下单: {code} {side} {qty}股 @ {price:.2f}")
        
        ret, data = self.trd_ctx.place_order(
            price=price,
            qty=qty,
            code=code,
            trd_side=side,
            order_type=OrderType.NORMAL,
            trd_env=TrdEnv.SIMULATE,
            remark="自动交易"
        )
        
        if ret == RET_OK:
            order_id = data['order_id'].iloc[0]
            print(f"✅ 下单成功，订单ID: {order_id}")
            return True
        else:
            print(f"❌ 下单失败: {data}")
            return False
    
    def run(self):
        """运行自动交易"""
        print("=" * 60)
        print(f"🚀 富途自动交易系统启动")
        print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        if not self.connect():
            return
        
        # 检查交易时间
        if not self.is_trading_hours():
            print("⏰ 当前非交易时间，只进行监控")
        
        # 执行交易策略
        self.simple_trading_strategy()
        
        # 关闭连接
        self.trd_ctx.close()
        self.quote_ctx.close()
        print("\n✅ 自动交易完成")

def main():
    """主函数"""
    trader = AutoTrader()
    trader.run()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
安全版技术图表交易系统
确保只操作模拟环境，不碰真实账户
"""

import sys
import time
import json
import pandas as pd
from datetime import datetime, time as dt_time, timedelta
from futu import *

# 导入技术分析库
sys.path.append('/Users/gordonlui/.openclaw/workspace')
from technical_analysis import TechnicalAnalyzer, Pattern, Trend

class SafeTechnicalTrader:
    """安全版技术图表交易器（只操作模拟环境）"""
    
    def __init__(self):
        self.trd_ctx = None
        self.quote_ctx = None
        self.trading_hours = {
            'start': dt_time(9, 30),   # 港股开盘
            'end': dt_time(16, 0)      # 港股收盘
        }
        
        # 强制使用模拟环境
        self.trade_environment = TrdEnv.SIMULATE
        
        # 交易配置（正确的2% Rule版本）
        self.config = {
            'max_position_size': 0.25,   # 单只股票最大仓位比例 25%
            'stop_loss_pct': 0.02,       # 止损比例 2%
            'take_profit_pct': 0.10,     # 止盈比例 10%
            'max_risk_per_trade': 0.02,  # 2% Rule：每注风险金额 = 总资金 × 2%
            'rsi_overbought': 70,        # RSI超买线 70
            'rsi_oversold': 30,          # RSI超卖线 30
            'min_volume': 1000000,       # 最小成交量 100万
            'watchlist': [               # 监控列表
                "HK.02800",  # 盈富基金
                "HK.00700",  # 腾讯
                "HK.09988",  # 阿里巴巴
                "HK.01299",  # 友邦保险
                "HK.02318",  # 中国平安
                "HK.00992",  # 联想集团（新增，您手动买入）
            ]
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
            
            # 环境安全检查
            print(f"🔒 交易环境: {self.trade_environment} (模拟)")
            
            # 解锁交易
            ret, _ = self.trd_ctx.unlock_trade('')
            if ret != RET_OK:
                print("⚠️  交易解锁失败（模拟环境可能不需要）")
            
            print("✅ 连接成功")
            return True
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def check_account_safety(self):
        """检查账户安全性"""
        print("\n🔒 账户安全检查...")
        
        # 检查模拟账户资金
        ret, sim_data = self.trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK and len(sim_data) > 0:
            print(f"✅ 模拟账户可用:")
            cash = sim_data['cash'].iloc[0]
            total_assets = sim_data['total_assets'].iloc[0]
            print(f"   现金: HKD {cash:,.2f}")
            print(f"   总资产: HKD {total_assets:,.2f}")
        
        # 确认不操作真实账户
        ret, real_data = self.trd_ctx.accinfo_query()
        if ret == RET_OK and len(real_data) > 0:
            real_cash = real_data['cash'].iloc[0]
            print(f"⚠️  真实账户现金: HKD {real_cash:,.2f} (不会操作)")
        
        return True
    
    def is_trading_hours(self):
        """检查是否在交易时间内"""
        now = datetime.now().time()
        return self.trading_hours['start'] <= now <= self.trading_hours['end']
    
    def get_account_info(self):
        """获取账户信息（模拟环境）"""
        ret, data = self.trd_ctx.accinfo_query(trd_env=self.trade_environment)
        if ret == RET_OK and len(data) > 0:
            return {
                'cash': float(data['cash'].iloc[0]),
                'total_assets': float(data['total_assets'].iloc[0]),
                'market_val': float(data['market_val'].iloc[0]),
                'power': float(data['power'].iloc[0])
            }
        return None
    
    def get_current_positions(self):
        """获取当前持仓（模拟环境）"""
        ret, positions = self.trd_ctx.position_list_query(trd_env=self.trade_environment)
        if ret == RET_OK:
            return positions
        return None
    
    def analyze_stock(self, code):
        """分析单只股票"""
        # 获取当前价格
        ret, snapshot = self.quote_ctx.get_market_snapshot([code])
        if ret != RET_OK or len(snapshot) == 0:
            return None
        
        current_price = snapshot['last_price'].iloc[0]
        volume = snapshot['volume'].iloc[0]
        
        # 获取历史数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)
        
        ret, hist_data, _ = self.quote_ctx.request_history_kline(
            code=code,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            ktype=KLType.K_DAY,
            autype=AuType.QFQ
        )
        
        if ret != RET_OK:
            return None
        
        # 重命名列以匹配技术分析库
        hist_data = hist_data.rename(columns={'time_key': 'date'})
        
        # 创建技术分析器
        analyzer = TechnicalAnalyzer(hist_data)
        
        # 生成技术信号
        signals = analyzer.generate_signals()
        
        analysis = {
            'code': code,
            'current_price': current_price,
            'volume': volume,
            'trend': signals['trend'].value,
            'patterns': [p.value for p in signals['patterns']],
            'indicators': signals['indicators'],
            'recommendation': signals['recommendation']
        }
        
        return analysis
    
    def generate_trading_signals(self):
        """生成交易信号"""
        print(f"\n🎯 [{datetime.now().strftime('%H:%M:%S')}] 生成交易信号...")
        
        account_info = self.get_account_info()
        if account_info is None:
            print("❌ 无法获取账户信息")
            return []
        
        positions = self.get_current_positions()
        current_positions = {}
        if positions is not None and len(positions) > 0:
            for _, row in positions.iterrows():
                if row['qty'] > 0:  # 只统计有持仓的
                    current_positions[row['code']] = {
                        'qty': row['qty'],
                        'cost': row['cost_price'],
                        'market_val': row['market_val']
                    }
        
        print(f"💰 账户现金: HKD {account_info['cash']:,.2f}")
        print(f"📊 总资产: HKD {account_info['total_assets']:,.2f}")
        print(f"📦 当前持仓: {len(current_positions)}只股票")
        
        trading_signals = []
        
        # 分析监控列表中的股票
        for code in self.config['watchlist']:
            analysis = self.analyze_stock(code)
            if analysis is None:
                continue
            
            signal = {
                'code': code,
                'analysis': analysis,
                'action': 'HOLD',
                'reason': [],
                'quantity': 0,
                'price': analysis['current_price']
            }
            
            # 检查是否已持仓
            has_position = code in current_positions
            position_data = current_positions.get(code)
            
            # 生成买入信号
            if (analysis['recommendation'] == 'BUY' and 
                analysis['volume'] > self.config['min_volume'] and
                not has_position):
                
                buy_conditions = []
                
                # RSI超卖
                if analysis['indicators']['rsi'] < self.config['rsi_oversold']:
                    buy_conditions.append("RSI超卖")
                
                # 看涨形态
                bullish_patterns = [Pattern.BULLISH_ENGULFING.value, Pattern.HAMMER.value]
                if any(p in bullish_patterns for p in analysis['patterns']):
                    buy_conditions.append("看涨形态")
                
                if buy_conditions:
                    # 正确的2% Rule风险管理
                    # 每注风险金额 = 总资金 × 2%
                    risk_amount = account_info['total_assets'] * self.config['max_risk_per_trade']
                    
                    # 根据止损比例计算可买数量
                    # 风险金额 = 数量 × 价格 × 止损比例
                    # 数量 = 风险金额 ÷ (价格 × 止损比例)
                    max_quantity_by_risk = int(risk_amount / (analysis['current_price'] * self.config['stop_loss_pct']) / 100) * 100
                    
                    # 同时考虑仓位限制
                    max_investment = account_info['cash'] * self.config['max_position_size']
                    max_quantity_by_cash = int(max_investment / analysis['current_price'] / 100) * 100
                    
                    # 取两者中较小的
                    quantity = min(max_quantity_by_risk, max_quantity_by_cash, 10000)  # 限制最大数量
                    
                    if quantity >= 100:  # 至少1手
                        signal['action'] = 'BUY'
                        signal['reason'] = buy_conditions
                        signal['quantity'] = quantity
                        
                        # 添加正确的风险管理说明
                        actual_risk_amount = quantity * analysis['current_price'] * self.config['stop_loss_pct']
                        signal['risk_management'] = {
                            'risk_amount': risk_amount,
                            'actual_risk': actual_risk_amount,
                            'risk_pct_of_capital': (actual_risk_amount / account_info['total_assets']) * 100,
                            'position_size': quantity * analysis['current_price'],
                            'position_pct': (quantity * analysis['current_price'] / account_info['total_assets']) * 100,
                            'stop_loss_pct': self.config['stop_loss_pct'] * 100
                        }
                        
                        trading_signals.append(signal)
                        print(f"  ✅ 通过2% Rule检查：风险{actual_risk_amount:,.0f}/{risk_amount:,.0f}")
                    else:
                        print(f"  ⚠️  跳过买入{code}：可买数量不足（{quantity}股）")
            
            # 生成卖出信号
            elif (analysis['recommendation'] == 'SELL' and has_position):
                
                sell_conditions = []
                
                # RSI超买
                if analysis['indicators']['rsi'] > self.config['rsi_overbought']:
                    sell_conditions.append("RSI超买")
                
                # 看跌形态
                bearish_patterns = [Pattern.BEARISH_ENGULFING.value, Pattern.SHOOTING_STAR.value]
                if any(p in bearish_patterns for p in analysis['patterns']):
                    sell_conditions.append("看跌形态")
                
                # 止损止盈检查
                if position_data:
                    cost = position_data['cost']
                    current_price = analysis['current_price']
                    if cost > 0:
                        pnl_pct = (current_price - cost) / cost
                        
                        if pnl_pct < -self.config['stop_loss_pct']:
                            sell_conditions.append(f"止损触发 ({pnl_pct:.1%})")
                        elif pnl_pct > self.config['take_profit_pct']:
                            sell_conditions.append(f"止盈触发 ({pnl_pct:.1%})")
                
                if sell_conditions:
                    signal['action'] = 'SELL'
                    signal['reason'] = sell_conditions
                    signal['quantity'] = position_data['qty']  # 卖出全部持仓
                    
                    trading_signals.append(signal)
        
        return trading_signals
    
    def execute_trades(self, signals):
        """执行交易（模拟环境）"""
        if not signals:
            print("📭 没有交易信号")
            return
        
        print(f"\n🚀 执行交易（模拟环境）...")
        
        for signal in signals:
            code = signal['code']
            action = signal['action']
            quantity = signal['quantity']
            price = signal['price']
            reasons = signal['reason']
            
            if quantity <= 0:
                continue
            
            print(f"\n{'🛒' if action == 'BUY' else '💰'} {action} {code}")
            print(f"  数量: {quantity}股")
            print(f"  价格: {price:.2f}")
            print(f"  理由: {', '.join(reasons)}")
            
            # 确定交易方向
            trd_side = TrdSide.BUY if action == 'BUY' else TrdSide.SELL
            
            # 下单（模拟环境）
            # 调整数量为100的倍数（港股标准手数）
            adjusted_quantity = (quantity // 100) * 100
            if adjusted_quantity <= 0:
                print(f"  ⚠️  调整后数量为0，跳过")
                continue
            
            # 使用更短的备注信息
            remark = "技术交易"
            if reasons:
                # 只取第一个理由的前20个字符
                first_reason = str(reasons[0])[:20]
                remark = f"技术:{first_reason}"
            
            ret, data = self.trd_ctx.place_order(
                price=price,
                qty=adjusted_quantity,
                code=code,
                trd_side=trd_side,
                order_type=OrderType.NORMAL,
                trd_env=self.trade_environment,
                remark=remark
            )
            
            if ret == RET_OK:
                order_id = data['order_id'].iloc[0]
                print(f"  ✅ 下单成功，订单ID: {order_id}")
            else:
                print(f"  ❌ 下单失败: {data}")
    
    def run(self, execute_trades=False):
        """运行交易系统"""
        print("=" * 70)
        print(f"🔒 安全版技术图表交易系统")
        print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 环境: 模拟账户（只操作模拟环境）")
        print(f"📊 策略: 平行通道 + 黄金分割 + 旗形 + K线")
        print("=" * 70)
        
        if not self.connect():
            return
        
        # 账户安全检查
        self.check_account_safety()
        
        # 检查交易时间
        if not self.is_trading_hours():
            print("⏰ 当前非交易时间，只进行分析")
            execute_trades = False
        
        # 生成交易信号
        signals = self.generate_trading_signals()
        
        # 执行或显示交易
        if execute_trades and signals:
            self.execute_trades(signals)
        elif signals:
            print(f"\n📋 交易信号（模拟）:")
            for signal in signals:
                action_emoji = "🟢" if signal['action'] == 'BUY' else "🔴"
                print(f"{action_emoji} {signal['action']} {signal['code']}")
                print(f"   价格: {signal['price']:.2f}, 数量: {signal['quantity']}")
                print(f"   理由: {', '.join(signal['reason'])}")
        else:
            print("📭 没有交易信号")
        
        # 关闭连接
        self.trd_ctx.close()
        self.quote_ctx.close()
        print(f"\n✅ 交易系统运行完成")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='安全版技术图表交易系统（只操作模拟环境）')
    parser.add_argument('--execute', action='store_true', help='执行实际交易（模拟环境）')
    
    args = parser.parse_args()
    
    trader = SafeTechnicalTrader()
    trader.run(execute_trades=args.execute)

if __name__ == "__main__":
    main()
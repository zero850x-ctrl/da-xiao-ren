#!/usr/bin/env python3
"""
富途技术图表派交易系统
基于平行通道、黄金分割、旗形、K线等技术分析
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

class TechnicalTrader:
    """技术图表派交易器"""
    
    def __init__(self, use_real_account=False):
        self.trd_ctx = None
        self.quote_ctx = None
        self.use_real_account = use_real_account
        self.trading_hours = {
            'start': dt_time(9, 30),   # 港股开盘
            'end': dt_time(16, 0)      # 港股收盘
        }
        
        # 交易配置
        self.config = {
            'max_position_size': 0.2,  # 单只股票最大仓位比例
            'stop_loss_pct': 0.05,     # 止损比例 5%
            'take_profit_pct': 0.15,   # 止盈比例 15%
            'rsi_overbought': 65,      # RSI超买线（降低以增加卖出机会）
            'rsi_oversold': 35,        # RSI超卖线（提高以增加买入机会）
            'min_volume': 1000000,     # 最小成交量
            'watchlist': [             # 监控列表
                "HK.02800",  # 盈富基金
                "HK.00700",  # 腾讯
                "HK.09988",  # 阿里巴巴
                "HK.01299",  # 友邦保险
                "HK.02318",  # 中国平安
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
    
    def get_account_info(self):
        """获取账户信息"""
        ret, data = self.trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK and len(data) > 0:
            return {
                'cash': float(data['cash'].iloc[0]),
                'total_assets': float(data['total_assets'].iloc[0]),
                'market_val': float(data['market_val'].iloc[0]),
                'power': float(data['power'].iloc[0])
            }
        return None
    
    def get_current_positions(self):
        """获取当前持仓"""
        # 先尝试真实环境
        ret, positions = self.trd_ctx.position_list_query(trd_env=TrdEnv.REAL)
        if ret == RET_OK:
            return positions
        
        # 如果真实环境没有持仓，尝试模拟环境
        ret, positions = self.trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK:
            return positions
        
        print(f"⚠️  持仓查询失败: {positions}")
        return None
    
    def get_historical_data(self, code: str, days: int = 100):
        """获取历史K线数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        ret, data, page_req_key = self.quote_ctx.request_history_kline(
            code=code,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            ktype=KLType.K_DAY,  # 日K线
            max_count=days
        )
        
        if ret == RET_OK:
            # 转换为标准格式
            df = pd.DataFrame({
                'date': data['time_key'],
                'open': data['open'],
                'high': data['high'],
                'low': data['low'],
                'close': data['close'],
                'volume': data['volume']
            })
            return df
        else:
            print(f"❌ 获取 {code} 历史数据失败")
            return None
    
    def get_realtime_data(self, code: str):
        """获取实时数据"""
        ret, data = self.quote_ctx.get_market_snapshot([code])
        if ret == RET_OK and len(data) > 0:
            return {
                'last_price': float(data['last_price'].iloc[0]),
                'open': float(data['open_price'].iloc[0]),
                'high': float(data['high_price'].iloc[0]),
                'low': float(data['low_price'].iloc[0]),
                'volume': int(data['volume'].iloc[0]),
                'turnover': float(data['turnover'].iloc[0]),
                'amplitude': float(data['amplitude'].iloc[0])
            }
        return None
    
    def analyze_stock(self, code: str):
        """分析股票技术面"""
        print(f"\n📈 分析 {code} ...")
        
        # 获取历史数据
        hist_data = self.get_historical_data(code, days=100)
        if hist_data is None or len(hist_data) < 50:
            print(f"  ⚠️  数据不足，跳过分析")
            return None
        
        # 获取实时数据
        realtime_data = self.get_realtime_data(code)
        if realtime_data is None:
            print(f"  ❌ 无法获取实时数据")
            return None
        
        # 技术分析
        analyzer = TechnicalAnalyzer(hist_data)
        signals = analyzer.generate_signals()
        
        # 添加实时价格
        signals['current_price'] = realtime_data['last_price']
        signals['volume'] = realtime_data['volume']
        signals['code'] = code
        
        # 平行通道分析
        channel = analyzer.find_parallel_channel()
        if channel:
            signals['parallel_channel'] = channel
            print(f"  📊 平行通道: {channel['trend']}趋势，宽度: {channel['channel_width']:.2f}")
        
        # 黄金分割位
        swing_high = hist_data['high'].max()
        swing_low = hist_data['low'].min()
        golden_levels = analyzer.calculate_golden_ratio_levels(swing_high, swing_low)
        signals['golden_levels'] = golden_levels
        
        # 当前价格相对于黄金分割位
        current_price = realtime_data['last_price']
        for level_name, level_price in golden_levels.items():
            if abs(current_price - level_price) / level_price < 0.01:  # 1%范围内
                signals['near_golden_level'] = level_name
                print(f"  📍 接近黄金分割位: {level_name} ({level_price:.2f})")
                break
        
        print(f"  📊 趋势: {signals['trend'].value}")
        print(f"  📈 形态: {[p.value for p in signals['patterns']]}")
        print(f"  🔢 RSI: {signals['indicators']['rsi']:.1f}")
        print(f"  💰 价格: {current_price:.2f}")
        # 注意：这里显示的是技术分析的推荐，最终交易建议在generate_trading_signals中确定
        
        return signals
    
    def generate_trading_signals(self):
        """生成交易信号"""
        print(f"\n🎯 [{datetime.now().strftime('%H:%M:%S')}] 生成交易信号...")
        
        account_info = self.get_account_info()
        if not account_info:
            print("❌ 无法获取账户信息")
            return []
        
        positions = self.get_current_positions()
        current_positions = {}
        if positions is not None and len(positions) > 0:
            for _, row in positions.iterrows():
                if row['qty'] > 0:  # 只统计有实际持仓的股票
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
            if (analysis['volume'] > self.config['min_volume'] and
                not has_position):
                
                # 检查技术条件
                buy_conditions = []
                
                # RSI超卖
                if analysis['indicators']['rsi'] < self.config['rsi_oversold']:
                    buy_conditions.append(f"RSI超卖({analysis['indicators']['rsi']:.1f}<{self.config['rsi_oversold']})")
                
                # 看涨形态
                bullish_patterns = [Pattern.BULLISH_ENGULFING.value, Pattern.HAMMER.value]
                if any(p.value in bullish_patterns for p in analysis['patterns']):
                    buy_conditions.append("看涨形态")
                
                # 接近黄金分割支撑位
                if 'near_golden_level' in analysis:
                    level = analysis['near_golden_level']
                    if level in ['23.6%', '38.2%', '50.0%']:
                        buy_conditions.append(f"黄金分割支撑位{level}")
                
                if buy_conditions:
                    signal['action'] = 'BUY'
                    signal['reason'] = buy_conditions
                    
                    # 计算买入数量
                    max_investment = account_info['cash'] * self.config['max_position_size']
                    
                    # 不同股票的最小交易单位
                    min_lot = 100  # 默认100股
                    if code == "HK.02800":  # 盈富基金
                        min_lot = 500
                    
                    quantity = int(max_investment / analysis['current_price'] / min_lot) * min_lot  # 整手
                    quantity = max(quantity, min_lot)  # 至少最小交易单位
                    signal['quantity'] = min(quantity, 10000)  # 限制最大数量
                    
                    trading_signals.append(signal)
            
            # 生成卖出信号
            elif has_position:
                
                # 检查技术条件
                sell_conditions = []
                
                # RSI超买
                if analysis['indicators']['rsi'] > self.config['rsi_overbought']:
                    sell_conditions.append(f"RSI超买({analysis['indicators']['rsi']:.1f}>{self.config['rsi_overbought']})")
                
                # 看跌形态
                bearish_patterns = [Pattern.BEARISH_ENGULFING.value, Pattern.SHOOTING_STAR.value]
                if any(p.value in bearish_patterns for p in analysis['patterns']):
                    sell_conditions.append("看跌形态")
                
                # 接近黄金分割阻力位（只有在有盈利时才考虑卖出）
                if 'near_golden_level' in analysis and position_data and position_data['cost'] > 0:
                    level = analysis['near_golden_level']
                    cost = position_data['cost']
                    current_price = analysis['current_price']
                    profit_pct = (current_price - cost) / cost
                    
                    # 只有在有盈利且接近阻力位时才考虑卖出
                    if level in ['61.8%', '78.6%', '100.0%'] and profit_pct > 0.02:  # 至少2%盈利
                        sell_conditions.append(f"黄金分割阻力位{level} (盈利{profit_pct:.1%})")
                
                # 止损检查
                if position_data and position_data['cost'] > 0:
                    cost = position_data['cost']
                    current_price = analysis['current_price']
                    loss_pct = (current_price - cost) / cost
                    
                    if loss_pct < -self.config['stop_loss_pct']:
                        sell_conditions.append(f"止损触发 ({loss_pct:.1%})")
                    
                    # 止盈检查
                    elif loss_pct > self.config['take_profit_pct']:
                        sell_conditions.append(f"止盈触发 ({loss_pct:.1%})")
                
                if sell_conditions:
                    signal['action'] = 'SELL'
                    signal['reason'] = sell_conditions
                    signal['quantity'] = position_data['qty']  # 卖出全部持仓
                    
                    trading_signals.append(signal)
        
        return trading_signals
    
    def execute_trades(self, signals):
        """执行交易"""
        if not signals:
            print("📭 没有交易信号")
            return
        
        print(f"\n🚀 执行交易...")
        
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
            
            # 下单
            ret, data = self.trd_ctx.place_order(
                price=price,
                qty=quantity,
                code=code,
                trd_side=trd_side,
                order_type=OrderType.NORMAL,
                trd_env=TrdEnv.SIMULATE,
                remark=f"技术交易:{','.join(reasons)}"
            )
            
            if ret == RET_OK:
                order_id = data['order_id'].iloc[0]
                print(f"  ✅ 下单成功，订单ID: {order_id}")
            else:
                print(f"  ❌ 下单失败: {data}")
    
    def run_analysis_only(self):
        """只进行分析，不执行交易"""
        print(f"\n🔍 [{datetime.now().strftime('%H:%M:%S')}] 技术分析模式")
        
        signals = self.generate_trading_signals()
        
        if signals:
            print(f"\n📋 交易信号总结:")
            for signal in signals:
                action_emoji = "🟢" if signal['action'] == 'BUY' else "🔴"
                print(f"{action_emoji} {signal['action']} {signal['code']}")
                print(f"   价格: {signal['price']:.2f}, 数量: {signal['quantity']}")
                print(f"   理由: {', '.join(signal['reason'])}")
        else:
            print("📭 没有交易信号")
        
        return signals
    
    def run(self, execute_trades=False):
        """运行交易系统"""
        print("=" * 70)
        print(f"🚀 富途技术图表派交易系统")
        print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 策略: 平行通道 + 黄金分割 + 旗形 + K线")
        print("=" * 70)
        
        if not self.connect():
            return
        
        # 检查交易时间
        if not self.is_trading_hours():
            print("⏰ 当前非交易时间，只进行分析")
            execute_trades = False
        
        # 生成交易信号
        signals = self.generate_trading_signals()
        
        # 如果没有信号，尝试强制生成一个买入信号（用于测试）
        if not signals and execute_trades:
            print("⚠️  没有自动生成的交易信号，尝试测试买入...")
            # 选择第一个监控股票
            test_code = self.config['watchlist'][0]
            ret, quote = self.quote_ctx.get_market_snapshot([test_code])
            if ret == RET_OK:
                current_price = quote.iloc[0]['last_price']
                
                # 确定最小交易单位
                min_lot = 500 if test_code == "HK.02800" else 100
                
                test_signal = {
                    'code': test_code,
                    'action': 'BUY',
                    'reason': ['测试交易'],
                    'quantity': min_lot,  # 最小交易单位
                    'price': current_price
                }
                signals = [test_signal]
        
        # 执行或显示交易
        if execute_trades and signals:
            self.execute_trades(signals)
        elif signals:
            print(f"\n📋 交易信号（模拟）:")
            for signal in signals:
                action_emoji = "🟢" if signal['action'] == 'BUY' else "🔴"
                print(f"{action_emoji} {signal['action']} {signal['code']} "
                      f"{signal['quantity']}股 @ {signal['price']:.2f}")
                print(f"   理由: {', '.join(signal['reason'])}")
        
        # 关闭连接
        self.trd_ctx.close()
        self.quote_ctx.close()
        print(f"\n✅ 交易系统运行完成")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='富途技术图表派交易系统')
    parser.add_argument('--execute', action='store_true', help='执行实际交易（谨慎使用！）')
    parser.add_argument('--analyze-only', action='store_true', help='只进行分析（安全模式）')
    parser.add_argument('--real-account', action='store_true', help='使用真实账户（默认模拟）')
    
    args = parser.parse_args()
    
    # 安全限制：如果是真实账户，强制只分析模式
    if args.real_account:
        print("⚠️  真实账户模式：强制只分析，不执行交易")
        args.execute = False
        args.analyze_only = True
    
    trader = TechnicalTrader(use_real_account=args.real_account)
    
    if args.analyze_only:
        trader.connect()
        trader.run_analysis_only()
        trader.trd_ctx.close()
        trader.quote_ctx.close()
    else:
        trader.run(execute_trades=args.execute)

if __name__ == "__main__":
    main()
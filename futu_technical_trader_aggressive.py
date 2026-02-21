#!/usr/bin/env python3
"""
积极版技术图表交易系统
调整参数以在横盘市场中也能找到交易机会
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

class AggressiveTechnicalTrader:
    """积极版技术图表交易器（只操作模拟环境）"""
    
    def __init__(self):
        self.trd_ctx = None
        self.quote_ctx = None
        self.trading_hours = {
            'start': dt_time(9, 30),   # 港股开盘
            'end': dt_time(16, 0)      # 港股收盘
        }
        
        # 强制使用模拟环境
        self.trade_environment = TrdEnv.SIMULATE
        
        # 更积极的交易配置
        self.config = {
            'max_position_size': 0.15,  # 单只股票最大仓位比例（降低风险）
            'stop_loss_pct': 0.03,      # 止损比例 3%（更紧）
            'take_profit_pct': 0.08,    # 止盈比例 8%（更保守）
            'rsi_overbought': 60,       # RSI超买线（更敏感）
            'rsi_oversold': 40,         # RSI超卖线（更敏感）
            'min_volume': 500000,       # 最小成交量（降低要求）
            'watchlist': [              # 监控列表（只关注流动性最好的）
                "HK.02800",  # 盈富基金（ETF，波动较小）
                "HK.00700",  # 腾讯（流动性好）
            ]
        }
        
    def connect(self):
        """连接富途API"""
        print(f"🔗 [{datetime.now().strftime('%H:%M:%S')}] 连接富途API...")
        try:
            self.trd_ctx = OpenSecTradeContext(
                host='127.0.0.1',
                port=11111
            )
            self.quote_ctx = OpenQuoteContext(
                host='127.0.0.1',
                port=11111
            )
            
            # 解锁交易（模拟环境）
            ret, data = self.trd_ctx.unlock_trade(password='123456')
            if ret != RET_OK:
                print("⚠️  交易解锁失败（模拟环境可能不需要）")
            
            print(f"🔒 交易环境: {self.trade_environment} (模拟)")
            return True
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
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
        start_date = end_date - timedelta(days=30)  # 缩短时间窗口
        
        ret, hist_data, _ = self.quote_ctx.request_history_kline(
            code=code,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            ktype=KLType.K_DAY,
            autype=AuType.QFQ
        )
        
        if ret != RET_OK:
            return None
        
        # 准备数据用于技术分析
        analysis_data = hist_data[['time_key', 'open', 'high', 'low', 'close', 'volume']].copy()
        analysis_data.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        # 技术分析
        analyzer = TechnicalAnalyzer(analysis_data)
        signals = analyzer.generate_signals()
        
        # 计算移动平均线
        sma_10 = hist_data['close'].tail(10).mean()
        sma_20 = hist_data['close'].tail(20).mean()
        
        return {
            'code': code,
            'price': current_price,
            'volume': volume,
            'signals': signals,
            'sma_10': sma_10,
            'sma_20': sma_20,
            'hist_data': hist_data
        }
    
    def generate_trading_signals(self):
        """生成交易信号（积极策略）"""
        print(f"🎯 [{datetime.now().strftime('%H:%M:%S')}] 生成交易信号（积极策略）...")
        
        account_info = self.get_account_info()
        if not account_info:
            print("❌ 无法获取账户信息")
            return []
        
        positions = self.get_current_positions()
        position_map = {}
        if positions is not None and len(positions) > 0:
            for _, row in positions.iterrows():
                if row['qty'] > 0:
                    position_map[row['code']] = {
                        'qty': row['qty'],
                        'cost': row['cost_price']
                    }
        
        print(f"💰 账户现金: HKD {account_info['cash']:,.2f}")
        print(f"📊 总资产: HKD {account_info['total_assets']:,.2f}")
        print(f"📦 当前持仓: {len(position_map)}只股票")
        
        trading_signals = []
        available_cash = account_info['cash']
        
        for code in self.config['watchlist']:
            analysis = self.analyze_stock(code)
            if not analysis:
                continue
            
            signals = analysis['signals']
            current_price = analysis['price']
            volume = analysis['volume']
            sma_10 = analysis['sma_10']
            sma_20 = analysis['sma_20']
            
            position_data = position_map.get(code)
            
            signal = {
                'code': code,
                'price': current_price,
                'action': 'HOLD',
                'reason': [],
                'quantity': 0
            }
            
            # 买入信号（更积极的条件）
            buy_conditions = []
            
            # 1. RSI条件（更敏感）
            if signals['indicators']['rsi'] < self.config['rsi_oversold']:
                buy_conditions.append(f"RSI超卖 ({signals['indicators']['rsi']:.1f})")
            
            # 2. 价格低于短期均线
            if current_price < sma_10 * 0.98:  # 价格低于SMA10 2%
                buy_conditions.append(f"价格低于SMA10 ({current_price:.2f} < {sma_10:.2f})")
            
            # 3. 看涨形态
            bullish_patterns = [Pattern.BULLISH_ENGULFING.value, Pattern.HAMMER.value]
            if any(p in bullish_patterns for p in signals['patterns']):
                buy_conditions.append("看涨形态")
            
            # 4. 横盘市场中的反弹机会
            if signals['trend'] == Trend.SIDEWAYS and current_price < sma_20:
                # 在横盘市场中，价格低于中期均线可能是买入机会
                buy_conditions.append("横盘市场中价格低于SMA20")
            
            if buy_conditions and volume >= self.config['min_volume']:
                # 计算买入数量
                max_investment = available_cash * self.config['max_position_size']
                max_shares = int(max_investment / current_price)
                
                if max_shares >= 100:  # 至少100股
                    signal['action'] = 'BUY'
                    signal['reason'] = buy_conditions
                    # 调整为100的倍数（港股标准手数）
                    signal['quantity'] = (min(max_shares, 1000) // 100) * 100
                    
                    trading_signals.append(signal)
            
            # 卖出信号
            if position_data and position_data['qty'] > 0:
                sell_conditions = []
                
                # 1. RSI超买
                if signals['indicators']['rsi'] > self.config['rsi_overbought']:
                    sell_conditions.append(f"RSI超买 ({signals['indicators']['rsi']:.1f})")
                
                # 2. 价格高于短期均线
                if current_price > sma_10 * 1.02:  # 价格高于SMA10 2%
                    sell_conditions.append(f"价格高于SMA10 ({current_price:.2f} > {sma_10:.2f})")
                
                # 3. 看跌形态
                bearish_patterns = [Pattern.BEARISH_ENGULFING.value, Pattern.SHOOTING_STAR.value]
                if any(p in bearish_patterns for p in signals['patterns']):
                    sell_conditions.append("看跌形态")
                
                # 4. 止损止盈检查
                cost = position_data['cost']
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
            # 使用更短的备注信息
            remark = "积极策略"
            if reasons:
                # 只取第一个理由的前20个字符
                first_reason = str(reasons[0])[:20]
                remark = f"积极:{first_reason}"
            
            ret, data = self.trd_ctx.place_order(
                price=price,
                qty=quantity,
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
        print(f"⚡ 积极版技术图表交易系统")
        print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 环境: 模拟账户（只操作模拟环境）")
        print(f"📊 策略: 积极策略 - 适应横盘市场")
        print("=" * 70)
        
        if not self.connect():
            return
        
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
                print(f"   价格: {signal['price']:.2f}")
                print(f"   数量: {signal['quantity']}股")
                print(f"   理由: {', '.join(signal['reason'])}")
        else:
            print("\n📭 没有交易信号")
        
        # 关闭连接
        self.quote_ctx.close()
        self.trd_ctx.close()
        
        print("\n✅ 交易系统运行完成")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='积极版技术图表交易系统')
    parser.add_argument('--execute', action='store_true', help='执行交易（否则只显示信号）')
    
    args = parser.parse_args()
    
    trader = AggressiveTechnicalTrader()
    trader.run(execute_trades=args.execute)
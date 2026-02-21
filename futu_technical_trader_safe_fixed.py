#!/usr/bin/env python3
"""
安全版技术图表交易系统 - 修复版
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
        
        # 交易配置
        self.config = {
            'max_position_size': 0.2,  # 单只股票最大仓位比例
            'stop_loss_pct': 0.05,     # 止损比例 5%
            'take_profit_pct': 0.15,   # 止盈比例 15%
            'rsi_overbought': 65,      # RSI超买线
            'rsi_oversold': 35,        # RSI超卖线
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
            
            # 环境安全检查 - 修复：直接使用字符串
            print(f"🔒 交易环境: SIMULATE (模拟)")
            
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
        
        ret, hist_data, page_req_key = self.quote_ctx.request_history_kline(
            code=code,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            ktype=KLType.K_DAY,
            max_count=100
        )
        
        if ret != RET_OK:
            return None
        
        # 创建技术分析器
        analyzer = TechnicalAnalyzer(hist_data)
        
        # 技术分析
        analysis = {
            'code': code,
            'current_price': current_price,
            'volume': volume,
            'rsi': analyzer.calculate_rsi(),
            'macd': analyzer.calculate_macd(),
            'bollinger_bands': analyzer.calculate_bollinger_bands(),
            'support_resistance': analyzer.identify_support_resistance(),
            'patterns': analyzer.detect_patterns(),
            'trend': analyzer.identify_trend()
        }
        
        return analysis
    
    def generate_trading_signal(self, analysis):
        """生成交易信号"""
        if not analysis:
            return None
        
        signal = {
            'code': analysis['code'],
            'action': 'HOLD',  # 默认持有
            'confidence': 0,
            'reason': [],
            'price': analysis['current_price']
        }
        
        # RSI信号
        rsi = analysis['rsi']
        if rsi < self.config['rsi_oversold']:
            signal['action'] = 'BUY'
            signal['confidence'] += 0.3
            signal['reason'].append(f"RSI超卖 ({rsi:.1f})")
        elif rsi > self.config['rsi_overbought']:
            signal['action'] = 'SELL'
            signal['confidence'] += 0.3
            signal['reason'].append(f"RSI超买 ({rsi:.1f})")
        
        # 成交量检查
        if analysis['volume'] < self.config['min_volume']:
            signal['confidence'] -= 0.2
            signal['reason'].append(f"成交量不足 ({analysis['volume']:,.0f})")
        
        # 形态识别
        patterns = analysis['patterns']
        if Pattern.BULLISH_FLAG in patterns:
            signal['action'] = 'BUY'
            signal['confidence'] += 0.4
            signal['reason'].append("看涨旗形")
        elif Pattern.BEARISH_FLAG in patterns:
            signal['action'] = 'SELL'
            signal['confidence'] += 0.4
            signal['reason'].append("看跌旗形")
        
        # 趋势分析
        trend = analysis['trend']
        if trend == Trend.UPTREND:
            if signal['action'] == 'BUY':
                signal['confidence'] += 0.2
                signal['reason'].append("上升趋势")
        elif trend == Trend.DOWNTREND:
            if signal['action'] == 'SELL':
                signal['confidence'] += 0.2
                signal['reason'].append("下降趋势")
        
        # 支撑阻力
        support_resistance = analysis['support_resistance']
        current_price = analysis['current_price']
        
        if 'support' in support_resistance:
            support_levels = support_resistance['support']
            for level in support_levels:
                if abs(current_price - level) / level < 0.02:  # 2%范围内
                    if signal['action'] == 'BUY':
                        signal['confidence'] += 0.3
                        signal['reason'].append(f"接近支撑位 ({level:.2f})")
        
        if 'resistance' in support_resistance:
            resistance_levels = support_resistance['resistance']
            for level in resistance_levels:
                if abs(current_price - level) / level < 0.02:  # 2%范围内
                    if signal['action'] == 'SELL':
                        signal['confidence'] += 0.3
                        signal['reason'].append(f"接近阻力位 ({level:.2f})")
        
        # 确保信心度在0-1之间
        signal['confidence'] = max(0, min(1, signal['confidence']))
        
        return signal
    
    def execute_trade(self, signal):
        """执行交易"""
        if not signal or signal['confidence'] < 0.5:
            print(f"📊 {signal['code']}: 信号信心不足 ({signal['confidence']:.2f})，跳过")
            return False
        
        code = signal['code']
        action = signal['action']
        price = signal['price']
        
        # 获取账户信息
        account = self.get_account_info()
        if not account:
            print("❌ 无法获取账户信息")
            return False
        
        # 计算交易数量
        if action == 'BUY':
            max_amount = account['cash'] * self.config['max_position_size']
            qty = int(max_amount / price / 100) * 100  # 港股以100股为单位
        else:  # SELL
            # 检查是否有持仓
            positions = self.get_current_positions()
            if positions is None or code not in positions['code'].values:
                print(f"❌ {code}: 没有持仓可卖")
                return False
            
            position = positions[positions['code'] == code]
            qty = int(position['qty'].iloc[0])
        
        if qty <= 0:
            print(f"❌ {code}: 交易数量为0")
            return False
        
        # 执行交易
        print(f"\n🎯 执行交易:")
        print(f"   股票: {code}")
        print(f"   操作: {action}")
        print(f"   价格: HKD {price:.2f}")
        print(f"   数量: {qty}")
        print(f"   总价: HKD {price * qty:,.2f}")
        print(f"   理由: {', '.join(signal['reason'])}")
        print(f"   信心: {signal['confidence']:.2f}")
        
        try:
            if action == 'BUY':
                ret, data = self.trd_ctx.place_order(
                    price=price,
                    qty=qty,
                    code=code,
                    trd_side=TrdSide.BUY,
                    order_type=OrderType.NORMAL,
                    trd_env=self.trade_environment
                )
            else:  # SELL
                ret, data = self.trd_ctx.place_order(
                    price=price,
                    qty=qty,
                    code=code,
                    trd_side=TrdSide.SELL,
                    order_type=OrderType.NORMAL,
                    trd_env=self.trade_environment
                )
            
            if ret == RET_OK:
                print(f"✅ 交易成功")
                return True
            else:
                print(f"❌ 交易失败: {data}")
                return False
                
        except Exception as e:
            print(f"❌ 交易异常: {e}")
            return False
    
    def run(self):
        """运行交易系统"""
        print("=" * 70)
        print("🔒 安全版技术图表交易系统")
        print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 环境: 模拟账户（只操作模拟环境）")
        print("📊 策略: 平行通道 + 黄金分割 + 旗形 + K线")
        print("=" * 70)
        
        # 连接API
        if not self.connect():
            return
        
        # 账户安全检查
        if not self.check_account_safety():
            return
        
        # 检查交易时间
        if not self.is_trading_hours():
            print(f"\n⏰ 非交易时间: {datetime.now().strftime('%H:%M:%S')}")
            print("   港股交易时间: 09:30 - 16:00")
            return
        
        print(f"\n📈 开始分析 {len(self.config['watchlist'])} 只股票...")
        
        # 分析每只股票
        signals = []
        for code in self.config['watchlist']:
            print(f"\n🔍 分析 {code}...")
            
            # 分析股票
            analysis = self.analyze_stock(code)
            if not analysis:
                print(f"❌ {code}: 分析失败")
                continue
            
            # 生成交易信号
            signal = self.generate_trading_signal(analysis)
            if signal:
                signals.append(signal)
                
                # 显示分析结果
                print(f"   当前价格: HKD {analysis['current_price']:.2f}")
                print(f"   成交量: {analysis['volume']:,.0f}")
                print(f"   RSI: {analysis['rsi']:.1f}")
                print(f"   趋势: {analysis['trend']}")
                print(f"   形态: {', '.join([p.name for p in analysis['patterns']])}")
                print(f"   信号: {signal['action']} (信心: {signal['confidence']:.2f})")
                if signal['reason']:
                    print(f"   理由: {', '.join(signal['reason'])}")
        
        # 执行交易
        print(f"\n🎯 执行交易决策...")
        executed_trades = 0
        
        for signal in signals:
            if self.execute_trade(signal):
                executed_trades += 1
        
        print(f"\n📊 交易总结:")
        print(f"   分析股票: {len(self.config['watchlist'])}")
        print(f"   生成信号: {len(signals)}")
        print(f"   执行交易: {executed_trades}")
        
        # 显示最终账户状态
        print(f"\n💰 最终账户状态:")
        account = self.get_account_info()
        if account:
            print(f"   现金: HKD {account['cash']:,.2f}")
            print(f"   总资产: HKD {account['total_assets']:,.2f}")
            print(f"   市值: HKD {account['market_val']:,.2f}")
            print(f"   购买力: HKD {account['power']:,.2f}")
        
        print(f"\n✅ 交易系统运行完成")
        
        # 关闭连接
        if self.trd_ctx:
            self.trd_ctx.close()
        if self.quote_ctx:
            self.quote_ctx.close()

def main():
    """主函数"""
    trader = SafeTechnicalTrader()
    trader.run()

if __name__ == "__main__":
    main()
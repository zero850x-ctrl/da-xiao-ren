#!/usr/bin/env python3
"""
安全模式技术图表分析器
只进行分析，不执行任何交易
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

class SafeTechnicalAnalyzer:
    """安全模式技术分析器（只分析不交易）"""
    
    def __init__(self):
        self.trd_ctx = None
        self.quote_ctx = None
        self.trading_hours = {
            'start': dt_time(9, 30),   # 港股开盘
            'end': dt_time(16, 0)      # 港股收盘
        }
        
        # 分析配置
        self.config = {
            'watchlist': [             # 监控列表
                "HK.02800",  # 盈富基金
                "HK.00700",  # 腾讯
                "HK.09988",  # 阿里巴巴
                "HK.01299",  # 友邦保险
                "HK.02318",  # 中国平安
            ],
            'rsi_overbought': 70,      # RSI超买线
            'rsi_oversold': 30,        # RSI超卖线
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
            
            print("✅ 连接成功")
            return True
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def get_account_status(self):
        """获取账户状态（只读）"""
        print("\n💰 账户状态检查...")
        
        # 检查真实账户
        ret, real_data = self.trd_ctx.accinfo_query()
        if ret == RET_OK and len(real_data) > 0:
            print("📊 真实账户:")
            for idx, row in real_data.iterrows():
                print(f"   现金: HKD {row['cash']:,.2f}")
                print(f"   总资产: HKD {row['total_assets']:,.2f}")
                print(f"   持仓市值: HKD {row['market_val']:,.2f}")
        
        # 检查模拟账户
        ret, sim_data = self.trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE)
        if ret == RET_OK and len(sim_data) > 0:
            print("\n🔄 模拟账户:")
            for idx, row in sim_data.iterrows():
                print(f"   现金: HKD {row['cash']:,.2f}")
                print(f"   总资产: HKD {row['total_assets']:,.2f}")
    
    def get_historical_data(self, code, days=30):
        """获取历史数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        ret, data = self.quote_ctx.get_history_kline(
            code=code,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            ktype=KLType.K_DAY,
            autype=AuType.QFQ
        )
        
        if ret == RET_OK:
            return data
        return None
    
    def analyze_stock(self, code):
        """分析单只股票"""
        print(f"\n📈 分析 {code} ...")
        
        # 获取当前价格
        ret, snapshot = self.quote_ctx.get_market_snapshot([code])
        if ret != RET_OK or len(snapshot) == 0:
            print(f"  ❌ 无法获取数据")
            return None
        
        current_price = snapshot['last_price'].iloc[0]
        volume = snapshot['volume'].iloc[0]
        
        # 获取历史数据
        hist_data = self.get_historical_data(code, 60)
        if hist_data is None:
            print(f"  ❌ 无法获取历史数据")
            return None
        
        # 创建技术分析器
        analyzer = TechnicalAnalyzer(hist_data)
        
        # 生成技术信号
        signals = analyzer.generate_signals()
        
        # 显示分析结果
        analysis = {
            'code': code,
            'current_price': current_price,
            'volume': volume,
            'trend': signals['trend'].value,
            'patterns': [p.value for p in signals['patterns']],
            'indicators': signals['indicators'],
            'recommendation': signals['recommendation']
        }
        
        # 输出分析结果
        print(f"  💰 价格: {current_price:.2f}")
        print(f"  📊 趋势: {analysis['trend']}")
        
        if analysis['patterns']:
            print(f"  📈 形态: {analysis['patterns']}")
        
        print(f"  🔢 RSI: {analysis['indicators']['rsi']:.1f}")
        print(f"  📋 建议: {analysis['recommendation']}")
        
        return analysis
    
    def run_analysis(self):
        """运行安全分析"""
        print("=" * 70)
        print(f"🔒 安全模式技术图表分析系统")
        print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 模式: 只分析，不交易")
        print(f"📊 策略: 平行通道 + 黄金分割 + 旗形 + K线")
        print("=" * 70)
        
        if not self.connect():
            return
        
        # 显示账户状态
        self.get_account_status()
        
        print(f"\n🎯 [{datetime.now().strftime('%H:%M:%S')}] 技术分析开始...")
        
        # 分析所有监控股票
        all_analysis = []
        for code in self.config['watchlist']:
            analysis = self.analyze_stock(code)
            if analysis:
                all_analysis.append(analysis)
        
        # 生成总结报告
        print(f"\n📋 分析总结:")
        buy_signals = [a for a in all_analysis if a['recommendation'] == 'BUY']
        sell_signals = [a for a in all_analysis if a['recommendation'] == 'SELL']
        
        if buy_signals:
            print(f"🟢 买入信号 ({len(buy_signals)}个):")
            for signal in buy_signals:
                print(f"   {signal['code']} @ {signal['current_price']:.2f}")
        
        if sell_signals:
            print(f"🔴 卖出信号 ({len(sell_signals)}个):")
            for signal in sell_signals:
                print(f"   {signal['code']} @ {signal['current_price']:.2f}")
        
        if not buy_signals and not sell_signals:
            print("📭 无强烈交易信号")
        
        # 关闭连接
        self.trd_ctx.close()
        self.quote_ctx.close()
        print(f"\n✅ 安全分析完成")

def main():
    """主函数"""
    analyzer = SafeTechnicalAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
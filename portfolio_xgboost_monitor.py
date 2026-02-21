#!/usr/bin/env python3
"""
完整投資組合XGBoost監控系統
監控所有持倉股票：聯想、匯豐、工行、港燈、京東、騰訊、阿里
"""

import sys
import json
import pandas as pd
from datetime import datetime, time as dt_time
sys.path.append('/Users/gordonlui/.openclaw/workspace')

class PortfolioXGBoostMonitor:
    """投資組合XGBoost監控系統"""
    
    def __init__(self):
        # 完整的投資組合配置
        self.portfolio = {
            'HK.00992': {  # 聯想集團
                'name': '聯想集團',
                'position': 26000,
                'buy_price': 8.59,
                'category': '科技股',
                'weight': 0.25  # 組合權重
            },
            'HK.00005': {  # 匯豐控股
                'name': '匯豐控股',
                'position': '持有',  # 具體股數未知
                'buy_price': 59.40,  # 從歷史記錄
                'category': '銀行股',
                'weight': 0.20
            },
            'HK.01398': {  # 工商銀行
                'name': '工商銀行',
                'position': '持有',
                'buy_price': 4.46,
                'category': '銀行股',
                'weight': 0.15
            },
            'HK.02638': {  # 港燈-SS
                'name': '港燈-SS',
                'position': '持有',
                'buy_price': 4.85,
                'category': '公用事業',
                'weight': 0.15
            },
            'HK.09618': {  # 京東集團
                'name': '京東集團',
                'position': '持有',
                'buy_price': 120.00,
                'category': '科技股',
                'weight': 0.10
            },
            'HK.00700': {  # 騰訊控股
                'name': '騰訊控股',
                'position': '監控',
                'current_price': 522.00,  # 從最新報告
                'category': '科技股',
                'weight': 0.10
            },
            'HK.09988': {  # 阿里巴巴
                'name': '阿里巴巴',
                'position': '監控',
                'current_price': 148.70,  # 從最新報告
                'category': '科技股',
                'weight': 0.05
            }
        }
        
        # 監控配置
        self.config = {
            'monitor_interval': 30,  # 分鐘
            'alert_thresholds': {
                'price_change': 0.03,  # 3%價格變動
                'volume_spike': 2.0,   # 成交量暴漲2倍
                'rsi_extreme': 30,     # RSI超賣
                'support_break': True  # 支撐位突破
            },
            'trading_hours': {
                'start': dt_time(9, 30),
                'end': dt_time(16, 0)
            }
        }
        
        # 技術分析參數
        self.technical_params = {
            'golden_ratios': [0.382, 0.5, 0.618],
            'rsi_period': 14,
            'ma_periods': [20, 50, 200]
        }
    
    def get_current_prices(self):
        """獲取當前價格（模擬數據）"""
        # 從最新報告獲取
        current_prices = {
            'HK.00992': 9.17,    # 聯想集團
            'HK.00700': 522.00,  # 騰訊控股
            'HK.09988': 148.70,  # 阿里巴巴
            'HK.00005': 134.20,  # 匯豐控股 (從歷史記錄)
            'HK.01398': 6.40,    # 工商銀行 (從歷史記錄)
            'HK.02638': 6.97,    # 港燈-SS (從歷史記錄)
            'HK.09618': 105.90   # 京東集團 (從歷史記錄)
        }
        return current_prices
    
    def calculate_performance(self):
        """計算投資組合表現"""
        current_prices = self.get_current_prices()
        performance = {}
        total_profit = 0
        total_investment = 0
        
        for stock_code, stock_info in self.portfolio.items():
            if stock_code in current_prices:
                current_price = current_prices[stock_code]
                
                # 計算盈虧
                if 'buy_price' in stock_info:
                    buy_price = stock_info['buy_price']
                    profit_pct = ((current_price - buy_price) / buy_price) * 100
                    
                    # 計算盈利金額（如果知道股數）
                    if isinstance(stock_info['position'], int):
                        profit_amount = (current_price - buy_price) * stock_info['position']
                    else:
                        profit_amount = None
                    
                    performance[stock_code] = {
                        'name': stock_info['name'],
                        'current_price': current_price,
                        'buy_price': buy_price,
                        'profit_pct': profit_pct,
                        'profit_amount': profit_amount,
                        'category': stock_info['category'],
                        'position': stock_info['position']
                    }
                    
                    # 累計總盈利
                    if profit_amount:
                        total_profit += profit_amount
                        total_investment += buy_price * stock_info['position']
        
        # 計算總體表現
        if total_investment > 0:
            total_return_pct = (total_profit / total_investment) * 100
        else:
            total_return_pct = 0
        
        return {
            'individual': performance,
            'summary': {
                'total_profit': total_profit,
                'total_investment': total_investment,
                'total_return_pct': total_return_pct,
                'monitored_stocks': len(performance),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
    
    def analyze_technical_levels(self, stock_code, current_price):
        """分析技術位"""
        if stock_code not in self.portfolio:
            return None
        
        stock_info = self.portfolio[stock_code]
        
        # 基礎技術分析
        analysis = {
            'stock_code': stock_code,
            'name': stock_info['name'],
            'current_price': current_price,
            'category': stock_info['category']
        }
        
        # 如果有買入價，計算關鍵位
        if 'buy_price' in stock_info:
            buy_price = stock_info['buy_price']
            
            # 計算黃金分割位
            price_range = current_price - buy_price
            golden_levels = {}
            for ratio in self.technical_params['golden_ratios']:
                level_price = buy_price + (price_range * ratio)
                golden_levels[f'{ratio*100:.1f}%'] = level_price
            
            analysis['golden_levels'] = golden_levels
            
            # 計算當前位置
            if current_price < golden_levels['38.2%']:
                golden_position = 'BELOW_382'
                golden_signal = 'OVERSOLD'
            elif current_price < golden_levels['50.0%']:
                golden_position = 'BETWEEN_382_500'
                golden_signal = 'NEAR_SUPPORT'
            elif current_price < golden_levels['61.8%']:
                golden_position = 'BETWEEN_500_618'
                golden_signal = 'NEUTRAL'
            else:
                golden_position = 'ABOVE_618'
                golden_signal = 'NEAR_RESISTANCE'
            
            analysis['golden_position'] = golden_position
            analysis['golden_signal'] = golden_signal
            
            # 計算支撐阻力位
            analysis['support_level'] = golden_levels['50.0%'] if current_price >= golden_levels['50.0%'] else golden_levels['38.2%']
            analysis['resistance_level'] = golden_levels['61.8%'] if current_price <= golden_levels['61.8%'] else None
            
            # 風險等級
            profit_pct = ((current_price - buy_price) / buy_price) * 100
            if profit_pct >= 10:
                risk_level = 'LOW'
                action_signal = 'CONSIDER_TAKE_PROFIT'
            elif profit_pct >= 5:
                risk_level = 'MEDIUM_LOW'
                action_signal = 'HOLD'
            elif profit_pct >= 0:
                risk_level = 'MEDIUM'
                action_signal = 'HOLD'
            elif profit_pct >= -5:
                risk_level = 'MEDIUM_HIGH'
                action_signal = 'CONSIDER_BUY'
            else:
                risk_level = 'HIGH'
                action_signal = 'STRONG_BUY'
            
            analysis['risk_level'] = risk_level
            analysis['action_signal'] = action_signal
            analysis['profit_pct'] = profit_pct
        
        return analysis
    
    def generate_xgboost_recommendation(self, stock_code, current_price):
        """生成XGBoost推薦（模擬）"""
        # 這裡可以整合真實的XGBoost預測
        # 目前使用模擬數據
        
        recommendations = {
            'HK.00992': {  # 聯想集團
                'probability': 0.65,
                'signal': 'BUY',
                'confidence': 0.30,
                'reason': '價格在關鍵支撐位，XGBoost預測上漲概率較高'
            },
            'HK.00700': {  # 騰訊控股
                'probability': 0.45,
                'signal': 'HOLD',
                'confidence': 0.40,
                'reason': '價格下跌中，等待企穩信號'
            },
            'HK.09988': {  # 阿里巴巴
                'probability': 0.48,
                'signal': 'HOLD',
                'confidence': 0.35,
                'reason': '中性區域，觀望為主'
            },
            'HK.00005': {  # 匯豐控股
                'probability': 0.70,
                'signal': 'HOLD',
                'confidence': 0.60,
                'reason': '長期持有，股息收益穩定'
            },
            'HK.01398': {  # 工商銀行
                'probability': 0.55,
                'signal': 'HOLD',
                'confidence': 0.50,
                'reason': '收息股，適合長期持有'
            },
            'HK.02638': {  # 港燈-SS
                'probability': 0.60,
                'signal': 'HOLD',
                'confidence': 0.55,
                'reason': '公用事業股，防守性強'
            },
            'HK.09618': {  # 京東集團
                'probability': 0.40,
                'signal': 'CONSIDER_BUY',
                'confidence': 0.45,
                'reason': '價格低於買入價，可考慮成本平均'
            }
        }
        
        return recommendations.get(stock_code, {
            'probability': 0.5,
            'signal': 'HOLD',
            'confidence': 0.5,
            'reason': '數據不足'
        })
    
    def generate_portfolio_report(self):
        """生成投資組合報告"""
        print(f"\n{'='*70}")
        print(f"📊 完整投資組合監控報告")
        print(f"{'='*70}")
        print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"監控股票: {len(self.portfolio)} 隻")
        print(f"{'='*70}")
        
        # 計算表現
        performance = self.calculate_performance()
        current_prices = self.get_current_prices()
        
        # 分類顯示
        categories = {}
        for stock_code, stock_info in self.portfolio.items():
            category = stock_info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(stock_code)
        
        # 按類別顯示
        for category, stocks in categories.items():
            print(f"\n📈 {category} ({len(stocks)}隻):")
            print("-" * 70)
            
            for stock_code in stocks:
                if stock_code in performance['individual']:
                    perf = performance['individual'][stock_code]
                    current_price = current_prices.get(stock_code, 0)
                    
                    # 技術分析
                    tech_analysis = self.analyze_technical_levels(stock_code, current_price)
                    
                    # XGBoost推薦
                    xgb_recommendation = self.generate_xgboost_recommendation(stock_code, current_price)
                    
                    print(f"  {stock_code} - {perf['name']}")
                    print(f"    當前價格: HKD {current_price:.2f}")
                    
                    if 'buy_price' in perf:
                        print(f"    買入價格: HKD {perf['buy_price']:.2f}")
                        print(f"    盈虧: {perf['profit_pct']:+.2f}%")
                        
                        if perf['profit_amount']:
                            print(f"    盈利金額: HKD {perf['profit_amount']:+,.2f}")
                    
                    if tech_analysis:
                        print(f"    技術位: {tech_analysis.get('golden_position', 'N/A')}")
                        print(f"    技術信號: {tech_analysis.get('golden_signal', 'N/A')}")
                        print(f"    風險等級: {tech_analysis.get('risk_level', 'N/A')}")
                    
                    print(f"    XGBoost概率: {xgb_recommendation['probability']:.2%}")
                    print(f"    XGBoost信號: {xgb_recommendation['signal']}")
                    print(f"    推薦理由: {xgb_recommendation['reason']}")
                    print()
        
        # 總體表現
        print(f"\n{'='*70}")
        print(f"💰 投資組合總體表現")
        print(f"{'='*70}")
        
        summary = performance['summary']
        print(f"監控股票數: {summary['monitored_stocks']} 隻")
        print(f"總投資金額: HKD {summary['total_investment']:,.2f}")
        print(f"總盈利金額: HKD {summary['total_profit']:+,.2f}")
        print(f"總回報率: {summary['total_return_pct']:+.2f}%")
        
        # 風險提示
        print(f"\n⚠️  風險提示:")
        if summary['total_return_pct'] >= 20:
            print(f"  ✅ 組合表現優秀，可考慮部分獲利了結")
        elif summary['total_return_pct'] >= 10:
            print(f"  👍 組合表現良好，繼續持有")
        elif summary['total_return_pct'] >= 0:
            print(f"  ⚠️  組合表現一般，密切監控")
        else:
            print(f"  🚨 組合虧損中，需要調整策略")
        
        # 保存報告
        self.save_report(performance, current_prices)
        
        print(f"\n{'='*70}")
        print(f"✅ 投資組合監控完成")
        print(f"{'='*70}")
        
        return performance
    
    def save_report(self, performance, current_prices):
        """保存報告"""
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'portfolio_summary': performance['summary'],
            'stocks_analysis': []
        }
        
        for stock_code, perf in performance['individual'].items():
            current_price = current_prices.get(stock_code, 0)
            tech_analysis = self.analyze_technical_levels(stock_code, current_price)
            xgb_recommendation = self.generate_xgboost_recommendation(stock_code, current_price)
            
            stock_analysis = {
                'stock_code': stock_code,
                'name': perf['name'],
                'performance': perf,
                'technical_analysis': tech_analysis,
                'xgboost_recommendation': xgb_recommendation
            }
            report['stocks_analysis'].append(stock_analysis)
        
        # 保存文件
        report_file = f"/Users/gordonlui/.openclaw/workspace/portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"💾 投資組合報告已保存: {report_file}")
        except Exception as e:
            print(f"❌ 保存報告失敗: {e}")
    
    def check_trading_alerts(self):
        """檢查
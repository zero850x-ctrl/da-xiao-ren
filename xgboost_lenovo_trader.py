#!/usr/bin/env python3
"""
聯想集團XGBoost專用交易系統
專注於00992的智能交易
"""

import sys
import time
import json
import pandas as pd
import numpy as np
from datetime import datetime, time as dt_time, timedelta
from futu import *

# 導入XGBoost預測系統
sys.path.append('/Users/gordonlui/.openclaw/workspace')
try:
    from validated_xgboost_predictor import ValidatedXGBoostPredictor
    XGBOOST_AVAILABLE = True
except ImportError:
    print("⚠️  XGBoost預測系統不可用")
    XGBOOST_AVAILABLE = False

class LenovoXGBoostTrader:
    """聯想集團專用XGBoost交易系統"""
    
    def __init__(self):
        self.trd_ctx = None
        self.quote_ctx = None
        self.trading_hours = {
            'start': dt_time(9, 30),   # 港股開盤
            'end': dt_time(16, 0)      # 港股收盤
        }
        
        # 強制使用模擬環境
        self.trade_environment = TrdEnv.SIMULATE
        
        # 初始化XGBoost預測器
        self.xgb_predictor = None
        if XGBOOST_AVAILABLE:
            try:
                self.xgb_predictor = ValidatedXGBoostPredictor()
                print("✅ XGBoost預測系統初始化成功")
            except Exception as e:
                print(f"❌ XGBoost預測系統初始化失敗: {e}")
                self.xgb_predictor = None
        
        # 聯想集團專用配置
        self.config = {
            'stock_code': 'HK.00992',
            'buy_price': 8.59,  # 你的買入價
            'current_position': 26000,  # 你的持倉量
            'max_additional_position': 10000,  # 最大加倉量
            'stop_loss_pct': 0.02,  # 2%止損
            'take_profit_pct': 0.08,  # 8%止盈
            'xgboost_buy_threshold': 0.65,  # XGBoost買入閾值
            'xgboost_sell_threshold': 0.35,  # XGBoost賣出閾值
            'golden_ratio_levels': {  # 黃金分割位
                '382': 8.89,  # 38.2%
                '500': 9.17,  # 50.0%
                '618': 9.55   # 61.8%
            }
        }
        
        # 交易記錄
        self.trades_log = []
        
    def connect_to_futu(self):
        """連接富途API"""
        try:
            self.trd_ctx = OpenSecTradeContext(
                host='127.0.0.1', 
                port=11111,
                security_firm=SecurityFirm.FUTUSECURITIES,
                trd_env=self.trade_environment
            )
            
            self.quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
            
            print(f"✅ 成功連接富途API (環境: {self.trade_environment})")
            return True
            
        except Exception as e:
            print(f"❌ 連接富途API失敗: {e}")
            return False
    
    def get_current_price(self):
        """獲取聯想集團當前價格"""
        try:
            ret, data = self.quote_ctx.get_market_snapshot([self.config['stock_code']])
            if ret == RET_OK:
                last_price = data['last_price'].iloc[0]
                return float(last_price)
            else:
                print(f"❌ 獲取價格失敗: {data}")
                return None
        except Exception as e:
            print(f"❌ 獲取價格異常: {e}")
            return None
    
    def get_xgboost_prediction(self, price):
        """獲取XGBoost預測"""
        if not self.xgb_predictor:
            return {'probability': 0.5, 'signal': 'HOLD', 'confidence': 0.5}
        
        try:
            prediction = self.xgb_predictor.predict_stock(self.config['stock_code'], price)
            return prediction
        except Exception as e:
            print(f"❌ XGBoost預測失敗: {e}")
            return {'probability': 0.5, 'signal': 'HOLD', 'confidence': 0.5}
    
    def analyze_golden_ratio(self, price):
        """分析黃金分割位"""
        levels = self.config['golden_ratio_levels']
        
        # 計算距離每個關鍵位的距離
        distances = {}
        for level_name, level_price in levels.items():
            distance_pct = ((price - level_price) / level_price) * 100
            distances[level_name] = {
                'price': level_price,
                'distance_pct': distance_pct,
                'distance': price - level_price
            }
        
        # 判斷當前位置
        current_level = None
        if price < levels['382']:
            current_level = 'BELOW_382'
        elif price < levels['500']:
            current_level = 'BETWEEN_382_500'
        elif price < levels['618']:
            current_level = 'BETWEEN_500_618'
        else:
            current_level = 'ABOVE_618'
        
        return {
            'current_level': current_level,
            'distances': distances,
            'support_level': levels['500'] if price >= levels['500'] else levels['382'],
            'resistance_level': levels['618'] if price <= levels['618'] else None
        }
    
    def calculate_trading_signal(self, price, xgb_prediction, golden_analysis):
        """計算交易信號"""
        
        # 1. XGBoost信號
        xgb_prob = xgb_prediction.get('probability', 0.5)
        xgb_signal = xgb_prediction.get('signal', 'HOLD')
        
        # 2. 黃金分割位信號
        golden_signal = 'HOLD'
        current_level = golden_analysis['current_level']
        
        if current_level == 'BELOW_382':
            golden_signal = 'STRONG_BUY'  # 嚴重超賣
        elif current_level == 'BETWEEN_382_500':
            golden_signal = 'BUY'  # 接近支撐
        elif current_level == 'BETWEEN_500_618':
            golden_signal = 'HOLD'  # 中性區域
        elif current_level == 'ABOVE_618':
            golden_signal = 'SELL'  # 接近阻力
        
        # 3. 價格動量信號
        momentum_signal = 'HOLD'
        # 這裡可以添加更多動量指標
        
        # 4. 綜合決策
        signal_score = 0
        
        # XGBoost權重: 40%
        if xgb_signal == 'BUY':
            signal_score += 0.4 * xgb_prob
        elif xgb_signal == 'SELL':
            signal_score -= 0.4 * (1 - xgb_prob)
        
        # 黃金分割位權重: 30%
        if golden_signal == 'STRONG_BUY':
            signal_score += 0.3
        elif golden_signal == 'BUY':
            signal_score += 0.15
        elif golden_signal == 'SELL':
            signal_score -= 0.15
        
        # 價格動量權重: 30%
        # 暫時設為中性
        
        # 生成最終信號
        if signal_score >= 0.3:
            final_signal = 'BUY'
            strength = 'STRONG' if signal_score >= 0.5 else 'MODERATE'
        elif signal_score <= -0.3:
            final_signal = 'SELL'
            strength = 'STRONG' if signal_score <= -0.5 else 'MODERATE'
        else:
            final_signal = 'HOLD'
            strength = 'NEUTRAL'
        
        return {
            'final_signal': final_signal,
            'strength': strength,
            'signal_score': signal_score,
            'xgb_probability': xgb_prob,
            'xgb_signal': xgb_signal,
            'golden_signal': golden_signal,
            'current_level': current_level,
            'analysis': {
                'price': price,
                'buy_price': self.config['buy_price'],
                'profit_pct': ((price - self.config['buy_price']) / self.config['buy_price']) * 100,
                'golden_analysis': golden_analysis
            }
        }
    
    def execute_trade(self, signal, price):
        """執行交易"""
        action = signal['final_signal']
        strength = signal['strength']
        
        if action == 'HOLD':
            print("⏸️  建議持有，不執行交易")
            return False, None
        
        # 計算交易數量
        if action == 'BUY':
            # 加倉邏輯
            if strength == 'STRONG':
                quantity = min(5000, self.config['max_additional_position'])
            else:
                quantity = min(2000, self.config['max_additional_position'])
        else:  # SELL
            # 減倉邏輯
            current_position = self.config['current_position']
            if strength == 'STRONG':
                quantity = min(current_position * 0.5, 10000)  # 最多賣一半
            else:
                quantity = min(current_position * 0.2, 5000)   # 賣20%
        
        quantity = int(quantity)
        if quantity <= 0:
            print("⚠️  交易數量為0，跳過")
            return False, None
        
        try:
            order_type = OrderType.NORMAL
            trd_side = TrdSide.BUY if action == 'BUY' else TrdSide.SELL
            
            ret, data = self.trd_ctx.place_order(
                price=price,
                qty=quantity,
                code=self.config['stock_code'],
                trd_side=trd_side,
                order_type=order_type,
                remark=f"XGBoost黃金分割交易: {signal['strength']}"
            )
            
            if ret == RET_OK:
                order_id = data['order_id'].iloc[0]
                trade_record = {
                    'order_id': order_id,
                    'action': action,
                    'price': price,
                    'quantity': quantity,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'signal_strength': strength,
                    'signal_score': signal['signal_score'],
                    'xgb_probability': signal['xgb_probability']
                }
                self.trades_log.append(trade_record)
                
                # 更新持倉
                if action == 'BUY':
                    self.config['current_position'] += quantity
                else:
                    self.config['current_position'] -= quantity
                
                print(f"✅ 交易執行成功: {action} {quantity}股 @ {price}")
                print(f"   更新後持倉: {self.config['current_position']}股")
                return True, order_id
            else:
                print(f"❌ 交易執行失敗: {data}")
                return False, None
                
        except Exception as e:
            print(f"❌ 交易執行異常: {e}")
            return False, None
    
    def generate_report(self, price, signal):
        """生成交易報告"""
        profit_pct = ((price - self.config['buy_price']) / self.config['buy_price']) * 100
        profit_amount = (price - self.config['buy_price']) * self.config['current_position']
        
        report = f"""
📱 聯想集團 (00992) XGBoost交易報告
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💰 價格分析:
├── 當前價格: HKD {price:.2f}
├── 買入價格: HKD {self.config['buy_price']:.2f}
├── 當前盈虧: {profit_pct:+.2f}%
├── 盈利金額: HKD {profit_amount:+,.2f}
└── 當前持倉: {self.config['current_position']:,}股

🤖 XGBoost分析:
├── 上漲概率: {signal['xgb_probability']:.2%}
├── XGBoost信號: {signal['xgb_signal']}
└── 綜合信號分數: {signal['signal_score']:.3f}

📊 技術分析:
├── 黃金分割位: {signal['current_level']}
├── 支撐位: HKD {signal['analysis']['golden_analysis']['support_level']:.2f}
├── 阻力位: HKD {signal['analysis']['golden_analysis']['resistance_level']:.2f if signal['analysis']['golden_analysis']['resistance_level'] else 'N/A'}
└── 黃金分割信號: {signal['golden_signal']}

🎯 交易建議:
├── 最終信號: {signal['final_signal']}
├── 信號強度: {signal['strength']}
└── 建議動作: {'執行交易' if signal['final_signal'] != 'HOLD' else '繼續持有'}

📈 關鍵價位:
├── 38.2%: HKD {self.config['golden_ratio_levels']['382']:.2f}
├── 50.0%: HKD {self.config['golden_ratio_levels']['500']:.2f} ⚠️ 當前測試中
└── 61.8%: HKD {self.config['golden_ratio_levels']['618']:.2f}
"""
        
        # 保存報告
        report_file = f"/Users/gordonlui/.openclaw/workspace/lenovo_trading_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 交易報告已生成: {report_file}")
            
            # 打印報告
            print(report)
            
        except Exception as e:
            print(f"❌ 生成交易報告失敗: {e}")
    
    def run_trading_cycle(self):
        """運行交易周期"""
        print(f"\n{'='*60}")
        print(f"📱 聯想集團XGBoost交易系統 - 開始分析")
        print(f"{'='*60}")
        
        # 1. 檢查交易時間
        current_time = datetime.now().time()
        if not (self.trading_hours['start'] <= current_time <= self.trading_hours['end']):
            print("⏰ 非交易時間，跳過分析")
            return
        
        # 2. 連接API
        if not self.connect_to_futu():
            print("❌ API連接失敗，跳過分析")
            return
        
        # 3. 獲取當前價格
        price = self.get_current_price()
        if price is None:
            print("❌ 無法獲取價格，跳過分析")
            return
        
        print(f"💰 當前價格: HKD {price:.2f}")
        
        # 4. 獲取XGBoost預測
        xgb_prediction = self.get_xgboost_prediction(price)
        print(f"🤖 XGBoost預測: {xgb_prediction.get('probability', 0.5):.2%} 上漲概率")
        
        # 5. 分析黃金分割位
        golden_analysis = self.analyze_golden_ratio(price)
        print(f"📊 黃金分割位: {golden_analysis['current_level']}")
        
        # 6. 計算交易信號
        signal = self.calculate_trading_signal(price, xgb_prediction, golden_analysis)
        print(f"🎯 綜合信號: {signal['final_signal']} ({signal['strength']})")
        
        # 7. 生成報告
        self.generate_report(price, signal)
        
        # 8. 詢問是否執行交易
        if signal['final_signal'] != 'HOLD':
            print(f"\n{'='*60}")
            response = input(f"🚀 是否執行{signal['final_signal']}交易? (y/n): ")
            
            if response.lower() == 'y':
                success, order_id = self.execute_trade(signal, price)
                if success:
                    print(f"✅ 交易已執行，訂單ID: {order_id}")
            else:
                print("⏸️  用戶取消交易")
        
        # 9. 保存交易記錄
        self.save_trading_log(price, signal)
        
        print(f"\n{'='*60}")
        print(f"✅ 聯想集團XGBoost交易系統 - 分析完成")
        print(f"{'='*60}")
    
    def save_trading_log(self, price, signal):
        """保存交易記錄"""
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'price': price,
            'signal': signal,
            'trades': self.trades_log
        }
        
        log_file = f"/Users/gordonlui/.openclaw/workspace/lenovo_trading_log_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            # 讀取現有記錄
            existing_logs = []
            try:
                with open(log_file, 'r') as f:
                    existing_logs = json.load(f)
            except FileNotFoundError
#!/usr/bin/env python3
"""
富途XGBoost智能交易系統
結合機器學習預測與技術分析的融合交易系統
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
    print("⚠️  XGBoost預測系統不可用，將使用純技術分析")
    XGBOOST_AVAILABLE = False

# 導入技術分析庫
try:
    from technical_analysis import TechnicalAnalyzer, Pattern, Trend
    TA_AVAILABLE = True
except ImportError:
    print("⚠️  技術分析庫不可用")
    TA_AVAILABLE = False

class XGBoostFutuTrader:
    """XGBoost智能交易系統（只操作模擬環境）"""
    
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
        
        # 交易配置 - 融合策略
        self.config = {
            'max_position_size': 0.20,   # 單隻股票最大倉位比例 20%
            'stop_loss_pct': 0.02,       # 止損比例 2%
            'take_profit_pct': 0.08,     # 止盈比例 8%
            'max_risk_per_trade': 0.015, # 每注風險金額 = 總資金 × 1.5%
            'min_xgboost_confidence': 0.60,  # XGBoost最小信心閾值 60%
            'min_technical_score': 0.50,     # 技術分析最小分數 50%
            'combined_threshold': 0.70,      # 綜合信號閾值 70%
            'watchlist': [               # 監控列表
                "HK.00992",  # 聯想集團（重點監控）
                "HK.00700",  # 騰訊控股
                "HK.09988",  # 阿里巴巴
                "HK.02800",  # 盈富基金
                "HK.01299",  # 友邦保險
                "HK.02318",  # 中國平安
            ]
        }
        
        # 交易記錄
        self.trades_log = []
        self.performance_log = []
        
    def connect_to_futu(self):
        """連接富途API"""
        try:
            # 創建交易上下文（模擬環境）
            self.trd_ctx = OpenSecTradeContext(
                host='127.0.0.1', 
                port=11111,
                security_firm=SecurityFirm.FUTUSECURITIES,
                trd_env=self.trade_environment
            )
            
            # 創建行情上下文
            self.quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
            
            print(f"✅ 成功連接富途API (環境: {self.trade_environment})")
            return True
            
        except Exception as e:
            print(f"❌ 連接富途API失敗: {e}")
            return False
    
    def get_account_info(self):
        """獲取賬戶信息"""
        try:
            ret, data = self.trd_ctx.accinfo_query()
            if ret == RET_OK:
                print(f"✅ 賬戶信息: {data.to_string()}")
                return data
            else:
                print(f"❌ 獲取賬戶信息失敗: {data}")
                return None
        except Exception as e:
            print(f"❌ 獲取賬戶信息異常: {e}")
            return None
    
    def get_stock_price(self, stock_code):
        """獲取股票價格"""
        try:
            ret, data = self.quote_ctx.get_market_snapshot([stock_code])
            if ret == RET_OK:
                last_price = data['last_price'].iloc[0]
                return float(last_price)
            else:
                print(f"❌ 獲取{stock_code}價格失敗: {data}")
                return None
        except Exception as e:
            print(f"❌ 獲取{stock_code}價格異常: {e}")
            return None
    
    def get_technical_analysis_score(self, stock_code, price):
        """獲取技術分析評分"""
        if not TA_AVAILABLE:
            return 0.5  # 默認分數
        
        try:
            # 這裡可以調用技術分析庫
            # 簡化版本：基於價格變化和RSI等指標
            analyzer = TechnicalAnalyzer()
            score = analyzer.analyze_stock(stock_code, price)
            return min(max(score, 0), 1)  # 確保在0-1範圍內
        except Exception as e:
            print(f"❌ 技術分析失敗: {e}")
            return 0.5
    
    def get_xgboost_prediction(self, stock_code, price):
        """獲取XGBoost預測"""
        if not self.xgb_predictor:
            return {'probability': 0.5, 'signal': 'HOLD', 'confidence': 0.5}
        
        try:
            prediction = self.xgb_predictor.predict_stock(stock_code, price)
            return prediction
        except Exception as e:
            print(f"❌ XGBoost預測失敗: {e}")
            return {'probability': 0.5, 'signal': 'HOLD', 'confidence': 0.5}
    
    def calculate_combined_signal(self, stock_code, price):
        """計算綜合交易信號"""
        
        # 1. 獲取XGBoost預測
        xgb_result = self.get_xgboost_prediction(stock_code, price)
        xgb_prob = xgb_result.get('probability', 0.5)
        xgb_signal = xgb_result.get('signal', 'HOLD')
        xgb_confidence = xgb_result.get('confidence', 0.5)
        
        # 2. 獲取技術分析評分
        ta_score = self.get_technical_analysis_score(stock_code, price)
        
        # 3. 計算綜合分數
        # 權重分配：XGBoost 60%，技術分析 40%
        combined_score = (xgb_prob * 0.6) + (ta_score * 0.4)
        
        # 4. 生成交易信號
        signal = {
            'stock_code': stock_code,
            'price': price,
            'xgb_probability': xgb_prob,
            'xgb_signal': xgb_signal,
            'xgb_confidence': xgb_confidence,
            'technical_score': ta_score,
            'combined_score': combined_score,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 5. 決定交易動作
        if combined_score >= self.config['combined_threshold']:
            signal['action'] = 'BUY'
            signal['strength'] = 'STRONG' if combined_score >= 0.85 else 'MODERATE'
        elif combined_score <= 0.3:
            signal['action'] = 'SELL'
            signal['strength'] = 'STRONG' if combined_score <= 0.15 else 'MODERATE'
        else:
            signal['action'] = 'HOLD'
            signal['strength'] = 'NEUTRAL'
        
        return signal
    
    def execute_trade(self, stock_code, action, price, quantity, reason=""):
        """執行交易"""
        try:
            order_type = OrderType.NORMAL
            trd_side = TrdSide.BUY if action == 'BUY' else TrdSide.SELL
            
            ret, data = self.trd_ctx.place_order(
                price=price,
                qty=quantity,
                code=stock_code,
                trd_side=trd_side,
                order_type=order_type,
                remark=f"XGBoost交易: {reason}"
            )
            
            if ret == RET_OK:
                order_id = data['order_id'].iloc[0]
                trade_record = {
                    'order_id': order_id,
                    'stock_code': stock_code,
                    'action': action,
                    'price': price,
                    'quantity': quantity,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'reason': reason
                }
                self.trades_log.append(trade_record)
                print(f"✅ 交易執行成功: {stock_code} {action} {quantity}股 @ {price}")
                return True, order_id
            else:
                print(f"❌ 交易執行失敗: {data}")
                return False, None
                
        except Exception as e:
            print(f"❌ 交易執行異常: {e}")
            return False, None
    
    def calculate_position_size(self, account_value, signal_strength, risk_level=1):
        """計算倉位大小"""
        base_size = self.config['max_position_size']
        
        # 根據信號強度調整
        if signal_strength == 'STRONG':
            size_multiplier = 1.0
        elif signal_strength == 'MODERATE':
            size_multiplier = 0.7
        else:
            size_multiplier = 0.3
        
        # 根據風險等級調整
        risk_multiplier = 1.0 / risk_level
        
        position_size = account_value * base_size * size_multiplier * risk_multiplier
        return min(position_size, account_value * 0.25)  # 最大不超過25%
    
    def run_trading_cycle(self):
        """運行交易周期"""
        print(f"\n{'='*60}")
        print(f"🔄 XGBoost智能交易系統 - 交易周期開始")
        print(f"{'='*60}")
        
        # 1. 檢查交易時間
        current_time = datetime.now().time()
        if not (self.trading_hours['start'] <= current_time <= self.trading_hours['end']):
            print("⏰ 非交易時間，跳過交易周期")
            return
        
        # 2. 連接API
        if not self.connect_to_futu():
            print("❌ API連接失敗，跳過交易周期")
            return
        
        # 3. 獲取賬戶信息
        account_info = self.get_account_info()
        if account_info is None:
            print("❌ 無法獲取賬戶信息，跳過交易周期")
            return
        
        account_value = float(account_info['total_assets'].iloc[0])
        print(f"💰 賬戶總資產: HKD {account_value:,.2f}")
        
        # 4. 監控每隻股票
        signals_summary = []
        for stock_code in self.config['watchlist']:
            print(f"\n📊 分析 {stock_code}...")
            
            # 獲取當前價格
            price = self.get_stock_price(stock_code)
            if price is None:
                continue
            
            print(f"  當前價格: HKD {price:.2f}")
            
            # 計算綜合信號
            signal = self.calculate_combined_signal(stock_code, price)
            signals_summary.append(signal)
            
            print(f"  XGBoost概率: {signal['xgb_probability']:.2%}")
            print(f"  技術評分: {signal['technical_score']:.2%}")
            print(f"  綜合分數: {signal['combined_score']:.2%}")
            print(f"  建議動作: {signal['action']} ({signal['strength']})")
            
            # 檢查是否需要交易
            if signal['action'] in ['BUY', 'SELL']:
                # 計算倉位大小
                position_value = self.calculate_position_size(
                    account_value, 
                    signal['strength'],
                    risk_level=2 if signal['xgb_confidence'] < 0.6 else 1
                )
                
                # 計算股數
                quantity = int(position_value / price)
                if quantity <= 0:
                    print(f"  ⚠️  倉位太小，跳過交易")
                    continue
                
                # 執行交易
                reason = f"XGBoost概率:{signal['xgb_probability']:.2%}, 技術評分:{signal['technical_score']:.2%}"
                success, order_id = self.execute_trade(
                    stock_code, 
                    signal['action'], 
                    price, 
                    quantity, 
                    reason
                )
                
                if success:
                    print(f"  ✅ 交易已執行: {quantity}股")
        
        # 5. 保存交易記錄
        self.save_trading_log(signals_summary)
        
        # 6. 生成報告
        self.generate_report(signals_summary)
        
        print(f"\n{'='*60}")
        print(f"✅ XGBoost智能交易系統 - 交易周期完成")
        print(f"{'='*60}")
    
    def save_trading_log(self, signals):
        """保存交易記錄"""
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'signals': signals,
            'trades': self.trades_log[-10:]  # 最近10筆交易
        }
        
        self.performance_log.append(log_entry)
        
        # 保存到文件
        log_file = f"/Users/gordonlui/.openclaw/workspace/xgboost_trading_log_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(log_file, 'w') as f:
                json.dump(self.performance_log, f, indent=2, ensure_ascii=False)
            print(f"💾 交易記錄已保存: {log_file}")
        except Exception as e:
            print(f"❌ 保存交易記錄失敗: {e}")
    
    def generate_report(self, signals):
        """生成交易報告"""
        buy_signals = [s for s in signals if s['action'] == 'BUY']
        sell_signals = [s for s in signals if s['action'] == 'SELL']
        hold_signals = [s for s in signals if s['action'] == 'HOLD']
        
        report = f"""
📈 XGBoost智能交易系統報告
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 信號統計:
├── 買入信號: {len(buy_signals)} 個
├── 賣出信號: {len(sell_signals)} 個
└── 持有信號: {len(hold_signals)} 個

🎯 重點股票分析:
"""
        
        # 添加重點股票分析
        for signal in signals:
            if signal['stock_code'] == 'HK.00992':  # 聯想集團
                report += f"""
📱 聯想集團 (00992):
├── 當前價格: HKD {signal['price']:.2f}
├── XGBoost概率: {signal['xgb_probability']:.2%}
├── 技術評分: {signal['technical_score']:.2%}
├── 綜合分數: {signal['combined_score']:.2%}
└── 建議動作: {signal['action']} ({signal['strength']})
"""
        
        # 保存報告
        report_file = f"/Users/gordonlui/.openclaw/workspace/xgboost_trading_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 交易報告已生成: {report_file}")
            
            # 打印報告摘要
            print("\n" + "="*60)
            print("📋 交易報告摘要")
            print("="*60)
            print(report[:500] + "...")  # 打印前500字符
            
        except Exception as e:
            print(f"❌ 生成交易報告失敗: {e}")
    
    def close_connections(self):
        """關閉連接"""
        try:
            if self.trd_ctx:
                self.trd_ctx.close()
            if self.quote_ctx:
                self.quote_ctx.close()
            print("✅ 連接已關閉")
        except Exception as e:
            print(f"❌ 關閉連接失敗: {e}")

def main():
    """主函數"""
    print("🚀 啟動XGBoost智能交易系統...")
    
    # 創建交易器
    trader = XGBoostFutuTrader()
    
    try:
        # 運行交易周期
        trader.run_trading_cycle()
        
    except KeyboardInterrupt:
        print("\n
#!/usr/bin/env python3
"""
聯想集團(00992)明日開市預測 - XGBoost系統
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime, timedelta
import json
import os

print("=" * 70)
print("🎯 聯想集團(00992)明日開市預測系統")
print("=" * 70)

class LenovoPredictor:
    """聯想集團專用預測器"""
    
    def __init__(self, stock_code="00992"):
        self.stock_code = stock_code
        self.model = None
        self.last_prediction = None
        self.prediction_history = []
        
    def get_historical_data(self, days=365):
        """獲取歷史數據"""
        print(f"📊 獲取 {self.stock_code} 歷史數據 ({days}天)...")
        
        # 嘗試從富途API獲取真實數據
        real_data = self.try_get_real_data()
        if real_data is not None and len(real_data) > 100:
            print(f"✅ 成功獲取真實數據: {len(real_data)} 天")
            return real_data
        
        # 使用模擬數據（基於聯想實際股價特徵）
        print("📊 使用模擬數據（基於聯想股價特徵）...")
        return self.create_lenovo_simulation(days)
    
    def try_get_real_data(self):
        """嘗試獲取真實數據"""
        try:
            import futu as ft
            
            quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)  # 多取一些
            
            ret, data, page_req_key = quote_ctx.get_history_kline(
                code=f"HK.{self.stock_code}",
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                ktype=ft.KLType.K_DAY,
                max_count=1000
            )
            
            quote_ctx.close()
            
            if ret == ft.RET_OK and len(data) > 100:
                data.rename(columns={
                    'time_key': 'date',
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close',
                    'volume': 'volume'
                }, inplace=True)
                
                data['date'] = pd.to_datetime(data['date'])
                data.set_index('date', inplace=True)
                data = data[['open', 'high', 'low', 'close', 'volume']]
                
                return data
                
        except Exception as e:
            print(f"⚠️  富途API連接失敗: {e}")
        
        return None
    
    def create_lenovo_simulation(self, days=365):
        """創建聯想集團模擬數據"""
        print("🎯 創建聯想集團特徵模擬數據...")
        
        np.random.seed(42)
        
        # 聯想股價特徵：波動較大，有明顯趨勢
        time = np.arange(days)
        
        # 多階段趨勢（反映科技股特性）
        phases = [
            (0, 60, 0.0015, 0.035),   # 快速上升，高波動
            (60, 120, 0.0005, 0.025), # 震盪整理
            (120, 180, -0.001, 0.03), # 調整下跌
            (180, 240, 0.002, 0.04),  # 強勢反彈
            (240, 300, 0.0008, 0.028),# 緩慢上升
            (300, 365, 0.0012, 0.032) # 加速上漲
        ]
        
        returns = np.zeros(days)
        for start, end, trend, volatility in phases:
            phase_days = end - start
            phase_returns = trend + np.random.normal(0, volatility, phase_days)
            returns[start:end] = phase_returns
        
        # 加入科技股特有的衝擊
        tech_shocks = [50, 150, 250, 320]
        for day in tech_shocks:
            returns[day] += np.random.choice([-0.08, 0.12])  # 科技股大波動
        
        # 起始價格約8-9港幣（聯想典型價格）
        start_price = 8.5
        prices = start_price * np.exp(np.cumsum(returns))
        
        # 創建DataFrame
        dates = pd.date_range(end=datetime.now(), periods=days)
        data = pd.DataFrame({
            'date': dates,
            'open': prices * (1 + np.random.normal(0, 0.01, days)),
            'high': prices * (1 + np.abs(np.random.normal(0, 0.018, days))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.018, days))),
            'close': prices,
            'volume': np.random.lognormal(15, 0.6, days)  # 較高成交量
        })
        
        data.set_index('date', inplace=True)
        
        print(f"✅ 模擬數據創建完成")
        print(f"   價格範圍: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
        print(f"   最終價格: ${data['close'].iloc[-1]:.2f}")
        
        return data
    
    def calculate_features(self, data):
        """計算特徵（專為聯想優化）"""
        print("🔧 計算聯想專用特徵...")
        
        # 1. 費波那契移動平均線（科技股適用）
        fib_periods = [5, 8, 13, 21, 34]  # 更短的周期適合科技股
        for period in fib_periods:
            if period < len(data):
                data[f'MA{period}'] = data['close'].rolling(period).mean()
        
        # 2. 黃金分割位（聯想常用技術位）
        lookback = 34  # 較短的回看期，科技股變化快
        data['high_34'] = data['high'].rolling(lookback).max()
        data['low_34'] = data['low'].rolling(lookback).min()
        data['price_range_34'] = data['high_34'] - data['low_34']
        
        # 特別關注0.618和0.382（科技股常用）
        data['golden_382'] = data['low_34'] + data['price_range_34'] * 0.382
        data['golden_618'] = data['low_34'] + data['price_range_34'] * 0.618
        
        # 3. 技術指標（科技股適用）
        # RSI（相對強弱指數）
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(10).mean()  # 較短周期
        loss = (-delta.where(delta < 0, 0)).rolling(10).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # 價格動量（科技股動量重要）
        for period in [1, 2, 3, 5, 10]:  # 短期動量
            data[f'return_{period}d'] = data['close'].pct_change(period)
        
        # 成交量分析（科技股成交量重要）
        data['volume_ma_10'] = data['volume'].rolling(10).mean()
        data['volume_ratio'] = data['volume'] / data['volume_ma_10']
        data['volume_spike'] = (data['volume_ratio'] > 2.5).astype(int)  # 科技股常有量能爆發
        
        # 4. 價格模式
        data['higher_high'] = (data['high'] > data['high'].shift(1)).astype(int)
        data['higher_low'] = (data['low'] > data['low'].shift(1)).astype(int)
        data['breakout'] = (data['close'] > data['high'].rolling(20).max()).astype(int)
        
        # 5. 波動率（科技股波動大）
        data['volatility_10'] = data['close'].pct_change().rolling(10).std()
        
        return data
    
    def prepare_training_data(self, data):
        """準備訓練數據"""
        print("📚 準備訓練數據...")
        
        # 計算所有特徵
        data = self.calculate_features(data)
        
        # 選擇特徵（專為科技股/聯想優化）
        feature_cols = [
            'open', 'high', 'low', 'close', 'volume',
            'MA5', 'MA8', 'MA13', 'MA21',
            'golden_382', 'golden_618',
            'RSI',
            'return_1d', 'return_2d', 'return_5d',
            'volume_ratio', 'volume_spike',
            'higher_high', 'higher_low', 'breakout',
            'volatility_10'
        ]
        
        # 只保留存在的特徵
        available_features = [col for col in feature_cols if col in data.columns]
        features = data[available_features].copy()
        
        # 處理缺失值
        features = features.fillna(method='ffill').fillna(0)
        
        # 創建標籤（預測明天漲跌）
        future_return = data['close'].shift(-1) / data['close'] - 1
        labels = (future_return > 0).astype(int)
        
        # 對齊數據
        aligned_idx = ~(features.isna().any(axis=1) | labels.isna())
        features = features[aligned_idx]
        labels = labels[aligned_idx]
        
        print(f"✅ 數據準備完成")
        print(f"   特徵數量: {len(available_features)}")
        print(f"   樣本數量: {len(features)}")
        print(f"   上漲比例: {labels.mean()*100:.1f}%")
        
        return features, labels, available_features
    
    def train_model(self, features, labels):
        """訓練XGBoost模型（聯想專用參數）"""
        print("🤖 訓練聯想專用XGBoost模型...")
        
        # 分割數據（時間序列）
        split_idx = int(len(features) * 0.8)
        X_train = features.iloc[:split_idx]
        X_test = features.iloc[split_idx:]
        y_train = labels.iloc[:split_idx]
        y_test = labels.iloc[split_idx:]
        
        print(f"   訓練集: {len(X_train)} 樣本")
        print(f"   測試集: {len(X_test)} 樣本")
        
        # XGBoost參數（優化用於科技股）
        params = {
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'max_depth': 3,  # 較淺，防止過擬合
            'learning_rate': 0.05,
            'n_estimators': 150,
            'subsample': 0.7,
            'colsample_bytree': 0.7,
            'gamma': 0.2,  # 較強正則化
            'reg_alpha': 0.2,
            'reg_lambda': 1.5,
            'random_state': 42,
            'n_jobs': -1,
            'use_label_encoder': False
        }
        
        # 訓練模型
        self.model = xgb.XGBClassifier(**params)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # 評估
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ 模型訓練完成")
        print(f"   測試集準確率: {accuracy:.3f}")
        
        # 特徵重要性
        importance = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        print(f"\n🏆 最重要的特徵:")
        print("-" * 40)
        for i, (_, row) in enumerate(feature_importance.head(8).iterrows(), 1):
            print(f"  {i:2d}. {row['feature']:20s} {row['importance']:.4f}")
        
        return accuracy, feature_importance
    
    def predict_tomorrow(self, data):
        """預測明日走勢"""
        print(f"\n🔮 預測 {self.stock_code} 明日開市走勢...")
        
        if self.model is None:
            print("❌ 請先訓練模型")
            return None
        
        # 準備最新數據的特徵
        features, _, feature_names = self.prepare_training_data(data)
        
        if len(features) == 0:
            print("❌ 特徵數據不足")
            return None
        
        # 使用最新數據
        latest_features = features.iloc[[-1]]
        
        # 預測
        probability = self.model.predict_proba(latest_features)[0, 1]
        current_price = data['close'].iloc[-1]
        
        # 生成信號（科技股適用閾值）
        if probability > 0.68:
            signal = "🟢 強力買入"
            action = "BUY"
            confidence_level = "極高"
        elif probability > 0.58:
            signal = "🟡 買入"
            action = "BUY"
            confidence_level = "高"
        elif probability < 0.32:
            signal = "🔴 強力賣出"
            action = "SELL"
            confidence_level = "極高"
        elif probability < 0.42:
            signal = "🟠 賣出"
            action = "SELL"
            confidence_level = "高"
        else:
            signal = "⚪ 持有"
            action = "HOLD"
            confidence_level = "中"
        
        confidence = probability if probability > 0.5 else 1 - probability
        
        # 技術分析
        tech_analysis = self.technical_analysis(data)
        
        prediction = {
            'stock': self.stock_code,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'prediction_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'current_price': float(current_price),
            'probability_up': float(probability),
            'signal': signal,
            'action': action,
            'confidence': float(confidence),
            'confidence_level': confidence_level,
            'technical_analysis': tech_analysis,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.last_prediction = prediction
        self.prediction_history.append(prediction)
        
        return prediction
    
    def technical_analysis(self, data):
        """技術分析"""
        analysis = {}
        
        # 黃金分割位分析
        if 'golden_618' in data.columns:
            current_price = data['close'].iloc[-1]
            golden_618 = data['golden_618'].iloc[-1]
            golden_382 = data['golden_382'].iloc[-1] if 'golden_382' in data.columns else None
            
            distance_618 = (current_price - golden_618) / golden_618 * 100
            
            analysis['golden_618'] = float(golden_618)
            analysis['distance_to_618'] = float(distance_618)
            
            if golden_382:
                analysis['golden_382'] = float(golden_382)
                distance_382 = (current_price - golden_382) / golden_382 * 100
                analysis['distance_to_382'] = float(distance_382)
            
            # 位置判斷
            if abs(distance_618) < 1.5:
                analysis['golden_position'] = "在0.618黃金分割位附近"
                analysis['golden_signal'] = "可能反轉"
            elif distance_618 > 0:
                analysis['golden_position'] = "在0.618之上"
                analysis['golden_signal'] = "強勢"
            else:
                analysis['golden_position'] = "在0.618之下"
                analysis['golden_signal'] = "弱勢"
        
        # 移動平均線分析
        ma_analysis = {}
        for period in [5, 8, 13, 21]:
            ma_col = f'MA{period}'
            if ma_col in data.columns:
                ma_value = data[ma_col].iloc[-1]
                current_price = data['close'].iloc[-1]
                distance_pct = (current_price - ma_value) / ma_value * 100
                
                ma_analysis[ma_col] = {
                    'value': float(ma_value),
                    'distance': float(distance_pct),
                    'position': "之上" if distance_pct > 0 else "之下"
                }
        
        analysis['moving_averages'] = ma_analysis
        
        # RSI分析
        if 'RSI' in data.columns:
            rsi = data['RSI'].iloc[-1]
            analysis['RSI'] = float(rsi)
            
            if rsi > 70:
                analysis['RSI_signal'] = "超買"
                analysis['RSI_warning'] = "可能回調"
            elif rsi < 30:
                analysis['RSI_signal'] = "超賣"
                analysis['RSI_warning'] = "可能反彈"
            else:
                analysis['RSI_signal'] = "中性"
        
        # 成交量分析
        if 'volume_ratio' in data.columns:
            volume_ratio = data['volume_ratio'].iloc[-1]
            analysis['volume_ratio'] = float(volume_ratio)
            
            if volume_ratio > 2:
                analysis['volume_signal'] = "放量"
            elif volume_ratio < 0.5:
                analysis['volume_signal'] = "縮量"
            else:
                analysis['volume_signal'] = "正常"
        
        return analysis
    
    def generate_trading_plan(self, prediction):
        """生成交易計劃"""
        print("\n💰 生成明日交易計劃...")
        
        if prediction is None:
            return None
        
        trading_plan = {
            'stock': prediction['stock'],
            'date': prediction['prediction_date'],
            'recommended_action': prediction['action'],
            'signal_strength': prediction['confidence_level'],
            'current_price': prediction['current_price'],
            'probability': prediction['probability_up'],
            'risk_assessment': self.assess_risk(prediction),
            'entry_strategy': {},
            'exit_strategy': {},
            'position_sizing': {},
            'contingency_plan': []
        }
        
        # 根據信號生成具體策略
        if prediction['action'] == "BUY":
            trading_plan['entry_strategy'] = {
                'type': '限價單',
                'price_range': f"{prediction['current_price'] * 0.99:.2f} - {prediction['current_price'] * 1.01:.2f}",
                'timing': '開市後30分鐘內',
                'condition': '價格在黃金分割位之上'
            }
            
            trading_plan['exit_strategy'] = {
                'stop_loss': prediction['current_price'] * 0.95,
                'take_profit': prediction['current_price'] * 1.08,
                'trailing_stop': prediction['current_price'] * 0.97
            }
            
            trading_plan['position_sizing'] = {
                'max_position': '30%',
                'initial_position': '15%',
                'add_on_dip': '價格回調2%加倉5%'
            }
            
        elif prediction['action'] == "SELL":
            trading_plan['entry_strategy'] = {
                'type': '市價單',
                'timing': '開市立即',
                'condition': 'RSI超買或跌破關鍵支撐'
            }
            
            trading_plan['exit_strategy'] = {
                'cover_price': prediction['current_price'] * 0.96,
                'stop_loss': prediction['current_price'] * 1.03
            }
            
            trading_plan['position_sizing'] = {
                'max_position': '20%',
                'initial_position': '10%'
            }
        
        else:  # HOLD
            trading_plan['entry_strategy'] = {'type': '不操作'}
            trading_plan['exit_strategy'] = {'type': '保持觀望'}
            trading_plan['position_sizing'] = {'action': '保持現有倉位'}
        
        # 應急計劃
        trading_plan['contingency_plan'] = [
            "如開市跳空超過3%，暫停交易",
            "如成交量異常放大，謹慎操作",
            "設置嚴格的止損位",
            "分批建倉，控制風險"
        ]
        
        return trading_plan
    
    def assess_risk(self, prediction):
        """風險評估"""
        risk_score = 0
        risk_factors = []
        
        # 基於信心程度
        if prediction['confidence'] < 0.6:
            risk_score += 2
            risk_factors.append("信心程度一般")
        
        # 基於技術分析
        tech = prediction.get('technical_analysis', {})
        
        if tech.get('RSI_signal') == "超買":
            risk_score += 1
            risk_factors.append("RSI超買")
        
        if tech.get('volume_ratio', 1) > 2.5:
            risk_score += 1
            risk_factors.append("成交量異常")
        
        # 風險等級
        if risk_score >= 3:
            risk_level = "高"
        elif risk_score >= 2:
            risk_level = "中高"
        elif risk_score >= 1:
            risk_level = "中"
        else:
            risk_level = "低"
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors
        }
    
    def save_prediction(self, prediction, trading_plan):
        """保存預測和交易計劃"""
        print("\n💾 保存預測結果...")
        
        # 創建結果目錄
        results_dir = '/Users/gordonlui/.openclaw/workspace/992_predictions'
        os.makedirs(results_dir, exist_ok=True)
        
        # 保存預測
        prediction_file = f"{results_dir}/prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(prediction_file, 'w') as f:
            json.dump(prediction, f, indent=2, ensure_ascii=False)
        
        # 保存交易計劃
        if trading_plan:
            plan_file = f"{results_dir}/trading_plan_{datetime.now().strftime('%Y%m%d')}.json"
            with open(plan_file, 'w') as f:
                json.dump(trading_plan, f, indent=2, ensure_ascii=False)
        
        # 保存到歷史記錄
        history_file = f"{results_dir}/prediction_history.json"
        history_data = []
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history_data = json.load(f)
        
        history_data.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'prediction': prediction,
            'trading_plan': trading_plan
        })
        
        with open(history_file, 'w') as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 結果已保存:")
        print(f"   預測文件: {prediction_file}")
        if trading_plan:
            print(f"   交易計劃: {plan_file}")
        print(f"   歷史記錄: {history_file}")
        
        return prediction_file
    
    def create_execution_script(self, trading_plan):
        """創建執行腳本"""
        print("\n⚡ 創建明日執行腳本...")
        
        if trading_plan is None or trading_plan['recommended_action'] == "HOLD":
            print("  無需創建執行腳本（持有信號）")
            return None
        
        script_content = f"""#!/usr/bin/env python3
"""
        
        if trading_plan['recommended_action'] == "BUY":
            script_content += f"""
# 聯想集團(00992)買入執行腳本
# 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 執行時間: 明日開市 (09:30)

import futu as ft
import time
from datetime import datetime

def execute_buy_order():
    \"\"\"執行買入訂單\"\"\"
    print("🚀 執行聯想集團(00992)買入訂單...")
    
    try:
        # 連接富途API
        trade_ctx = ft.OpenSecTradeContext(
            host='127.0.0.1', 
            port=11111
        )
        
        # 帳戶信息（模擬帳戶）
        account_info = {{
            'account_id': '20889483',  # 你的模擬帳戶
            'password': 'Ad!tA7e3',
            'server': 'MingTakInternational-Server'
        }}
        
        # 登錄
        ret, data = trade_ctx.unlock_trade(
            password=account_info['password']
        )
        
        if ret == ft.RET_OK:
            print("✅ 交易帳戶登錄成功")
            
            # 買入參數
            stock_code = "HK.00992"
            quantity = 1000  # 買入1000股
            price = {trading_plan['current_price'] * 1.005:.2f}  # 限價單，+0.5%
            
            # 下單
            ret, data = trade_ctx.place_order(
                price=price,
                qty=quantity,
                code=stock_code,
                trd_side=ft.TrdSide.BUY,
                order_type=ft.OrderType.NORMAL,
                trd_env=ft.TrdEnv.SIMULATE  # 模擬交易
            )
            
            if ret == ft.RET_OK:
                print(f"✅ 買入訂單提交成功")
                print(f"   股票: HK.00992")
                print(f"   數量: {quantity}股")
                print(f"   價格: ${price:.2f}")
                print(f"   訂單ID: {{data['order_id']}}")
            else:
                print(f"❌ 買入訂單失敗: {{data}}")
            
            # 登出
            trade_ctx.close()
            
        else:
            print(f"❌ 交易帳戶登錄失敗: {{data}}")
            
    except Exception as e:
        print(f"❌ 執行錯誤: {{e}}")

if __name__ == "__main__":
    # 等待開市時間
    print("⏰ 等待開市時間 (09:30)...")
    
    # 這裡可以添加時間等待邏輯
    # 實際使用時，可以設置定時任務
    
    execute_buy_order()
"""
        else:  # SELL
            script_content += f"""
# 聯想集團(00992)賣出執行腳本
# 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

import futu as ft

def execute_sell_order():
    \"\"\"執行賣出訂單\"\"\"
    print("🚀 執行聯想集團(00992)賣出訂單...")
    
    try:
        # 連接富途API
        trade_ctx = ft.OpenSecTradeContext(
            host='127.0.0.1', 
            port=11111
        )
        
        # 登錄
        ret, data = trade_ctx.unlock_trade(
            password='Ad!tA7e3'  # 你的密碼
        )
        
        if ret == ft.RET_OK:
            print("✅ 交易帳戶登錄成功")
            
            # 賣出參數
            stock_code = "HK.00992"
            quantity = 1000  # 賣出1000股
            
            # 下單（市價單）
            ret, data = trade_ctx.place_order(
                price=0,  # 市價單
                qty=quantity,
                code=stock_code,
                trd_side=ft.TrdSide.SELL,
                order_type=ft.OrderType.MARKET,
                trd_env=ft.TrdEnv.SIMULATE  # 模擬交易
            )
            
            if ret == ft.RET_OK:
                print(f"✅ 賣出訂單提交成功")
                print(f"   股票: HK.00992")
                print(f"   數量: {quantity}股")
                print(f"   訂單ID: {{data['order_id']}}")
            else:
                print(f"❌ 賣出訂單失敗: {{data}}")
            
            # 登出
            trade_ctx.close()
            
        else:
            print(f"❌ 交易帳戶登錄失敗: {{data}}")
            
    except Exception as e:
        print(f"❌ 執行錯誤: {{e}}")

if __name__ == "__main__":
    execute_sell_order()
"""
        
        # 保存腳本
        script_file = f"/Users/gordonlui/.openclaw/workspace/execute_992_{trading_plan['recommended_action'].lower()}.py"
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # 設置執行權限
        import stat
        os.chmod(script_file, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        
        print(f"✅ 執行腳本已創建: {script_file}")
        print(f"💡 使用方法: python3 {script_file}")
        
        return script_file

def main():
    """主函數"""
    print("🎯 聯想集團(00992)明日開市預測系統啟動")
    print("=" * 70)
    
    # 初始化預測器
    predictor = LenovoPredictor("00992")
    
    # 1. 獲取歷史數據
    data = predictor.get_historical_data(days=365)
    
    # 2. 準備訓練數據
    features, labels, feature_names = predictor.prepare_training_data(data)
    
    # 3. 訓練模型
    accuracy, feature_importance = predictor.train_model(features, labels)
    
    # 4. 預測明日走勢
    prediction = predictor.predict_tomorrow(data)
    
    if prediction:
        # 顯示預測結果
        print(f"\n{'='*70}")
        print(f"📈 預測結果總結")
        print(f"{'='*70}")
        
        print(f"股票: HK.{prediction['stock']}")
        print(f"當前價格: ${prediction['current_price']:.2f}")
        print(f"明日上漲概率: {prediction['probability_up']:.3f}")
        print(f"交易信號: {prediction['signal']}")
        print(f"信心程度: {prediction['confidence_level']} ({prediction['confidence']:.3f})")
        
        # 技術分析
        tech = prediction.get('technical_analysis', {})
        if tech:
            print(f"\n📊 技術分析:")
            if 'golden_618' in tech:
                print(f"   0.618黃金分割位: ${tech['golden_618']:.2f}")
                print(f"   當前距離: {tech.get('distance_to_618', 0):+.2f}%")
                print(f"   位置: {tech.get('golden_position', 'N/A')}")
            
            if 'RSI' in tech:
                print(f"   RSI: {tech['RSI']:.1f} ({tech.get('RSI_signal', 'N/A')})")
            
            if 'volume_ratio' in tech:
                print(f"   成交量比率: {tech['volume_ratio']:.2f}x")
        
        # 5. 生成交易計劃
        trading_plan = predictor.generate_trading_plan(prediction)
        
        if trading_plan:
            print(f"\n💰 交易計劃:")
            print(f"   推薦操作: {trading_plan['recommended_action']}")
            print(f"   信號強度: {trading_plan['signal_strength']}")
            print(f"   風險評估: {trading_plan['risk_assessment']['risk_level']}")
            
            if trading_plan['recommended_action'] == "BUY":
                print(f"   買入策略: {trading_plan['entry_strategy']['type']}")
                print(f"   價格區間: {trading_plan['entry_strategy']['price_range']}")
                print(f"   止損位: ${trading_plan['exit_strategy']['stop_loss']:.2f}")
                print(f"   止盈位: ${trading_plan['exit_strategy']['take_profit']:.2f}")
            
            elif trading_plan['recommended_action'] == "SELL":
                print(f"   賣出策略: {trading_plan['entry_strategy']['type']}")
                print(f"   時機: {trading_plan['entry_strategy']['timing']}")
        
        # 6. 保存結果
        prediction_file = predictor.save_prediction(prediction, trading_plan)
        
        # 7. 創建執行腳本
        if trading_plan and trading_plan['recommended_action'] != "HOLD":
            script_file = predictor.create_execution_script(trading_plan)
            
            print(f"\n⚡ 明日操作:")
            print(f"   1. 開市時間: 09:30")
            print(f"   2. 執行腳本: {script_file}")
            print(f"   3. 監控價格: 關注黃金分割位")
            print(f"   4. 風險控制: 嚴格執行止損")
        
        # 8. 設置定時任務（可選）
        print(f"\n⏰ 自動執行設置:")
        print(f"   手動執行: python3 {script_file if 'script_file' in locals() else 'N/A'}")
        print(f"   Cron任務: 09:31 執行預測腳本")
        print(f"   監控: 價格變動超過2%時重新評估")
        
        print(f"\n💡 重要提醒:")
        print(f"   1. 這是基於歷史數據的預測")
        print(f"   2. 實際市場可能不同")
        print(f"   3. 建議小資金測試")
        print(f"   4. 嚴格執行風險管理")
        
        print(f"\n✅ 熱身完成！系統已準備就緒")
        print(f"🎯 明日開市時間: 09:30")
        print(f"📊 監控股票: HK.00992")
        print(f"🤖 使用模型: XGBoost with 黃金分割")
        
        print(f"\n{'='*70}")
        print(f"🚀 準備明日開市操作！")
        print(f"{'='*70}")
        
        return {
            'predictor': predictor,
            'prediction': prediction,
            'trading_plan': trading_plan,
            'accuracy': accuracy
        }
    
    else:
        print("❌ 預測失敗")
        return None

if __name__ == "__main__":
    result = main()

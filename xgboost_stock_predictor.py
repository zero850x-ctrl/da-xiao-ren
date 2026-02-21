#!/usr/bin/env python3
"""
XGBoost股價預測系統
包含黃金分割和費波那契移動平均線
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime, timedelta
import talib
import matplotlib.pyplot as plt
import seaborn as sns

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS
plt.rcParams['axes.unicode_minus'] = False

class FibonacciStockPredictor:
    """費波那契XGBoost股價預測器"""
    
    def __init__(self, stock_code="00005"):
        self.stock_code = stock_code
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = None
        
        # 費波那契數列參數
        self.fibonacci_periods = [8, 13, 21, 34, 55]
        self.golden_ratios = [0.236, 0.382, 0.5, 0.618, 0.786]
        
    def fetch_stock_data(self, days=365):
        """獲取股票數據（模擬或從API）"""
        print(f"📊 獲取 {self.stock_code} 數據 ({days}天)...")
        
        # 這裡可以替換為富途API
        # 暫時使用模擬數據
        np.random.seed(42)
        
        dates = pd.date_range(end=datetime.now(), periods=days)
        
        # 生成模擬股價數據（帶趨勢和波動）
        base_price = 100
        trend = np.linspace(0, 0.2, days)  # 20%上升趨勢
        noise = np.random.normal(0, 0.02, days)  # 2%日波動
        
        prices = base_price * (1 + trend + np.cumsum(noise))
        
        # 創建DataFrame
        data = pd.DataFrame({
            'date': dates,
            'open': prices * (1 + np.random.normal(0, 0.01, days)),
            'high': prices * (1 + np.abs(np.random.normal(0, 0.015, days))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.015, days))),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, days)
        })
        
        data.set_index('date', inplace=True)
        print(f"✅ 獲取到 {len(data)} 天數據")
        return data
    
    def calculate_fibonacci_ma(self, data):
        """計算費波那契移動平均線"""
        print("📈 計算費波那契移動平均線...")
        
        for period in self.fibonacci_periods:
            if period <= len(data):
                data[f'MA{period}'] = data['close'].rolling(window=period).mean()
                print(f"  MA{period}: 已計算")
        
        # 計算MA交叉信號
        if 'MA8' in data.columns and 'MA13' in data.columns:
            data['MA8_13_cross'] = (data['MA8'] > data['MA13']).astype(int)
        
        if 'MA13' in data.columns and 'MA34' in data.columns:
            data['MA13_34_cross'] = (data['MA13'] > data['MA34']).astype(int)
        
        return data
    
    def calculate_golden_ratio_levels(self, data, lookback=55):
        """計算黃金分割位"""
        print("🎯 計算黃金分割位...")
        
        # 計算最近lookback天的最高最低
        data['high_55'] = data['high'].rolling(window=lookback).max()
        data['low_55'] = data['low'].rolling(window=lookback).min()
        
        # 計算價格範圍
        data['price_range'] = data['high_55'] - data['low_55']
        
        # 計算各黃金分割位
        for ratio in self.golden_ratios:
            level_name = f'golden_{int(ratio*1000)}'
            data[level_name] = data['low_55'] + data['price_range'] * ratio
            
            # 計算當前價格相對黃金分割位的位置
            data[f'position_{level_name}'] = (data['close'] - data[level_name]) / data['price_range']
            
            # 計算是否接近黃金分割位（±2%範圍內）
            data[f'near_{level_name}'] = ((abs(data['close'] - data[level_name]) / data['close']) < 0.02).astype(int)
        
        # 特別關注0.618黃金分割位
        if 'golden_618' in data.columns:
            data['at_golden_618'] = (abs(data['close'] - data['golden_618']) / data['close'] < 0.01).astype(int)
        
        return data
    
    def calculate_technical_indicators(self, data):
        """計算技術指標"""
        print("📊 計算技術指標...")
        
        # RSI
        data['RSI'] = talib.RSI(data['close'], timeperiod=14)
        data['RSI_signal'] = pd.cut(data['RSI'], 
                                    bins=[0, 30, 70, 100],
                                    labels=['oversold', 'neutral', 'overbought'])
        
        # MACD
        data['MACD'], data['MACD_signal'], data['MACD_hist'] = talib.MACD(
            data['close'], fastperiod=12, slowperiod=26, signalperiod=9
        )
        data['MACD_cross'] = (data['MACD'] > data['MACD_signal']).astype(int)
        
        # Bollinger Bands
        data['BB_upper'], data['BB_middle'], data['BB_lower'] = talib.BBANDS(
            data['close'], timeperiod=20, nbdevup=2, nbdevdn=2
        )
        data['BB_position'] = (data['close'] - data['BB_lower']) / (data['BB_upper'] - data['BB_lower'])
        
        # 成交量指標
        data['volume_ma'] = data['volume'].rolling(window=20).mean()
        data['volume_ratio'] = data['volume'] / data['volume_ma']
        data['volume_spike'] = (data['volume_ratio'] > 2).astype(int)
        
        # 價格動量
        for period in [1, 3, 5, 10, 20]:
            data[f'return_{period}d'] = data['close'].pct_change(period)
            data[f'volatility_{period}d'] = data['close'].pct_change().rolling(period).std()
        
        # 價格模式
        data['higher_high'] = (data['high'] > data['high'].shift(1)).astype(int)
        data['higher_low'] = (data['low'] > data['low'].shift(1)).astype(int)
        
        return data
    
    def create_features(self, data):
        """創建特徵數據集"""
        print("🔧 創建特徵數據集...")
        
        # 確保所有計算完成
        data = self.calculate_fibonacci_ma(data)
        data = self.calculate_golden_ratio_levels(data)
        data = self.calculate_technical_indicators(data)
        
        # 定義特徵列
        feature_columns = []
        
        # 價格特徵
        price_features = ['open', 'high', 'low', 'close', 'volume']
        feature_columns.extend(price_features)
        
        # 費波那契MA特徵
        for period in [8, 13, 34]:
            col = f'MA{period}'
            if col in data.columns:
                feature_columns.append(col)
                feature_columns.append(f'price_vs_{col}')  # 價格相對MA位置
                data[f'price_vs_{col}'] = data['close'] / data[col] - 1
        
        # MA交叉特徵
        if 'MA8_13_cross' in data.columns:
            feature_columns.append('MA8_13_cross')
        if 'MA13_34_cross' in data.columns:
            feature_columns.append('MA13_34_cross')
        
        # 黃金分割特徵
        for ratio in [382, 500, 618]:  # 0.382, 0.5, 0.618
            for suffix in ['', '_position', '_near']:
                col = f'golden_{ratio}{suffix}'
                if col in data.columns:
                    feature_columns.append(col)
        
        # 技術指標特徵
        tech_features = ['RSI', 'MACD', 'MACD_hist', 'BB_position', 
                        'volume_ratio', 'volume_spike']
        feature_columns.extend([f for f in tech_features if f in data.columns])
        
        # 動量特徵
        for period in [1, 5, 20]:
            feature_columns.append(f'return_{period}d')
            feature_columns.append(f'volatility_{period}d')
        
        # 模式特徵
        pattern_features = ['higher_high', 'higher_low']
        feature_columns.extend(pattern_features)
        
        # 創建特徵DataFrame
        features = data[feature_columns].copy()
        
        # 處理缺失值
        features = features.fillna(method='ffill').fillna(0)
        
        print(f"✅ 創建了 {len(feature_columns)} 個特徵")
        return features, feature_columns
    
    def create_labels(self, data, forward_days=1, threshold=0.005):
        """創建標籤（未來N天漲跌）"""
        print(f"🏷️ 創建標籤（未來{forward_days}天）...")
        
        # 計算未來N天的收益率
        future_return = data['close'].shift(-forward_days) / data['close'] - 1
        
        # 創建二元標籤：上漲=1，下跌=0
        labels = (future_return > threshold).astype(int)
        
        # 統計標籤分布
        print(f"  上漲樣本: {labels.sum()} ({labels.sum()/len(labels)*100:.1f}%)")
        print(f"  下跌樣本: {(len(labels)-labels.sum())} ({(len(labels)-labels.sum())/len(labels)*100:.1f}%)")
        
        return labels
    
    def prepare_training_data(self, data, test_size=0.2):
        """準備訓練數據"""
        print("📚 準備訓練數據...")
        
        # 創建特徵
        features, feature_names = self.create_features(data)
        
        # 創建標籤（預測未來1天漲跌）
        labels = self.create_labels(data, forward_days=1)
        
        # 對齊數據
        aligned_data = pd.concat([features, labels], axis=1).dropna()
        features = aligned_data.iloc[:, :-1]
        labels = aligned_data.iloc[:, -1]
        
        # 時間序列分割（避免未來信息洩漏）
        tscv = TimeSeriesSplit(n_splits=5)
        
        # 最後一次分割作為測試集
        train_idx, test_idx = list(tscv.split(features))[-1]
        
        X_train = features.iloc[train_idx]
        y_train = labels.iloc[train_idx]
        X_test = features.iloc[test_idx]
        y_test = labels.iloc[test_idx]
        
        # 標準化特徵
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"✅ 數據準備完成")
        print(f"  訓練集: {len(X_train)} 樣本")
        print(f"  測試集: {len(X_test)} 樣本")
        
        return (X_train_scaled, X_test_scaled, 
                y_train, y_test, feature_names)
    
    def train_model(self, X_train, y_train, X_test, y_test):
        """訓練XGBoost模型"""
        print("🤖 訓練XGBoost模型...")
        
        # XGBoost參數（優化用於股價預測）
        params = {
            'objective': 'binary:logistic',
            'eval_metric': ['logloss', 'error', 'auc'],
            'max_depth': 6,  # 控制模型複雜度
            'learning_rate': 0.05,  # 較小學習率
            'n_estimators': 200,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'gamma': 0.1,  # 正則化參數
            'reg_alpha': 0.1,  # L1正則化
            'reg_lambda': 1.0,  # L2正則化
            'random_state': 42,
            'n_jobs': -1
        }
        
        # 創建DMatrix（XGBoost專用數據格式）
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dtest = xgb.DMatrix(X_test, label=y_test)
        
        # 訓練模型
        self.model = xgb.train(
            params,
            dtrain,
            num_boost_round=params['n_estimators'],
            evals=[(dtrain, 'train'), (dtest, 'test')],
            early_stopping_rounds=20,
            verbose_eval=False
        )
        
        # 預測
        y_pred_proba = self.model.predict(dtest)
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        # 評估模型
        self.evaluate_model(y_test, y_pred, y_pred_proba)
        
        # 獲取特徵重要性
        self.get_feature_importance(X_train.columns if hasattr(X_train, 'columns') else None)
        
        return self.model
    
    def evaluate_model(self, y_true, y_pred, y_pred_proba):
        """評估模型性能"""
        print("📊 模型性能評估:")
        print("-" * 40)
        
        # 基本指標
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        print(f"準確率 (Accuracy): {accuracy:.3f}")
        print(f"精確率 (Precision): {precision:.3f}")
        print(f"召回率 (Recall): {recall:.3f}")
        print(f"F1分數: {f1:.3f}")
        
        # 交易相關指標
        self.calculate_trading_metrics(y_true, y_pred, y_pred_proba)
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    def calculate_trading_metrics(self, y_true, y_pred, y_pred_proba):
        """計算交易相關指標"""
        print("\n💰 交易指標評估:")
        print("-" * 40)
        
        # 假設每次交易固定金額
        # 簡單策略：預測上漲就買入，持有1天
        
        # 計算勝率
        correct_predictions = (y_pred == y_true)
        win_rate = correct_predictions.mean()
        
        # 計算盈虧比（簡單版本）
        # 這裡需要實際價格數據來計算真實盈虧
        
        print(f"預測勝率: {win_rate:.3f}")
        print(f"信號數量: {len(y_pred)}")
        print(f"買入信號: {y_pred.sum()} ({y_pred.sum()/len(y_pred)*100:.1f}%)")
        
        # 置信度分析
        confidence_thresholds = [0.6, 0.7, 0.8]
        for threshold in confidence_thresholds:
            high_conf_idx = y_pred_proba > threshold
            if high_conf_idx.any():
                high_conf_accuracy = accuracy_score(
                    y_true[high_conf_idx], 
                    y_pred[high_conf_idx]
                )
                print(f"信心>{threshold}的準確率: {high_conf_accuracy:.3f} "
                      f"({high_conf_idx.sum()}個信號)")
    
    def get_feature_importance(self, feature_names=None):
        """獲取特徵重要性"""
        if self.model is None:
            print("❌ 模型未訓練")
            return
        
        # 獲取特徵重要性
        importance = self.model.get_score(importance_type='weight')
        
        if feature_names is not None:
            # 轉換為DataFrame
            importance_df = pd.DataFrame({
                'feature': list(importance.keys()),
                'importance': list(importance.values())
            })
            
            # 排序
            importance_df = importance_df.sort_values('importance', ascending=False)
            
            print(f"\n🏆 特徵重要性排名 (前10):")
            print("-" * 50)
            
            for i, (_, row) in enumerate(importance_df.head(10).iterrows(), 1):
                print(f"{i:2d}. {row['feature']:30s} {row['importance']:6.0f}")
            
            self.feature_importance = importance_df
            
            # 可視化
            self.plot_feature_importance(importance_df.head(15))
        
        return importance_df
    
    def plot_feature_importance(self, importance_df):
        """可視化特徵重要性"""
        plt.figure(figsize=(12, 8))
        
        # 創建水平條形圖
        bars = plt.barh(range(len(importance_df)), 
                       importance_df['importance'].values,
                       color='steelblue')
        
        plt.yticks(range(len(importance_df)), importance_df['feature'].values)
        plt.xlabel('特徵重要性')
        plt.title(f'{self.stock_code} - XGBoost特徵重要性')
        plt.gca().invert_yaxis()  # 最重要的在頂部
        
        # 添加數值標籤
        for i, (bar, importance) in enumerate(zip(bars, importance_df['importance'].values)):
            plt.text(importance + 1, i, f'{importance:.0f}', 
                    va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(f'/Users/gordonlui/.openclaw/workspace/feature_importance_{self.stock_code}.png', dpi=150)
        print(f"📊 特徵重要性圖已保存")
    
    def predict_next_day(self, latest_data):
        """預測下一天走勢"""
        if self.model is None:
            print("❌ 請先訓練模型")
            return None
        
        print(f"\n🔮 預測 {self.stock_code} 下一天走勢...")
        
        # 準備特徵
        features, _ = self.create_features(latest_data)
        
        # 使用最新數據
        latest_features = features.iloc[[-1]].copy()
        
        # 標準化
        latest_scaled = self.scaler.transform(latest_features)
        
        # 創建DMatrix
        dpred = xgb.DMatrix(latest_scaled)
        
        # 預測
        probability = self.model.predict(dpred)[0]
        
        # 生成信號
        signal = "買入" if probability > 0.6 else "賣出" if probability < 0.4 else "持有"
        confidence = probability if probability > 0.5 else 1 - probability
        
        prediction = {
            'stock': self.stock_code,
            'date': latest_data.index[-1].strftime('%Y-%m-%d'),
            'probability_up': float(probability),
            'signal': signal,
            'confidence': float(confidence),
            'current_price': float(latest_data['close'].iloc[-1]),
            'fibonacci_status': self.get_fibonacci_status(latest_data),
            'golden_ratio_status': self.get_golden_ratio_status(latest_data)
        }
        
        print(f"📈 預測結果:")
        print(f"  上漲概率: {probability:.3f}")
        print(f"  交易信號: {signal}")
        print(f"  信心程度: {confidence:.3f}")
        print(f"  當前價格: {latest_data['close'].iloc[-1]:.2f}")
        
        return prediction
    
    def get_fibonacci_status(self, data):
        """獲取費波那契狀態"""
        status = {}
        
        # 檢查MA交叉
        if 'MA8' in data.columns and 'MA13' in data.columns:
            ma8 = data['MA8'].iloc[-1]
            ma13 = data['MA13'].iloc[-1]
            status['MA8_vs_MA13'] = "黃金交叉" if ma8 > ma13 else "死亡交叉"
            status['MA8_distance'] = float((data['close'].iloc[-1] / ma8 - 1) * 100)
        
        if 'MA13' in data.columns and 'MA34' in data.columns:
            ma13 = data['MA13'].iloc[-1]
            ma34 = data['MA34'].iloc[-1]
            status['MA13_vs_MA34'] = "黃金交叉" if ma13 > ma34 else "死亡交叉"
        
        return status
    
    def get_golden_ratio_status(self, data):
        """獲取黃金分割狀態"""
        status = {}
        
        if 'golden_618' in data.columns:
            current_price = data['close'].iloc[-1]
            golden_618 = data['golden_618'].iloc[-1]
            distance_pct = (current_price - golden_618) / golden_618 * 100
            
            status['near_golden_618'] = abs(distance_pct) < 2
            status['distance_to_618'] = float(distance_pct)
            
            if abs(distance_pct) < 1:
                status['position'] = "在0.618黃金分割位附近"
            elif distance_pct > 0:
                status['position'] = "在0.618之上"
            else:
                status['position'] = "在0.618之下"
        
        return status
    
    def backtest_strategy(self, data, initial_capital=100000):
        """回測交易策略"""
        print(f"\n📊 回測交易策略 (初始資金: ${initial_capital:,.0f})...")
        
        # 準備特徵
        features, _ = self.create_features(data)
        
        # 標準化
        features_scaled = self.scaler.transform(features)
        
        # 預測整個時間序列
        dpred = xgb.DMatrix(features_scaled)
        probabilities = self.model.predict(dpred)
        
        # 生成交易信號
        signals = pd.Series(index=data.index, data=probabilities)
        buy_signals = signals > 0.6
        sell_signals = signals < 0.4
        
        # 模擬交易
        capital = initial_capital
        position = 0  # 持股數量
        trades = []
        
        for i in range(1, len(data)):
            current_price = data['close'].iloc[i]
            prev_price = data['close'].iloc[i-1]
            
            # 買入信號
            if buy_signals.iloc[i] and position == 0:
                # 用50%資金買入
                buy_amount = capital * 0.5
                shares = buy_amount / current_price
                position = shares
                capital -= buy_amount
                
                trades.append({
                    'date': data.index[i],
                    'action': 'BUY',
                    'price': current_price,
                    'shares': shares,
                    'capital': capital + position * current_price
                })
            
            # 賣出信號
            elif sell_signals.iloc[i] and position > 0:
                sell_amount = position * current_price
                capital += sell_amount
                
                trades.append({
                    'date': data.index[i],
                    'action': 'SELL',
                    'price': current_price,
                    'shares': position,
                    'capital': capital
                })
                
                position = 0
        
        # 計算最終價值
        final_value = capital + (position * data['close'].iloc[-1] if position > 0 else 0)
        total_return = (final_value - initial_capital) / initial_capital * 100
        
        print(f"回測結果:")
        print(f"  初始資金: ${initial_capital:,.2f}")
        print(f"  最終價值: ${final_value:,.2f}")
        print(f"  總回報率: {total_return:.2f}%")
        print(f"  交易次數: {len(trades)}")
        
        if trades:
            winning_trades = sum(1 for t in trades if t['action'] == 'SELL' and 
                                t['price'] > trades[trades.index(t)-1]['price'])
            win_rate = winning_trades / len([t for t in trades if t['action'] == 'SELL']) * 100
            print(f"  勝率: {win_rate:.1f}%")
        
        return {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'trades': trades
        }

def main():
    """主函數"""
    print("=" * 70)
    print("📈 XGBoost股價預測系統 - 黃金分割 & 費波那契版本")
    print("=" * 70)
    
    # 初始化預測器
    stock_code = "00005"  # 匯豐控股
    predictor = FibonacciStockPredictor(stock_code)
    
    # 1. 獲取數據
    data = predictor.fetch_stock_data(days=500)
    
    # 2. 準備訓練數據
    X_train, X_test, y_train, y_test, feature_names = predictor.prepare_training_data(data)
    
    # 3. 訓練模型
    model = predictor.train_model(X_train, y_train, X_test, y_test)
    
    # 4. 預測下一天
    prediction = predictor.predict_next_day(data.tail(100))  # 使用最近100天數據
    
    # 5. 回測策略
    backtest_result = predictor.backtest_strategy(data.tail(200))
    
    # 6. 生成報告
    print(f"\n📋 系統報告:")
    print("-" * 50)
    print(f"股票代碼: {stock_code}")
    print(f"數據期間: {data.index[0].date()} 至 {data.index[-1].date()}")
    print(f"特徵數量: {len(feature_names)}")
    print(f"模型類型: XGBoost with Fibonacci & Golden Ratio")
    
    if prediction:
        print(f"\n🎯 最新預測:")
        print(f"  日期: {prediction['date']}")
        print(f"  信號: {prediction['signal']}")
        print(f"  信心: {prediction['confidence']:.3f}")
        
        if 'fibonacci_status' in prediction:
            fib_status = prediction['fibonacci_status']
            if 'MA8_vs_MA13' in fib_status:
                print(f"  MA8/13: {fib_status['MA8_vs_MA13']} (距離: {fib_status.get('MA8_distance', 0):.2f}%)")
        
        if 'golden_ratio_status' in prediction:
            golden_status = prediction['golden_ratio_status']
            if 'position' in golden_status:
                print(f"  黃金分割: {golden_status['position']}")
    
    print(f"\n💡 使用建議:")
    print("  1. 結合基本面分析使用")
    print("  2. 設置止損位 (建議: -5% 至 -8%)")
    print("  3. 分批建倉，控制風險")
    print("  4. 定期更新模型和數據")
    
    print(f"\n📁 生成文件:")
    print(f"  特徵重要性圖: feature_importance_{stock_code}.png")
    print(f"  模型已保存到內存")
    
    print(f"\n✅ 系統運行完成!")
    print("=" * 70)
    
    return predictor

if __name__ == "__main__":
    predictor = main()
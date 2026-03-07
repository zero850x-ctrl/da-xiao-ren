#!/usr/bin/env python3
"""
簡化版XGBoost股價預測 - 快速測試
包含黃金分割和費波那契指標
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

def create_synthetic_stock_data(days=500):
    """創建模擬股票數據"""
    print(f"📊 創建模擬股票數據 ({days}天)...")
    
    np.random.seed(42)
    
    # 生成價格序列（帶趨勢和季節性）
    time = np.arange(days)
    trend = 0.0005 * time  # 緩慢上升趨勢
    seasonal = 0.02 * np.sin(2 * np.pi * time / 60)  # 60天周期
    noise = np.random.normal(0, 0.015, days)  # 1.5%日波動
    
    # 累積收益率
    returns = 0.001 + trend + seasonal + noise
    prices = 100 * np.exp(np.cumsum(returns))
    
    # 創建DataFrame
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days)
    data = pd.DataFrame({
        'date': dates,
        'open': prices * (1 + np.random.normal(0, 0.005, days)),
        'high': prices * (1 + np.abs(np.random.normal(0, 0.01, days))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.01, days))),
        'close': prices,
        'volume': np.random.lognormal(14, 0.5, days)  # 對數正態分布
    })
    
    data.set_index('date', inplace=True)
    print(f"✅ 創建完成: 價格範圍 ${data['close'].min():.2f} - ${data['close'].max():.2f}")
    return data

def calculate_fibonacci_features(data):
    """計算費波那契特徵"""
    print("📈 計算費波那契特徵...")
    
    # 費波那契移動平均線
    fib_periods = [8, 13, 21, 34, 55]
    for period in fib_periods:
        if period < len(data):
            data[f'MA{period}'] = data['close'].rolling(period).mean()
    
    # MA交叉信號
    if 'MA8' in data.columns and 'MA13' in data.columns:
        data['MA8_above_MA13'] = (data['MA8'] > data['MA13']).astype(int)
    
    if 'MA13' in data.columns and 'MA34' in data.columns:
        data['MA13_above_MA34'] = (data['MA13'] > data['MA34']).astype(int)
    
    return data

def calculate_golden_ratio_features(data, lookback=55):
    """計算黃金分割特徵"""
    print("🎯 計算黃金分割特徵...")
    
    # 計算最近lookback天的最高最低
    high_55 = data['high'].rolling(lookback).max()
    low_55 = data['low'].rolling(lookback).min()
    price_range = high_55 - low_55
    
    # 黃金分割位
    golden_ratios = {
        '236': 0.236,  # 0.236
        '382': 0.382,  # 0.382
        '500': 0.5,    # 0.5
        '618': 0.618,  # 0.618 (最重要的黃金分割)
        '786': 0.786   # 0.786
    }
    
    for name, ratio in golden_ratios.items():
        level = low_55 + price_range * ratio
        data[f'golden_{name}'] = level
        
        # 計算價格相對位置
        data[f'pos_golden_{name}'] = (data['close'] - level) / price_range
        
        # 是否在黃金分割位附近（±2%）
        data[f'near_golden_{name}'] = (abs(data['close'] - level) / data['close'] < 0.02).astype(int)
    
    return data

def calculate_basic_indicators(data):
    """計算基本技術指標"""
    print("📊 計算技術指標...")
    
    # RSI (相對強弱指數)
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    data['RSI_overbought'] = (data['RSI'] > 70).astype(int)
    data['RSI_oversold'] = (data['RSI'] < 30).astype(int)
    
    # 價格動量
    for period in [1, 3, 5, 10, 20]:
        data[f'return_{period}d'] = data['close'].pct_change(period)
    
    # 成交量變化
    data['volume_change'] = data['volume'].pct_change()
    data['volume_ma_20'] = data['volume'].rolling(20).mean()
    data['volume_ratio'] = data['volume'] / data['volume_ma_20']
    
    # 價格模式
    data['higher_high'] = (data['high'] > data['high'].shift(1)).astype(int)
    data['higher_low'] = (data['low'] > data['low'].shift(1)).astype(int)
    
    return data

def prepare_features_and_labels(data, target_days=1):
    """準備特徵和標籤"""
    print("🔧 準備特徵和標籤...")
    
    # 計算所有特徵
    data = calculate_fibonacci_features(data)
    data = calculate_golden_ratio_features(data)
    data = calculate_basic_indicators(data)
    
    # 選擇特徵列
    feature_cols = []
    
    # 價格相關特徵
    price_features = ['open', 'high', 'low', 'close', 'volume']
    feature_cols.extend(price_features)
    
    # 費波那契特徵
    for period in [8, 13, 34]:
        if f'MA{period}' in data.columns:
            feature_cols.append(f'MA{period}')
            # 價格相對MA位置
            data[f'price_vs_MA{period}'] = data['close'] / data[f'MA{period}'] - 1
            feature_cols.append(f'price_vs_MA{period}')
    
    # MA交叉
    if 'MA8_above_MA13' in data.columns:
        feature_cols.append('MA8_above_MA13')
    if 'MA13_above_MA34' in data.columns:
        feature_cols.append('MA13_above_MA34')
    
    # 黃金分割特徵（重點關注0.618）
    golden_features = ['golden_618', 'pos_golden_618', 'near_golden_618']
    feature_cols.extend([f for f in golden_features if f in data.columns])
    
    # 技術指標
    tech_features = ['RSI', 'RSI_overbought', 'RSI_oversold', 
                    'volume_ratio', 'higher_high', 'higher_low']
    feature_cols.extend([f for f in tech_features if f in data.columns])
    
    # 動量特徵
    for period in [1, 5, 20]:
        if f'return_{period}d' in data.columns:
            feature_cols.append(f'return_{period}d')
    
    # 創建特徵DataFrame
    features = data[feature_cols].copy()
    
    # 處理缺失值
    features = features.fillna(method='ffill').fillna(0)
    
    # 創建標籤（未來target_d天上漲=1，下跌=0）
    future_return = data['close'].shift(-target_days) / data['close'] - 1
    labels = (future_return > 0).astype(int)  # 簡單二元分類
    
    # 對齊數據
    aligned_idx = ~(features.isna().any(axis=1) | labels.isna())
    features = features[aligned_idx]
    labels = labels[aligned_idx]
    
    print(f"✅ 特徵準備完成")
    print(f"  特徵數量: {len(feature_cols)}")
    print(f"  樣本數量: {len(features)}")
    print(f"  上漲樣本: {labels.sum()} ({labels.mean()*100:.1f}%)")
    
    return features, labels, feature_cols

def train_xgboost_model(features, labels, test_size=0.2):
    """訓練XGBoost模型"""
    print("🤖 訓練XGBoost模型...")
    
    # 分割數據
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=test_size, random_state=42, shuffle=False
    )
    
    print(f"  訓練集: {len(X_train)} 樣本")
    print(f"  測試集: {len(X_test)} 樣本")
    
    # XGBoost參數
    params = {
        'objective': 'binary:logistic',
        'eval_metric': 'logloss',
        'max_depth': 5,
        'learning_rate': 0.1,
        'n_estimators': 100,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42,
        'n_jobs': -1
    }
    
    # 訓練模型
    model = xgb.XGBClassifier(**params)
    model.fit(X_train, y_train,
              eval_set=[(X_test, y_test)],
              verbose=False)
    
    # 預測
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # 評估
    accuracy = accuracy_score(y_test, y_pred)
    print(f"✅ 模型訓練完成")
    print(f"  測試集準確率: {accuracy:.3f}")
    
    # 特徵重要性
    importance = model.feature_importances_
    feature_importance = pd.DataFrame({
        'feature': features.columns,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    print(f"\n🏆 最重要的5個特徵:")
    for i, (_, row) in enumerate(feature_importance.head(5).iterrows(), 1):
        print(f"  {i}. {row['feature']:25s} {row['importance']:.4f}")
    
    return model, X_test, y_test, y_pred, y_pred_proba, feature_importance

def generate_trading_signals(model, latest_data, feature_cols):
    """生成交易信號"""
    print("\n🔮 生成交易信號...")
    
    # 準備最新數據的特徵
    latest_features = latest_data[feature_cols].fillna(method='ffill').fillna(0)
    
    # 預測
    if len(latest_features) > 0:
        latest_features = latest_features.iloc[[-1]]  # 只取最新一天
        probability = model.predict_proba(latest_features)[0, 1]
        
        # 生成信號
        if probability > 0.65:
            signal = "強力買入"
            confidence = "高"
        elif probability > 0.55:
            signal = "買入"
            confidence = "中"
        elif probability < 0.35:
            signal = "強力賣出"
            confidence = "高"
        elif probability < 0.45:
            signal = "賣出"
            confidence = "中"
        else:
            signal = "持有"
            confidence = "低"
        
        current_price = latest_data['close'].iloc[-1]
        
        print(f"📈 最新預測結果:")
        print(f"  當前價格: ${current_price:.2f}")
        print(f"  上漲概率: {probability:.3f}")
        print(f"  交易信號: {signal}")
        print(f"  信心程度: {confidence}")
        
        # 檢查黃金分割位
        if 'golden_618' in latest_data.columns:
            golden_618 = latest_data['golden_618'].iloc[-1]
            distance_pct = (current_price - golden_618) / golden_618 * 100
            
            print(f"  0.618黃金分割位: ${golden_618:.2f}")
            print(f"  距離黃金分割位: {distance_pct:.2f}%")
            
            if abs(distance_pct) < 2:
                print(f"  ⚠️  接近黃金分割位，可能反轉")
        
        # 檢查費波那契MA
        if 'MA8' in latest_data.columns and 'MA13' in latest_data.columns:
            ma8 = latest_data['MA8'].iloc[-1]
            ma13 = latest_data['MA13'].iloc[-1]
            
            if ma8 > ma13:
                print(f"  📊 MA8 > MA13: 短期趨勢向上")
            else:
                print(f"  📊 MA8 < MA13: 短期趨勢向下")
        
        return {
            'signal': signal,
            'probability': probability,
            'confidence': confidence,
            'price': current_price
        }
    
    return None

def main():
    """主函數"""
    print("=" * 60)
    print("📈 XGBoost股價預測系統 (黃金分割 + 費波那契)")
    print("=" * 60)
    
    # 1. 創建模擬數據
    data = create_synthetic_stock_data(days=300)
    
    # 2. 準備特徵和標籤
    features, labels, feature_cols = prepare_features_and_labels(data, target_days=1)
    
    # 3. 訓練模型
    model, X_test, y_test, y_pred, y_pred_proba, feature_importance = train_xgboost_model(
        features, labels, test_size=0.2
    )
    
    # 4. 生成交易信號
    signal = generate_trading_signals(model, data, feature_cols)
    
    # 5. 簡單回測
    print(f"\n💰 簡單策略回測:")
    
    # 模擬買入持有策略
    initial_price = data['close'].iloc[0]
    final_price = data['close'].iloc[-1]
    buy_hold_return = (final_price - initial_price) / initial_price * 100
    
    print(f"  買入持有策略回報: {buy_hold_return:.2f}%")
    print(f"  初始價格: ${initial_price:.2f}")
    print(f"  最終價格: ${final_price:.2f}")
    
    # 6. 系統建議
    print(f"\n💡 系統使用建議:")
    print(f"  1. 結合模型信號和黃金分割位分析")
    print(f"  2. 當信號與技術位一致時行動")
    print(f"  3. 設置止損: -5% 至 -8%")
    print(f"  4. 分批建倉，控制風險")
    
    print(f"\n📊 系統統計:")
    print(f"  數據天數: {len(data)} 天")
    print(f"  特徵數量: {len(feature_cols)} 個")
    print(f"  模型準確率: {accuracy_score(y_test, y_pred):.3f}")
    
    if signal:
        print(f"  當前信號: {signal['signal']} ({signal['confidence']}信心)")
    
    print(f"\n✅ 系統運行完成!")
    print("=" * 60)
    
    return {
        'model': model,
        'data': data,
        'features': features,
        'feature_importance': feature_importance,
        'signal': signal
    }

if __name__ == "__main__":
    result = main()
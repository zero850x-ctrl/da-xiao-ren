#!/usr/bin/env python3
"""
可運行的XGBoost股價預測 - 包含黃金分割和費波那契
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("📈 XGBoost股價預測系統 - 黃金分割 & 費波那契版本")
print("=" * 70)

# 1. 創建模擬股票數據
print("\n📊 創建模擬股票數據...")
np.random.seed(42)

days = 300
time = np.arange(days)

# 生成價格序列
trend = 0.0003 * time  # 緩慢上升趨勢
seasonal = 0.015 * np.sin(2 * np.pi * time / 60)  # 60天周期
noise = np.random.normal(0, 0.02, days)  # 2%日波動

returns = 0.0005 + trend + seasonal + noise
prices = 100 * np.exp(np.cumsum(returns))

# 創建DataFrame
dates = pd.date_range(end=pd.Timestamp.now(), periods=days)
data = pd.DataFrame({
    'date': dates,
    'open': prices * (1 + np.random.normal(0, 0.005, days)),
    'high': prices * (1 + np.abs(np.random.normal(0, 0.01, days))),
    'low': prices * (1 - np.abs(np.random.normal(0, 0.01, days))),
    'close': prices,
    'volume': np.random.lognormal(14, 0.5, days)
})
data.set_index('date', inplace=True)

print(f"✅ 創建 {days} 天數據完成")
print(f"   價格範圍: ${data['close'].min():.2f} - ${data['close'].max():.2f}")

# 2. 計算費波那契移動平均線
print("\n📈 計算費波那契移動平均線...")
fib_periods = [8, 13, 21, 34, 55]

for period in fib_periods:
    if period < len(data):
        data[f'MA{period}'] = data['close'].rolling(period).mean()
        print(f"   MA{period}: 已計算")

# MA交叉信號
if 'MA8' in data.columns and 'MA13' in data.columns:
    data['MA8_above_MA13'] = (data['MA8'] > data['MA13']).astype(int)
    print("   MA8 vs MA13交叉信號: 已計算")

if 'MA13' in data.columns and 'MA34' in data.columns:
    data['MA13_above_MA34'] = (data['MA13'] > data['MA34']).astype(int)
    print("   MA13 vs MA34交叉信號: 已計算")

# 3. 計算黃金分割位
print("\n🎯 計算黃金分割位...")
lookback = 55
data['high_55'] = data['high'].rolling(lookback).max()
data['low_55'] = data['low'].rolling(lookback).min()
data['price_range_55'] = data['high_55'] - data['low_55']

# 黃金分割比率
golden_ratios = {
    '236': 0.236,  # 0.236
    '382': 0.382,  # 0.382
    '500': 0.5,    # 0.5
    '618': 0.618,  # 0.618 (最重要的黃金分割)
    '786': 0.786   # 0.786
}

for name, ratio in golden_ratios.items():
    data[f'golden_{name}'] = data['low_55'] + data['price_range_55'] * ratio
    print(f"   黃金分割位 0.{name}: 已計算")

# 特別關注0.618
if 'golden_618' in data.columns:
    data['near_golden_618'] = (abs(data['close'] - data['golden_618']) / data['close'] < 0.02).astype(int)
    print("   0.618附近信號: 已計算")

# 4. 計算技術指標
print("\n📊 計算技術指標...")

# RSI
delta = data['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
data['RSI'] = 100 - (100 / (1 + rs))
data['RSI_overbought'] = (data['RSI'] > 70).astype(int)
data['RSI_oversold'] = (data['RSI'] < 30).astype(int)
print("   RSI指標: 已計算")

# 價格動量
for period in [1, 3, 5, 10, 20]:
    data[f'return_{period}d'] = data['close'].pct_change(period)
print("   價格動量: 已計算")

# 成交量
data['volume_ma_20'] = data['volume'].rolling(20).mean()
data['volume_ratio'] = data['volume'] / data['volume_ma_20']
data['volume_spike'] = (data['volume_ratio'] > 2).astype(int)
print("   成交量指標: 已計算")

# 5. 準備特徵和標籤
print("\n🔧 準備特徵和標籤...")

# 選擇特徵
feature_cols = [
    'open', 'high', 'low', 'close', 'volume',
    'MA8', 'MA13', 'MA34',
    'MA8_above_MA13', 'MA13_above_MA34',
    'golden_618', 'near_golden_618',
    'RSI', 'RSI_overbought', 'RSI_oversold',
    'return_1d', 'return_5d', 'return_20d',
    'volume_ratio', 'volume_spike'
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

print(f"✅ 特徵準備完成")
print(f"   特徵數量: {len(available_features)}")
print(f"   樣本數量: {len(features)}")
print(f"   上漲天數: {labels.sum()} ({labels.mean()*100:.1f}%)")
print(f"   下跌天數: {len(labels)-labels.sum()} ({(1-labels.mean())*100:.1f}%)")

# 6. 訓練XGBoost模型
print("\n🤖 訓練XGBoost模型...")

try:
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    
    # 分割數據（時間序列，不隨機打亂）
    split_idx = int(len(features) * 0.8)
    X_train = features.iloc[:split_idx]
    X_test = features.iloc[split_idx:]
    y_train = labels.iloc[:split_idx]
    y_test = labels.iloc[split_idx:]
    
    print(f"   訓練集: {len(X_train)} 樣本 ({len(X_train)/len(features)*100:.1f}%)")
    print(f"   測試集: {len(X_test)} 樣本 ({len(X_test)/len(features)*100:.1f}%)")
    
    # XGBoost參數
    params = {
        'objective': 'binary:logistic',
        'eval_metric': 'logloss',
        'max_depth': 4,
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
    print(f"   測試集準確率: {accuracy:.3f}")
    
    # 特徵重要性
    importance = model.feature_importances_
    feature_importance = pd.DataFrame({
        'feature': available_features,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    print(f"\n🏆 最重要的特徵排名:")
    print("-" * 40)
    for i, (_, row) in enumerate(feature_importance.head(8).iterrows(), 1):
        print(f"  {i:2d}. {row['feature']:25s} {row['importance']:.4f}")
    
    # 7. 生成交易信號
    print(f"\n🔮 生成最新交易信號...")
    
    if len(features) > 0:
        latest_features = features.iloc[[-1]]
        probability = model.predict_proba(latest_features)[0, 1]
        current_price = data['close'].iloc[-1]
        
        # 生成信號
        if probability > 0.65:
            signal = "🟢 強力買入"
            action = "BUY"
        elif probability > 0.55:
            signal = "🟡 買入"
            action = "BUY"
        elif probability < 0.35:
            signal = "🔴 強力賣出"
            action = "SELL"
        elif probability < 0.45:
            signal = "🟠 賣出"
            action = "SELL"
        else:
            signal = "⚪ 持有"
            action = "HOLD"
        
        confidence = probability if probability > 0.5 else 1 - probability
        
        print(f"📈 預測結果:")
        print(f"   當前價格: ${current_price:.2f}")
        print(f"   上漲概率: {probability:.3f}")
        print(f"   交易信號: {signal}")
        print(f"   信心程度: {confidence:.3f}")
        
        # 技術分析
        print(f"\n📊 技術分析:")
        
        # 黃金分割分析
        if 'golden_618' in data.columns:
            golden_618 = data['golden_618'].iloc[-1]
            distance_pct = (current_price - golden_618) / golden_618 * 100
            print(f"   0.618黃金分割位: ${golden_618:.2f}")
            print(f"   當前距離: {distance_pct:+.2f}%")
            
            if abs(distance_pct) < 2:
                print(f"   ⚠️  接近黃金分割位，可能出現反轉")
        
        # 費波那契MA分析
        if 'MA8' in data.columns and 'MA13' in data.columns:
            ma8 = data['MA8'].iloc[-1]
            ma13 = data['MA13'].iloc[-1]
            ma34 = data['MA34'].iloc[-1] if 'MA34' in data.columns else None
            
            print(f"   MA8: ${ma8:.2f}")
            print(f"   MA13: ${ma13:.2f}")
            
            if ma8 > ma13:
                print(f"   📈 MA8 > MA13: 短期趨勢向上")
            else:
                print(f"   📉 MA8 < MA13: 短期趨勢向下")
            
            if ma34:
                print(f"   MA34: ${ma34:.2f}")
        
        # RSI分析
        if 'RSI' in data.columns:
            rsi = data['RSI'].iloc[-1]
            print(f"   RSI: {rsi:.1f}")
            if rsi > 70:
                print(f"   ⚠️  RSI超買 (>70)")
            elif rsi < 30:
                print(f"   ⚠️  RSI超賣 (<30)")
        
        # 8. 交易建議
        print(f"\n💡 交易建議:")
        
        if action == "BUY":
            print(f"   1. 考慮分批買入")
            print(f"   2. 建議買入價: ${current_price * 0.99:.2f} - ${current_price:.2f}")
            print(f"   3. 止損位: ${current_price * 0.95:.2f} (-5%)")
            print(f"   4. 目標價: ${current_price * 1.08:.2f} (+8%)")
        
        elif action == "SELL":
            print(f"   1. 考慮減倉或賣出")
            print(f"   2. 建議賣出價: ${current_price:.2f} - ${current_price * 1.01:.2f}")
            print(f"   3. 如持有，考慮設定止盈")
        
        else:  # HOLD
            print(f"   1. 保持觀望")
            print(f"   2. 等待更明確信號")
            print(f"   3. 密切關注黃金分割位")
        
        # 9. 風險提示
        print(f"\n⚠️  風險提示:")
        print(f"   1. 模型預測僅供參考")
        print(f"   2. 股市有風險，投資需謹慎")
        print(f"   3. 建議結合基本面分析")
        print(f"   4. 控制倉位，分散風險")
        
except Exception as e:
    print(f"❌ 模型訓練失敗: {e}")
    print(f"💡 請檢查XGBoost安裝")

# 10. 系統總結
print(f"\n📋 系統總結:")
print("-" * 40)
print(f"數據期間: {data.index[0].date()} 至 {data.index[-1].date()}")
print(f"特徵數量: {len(available_features)}")
print(f"模型類型: XGBoost with Fibonacci & Golden Ratio")

if 'accuracy' in locals():
    print(f"模型準確率: {accuracy:.3f}")

print(f"\n🎯 核心技術:")
print(f"  • 費波那契移動平均線 (8, 13, 34天)")
print(f"  • 黃金分割位分析 (0.618重點)")
print(f"  • XGBoost機器學習預測")
print(f"  • 多因子特徵工程")

print(f"\n✅ 系統運行完成!")
print("=" * 70)
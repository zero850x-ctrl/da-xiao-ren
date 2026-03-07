#!/usr/bin/env python3
"""
XGBoost股價預測 - 使用真實富途API數據
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime, timedelta
import sys

print("=" * 70)
print("📈 XGBoost股價預測 - 真實數據版本")
print("=" * 70)

def get_real_stock_data(stock_code="00005", days=365):
    """從富途API獲取真實股票數據"""
    print(f"📊 嘗試從富途API獲取 {stock_code} 數據...")
    
    try:
        import futu as ft
        
        # 連接富途OpenD
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 計算開始日期
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days*2)  # 多取一些數據
        
        # 獲取K線數據
        ret, data, page_req_key = quote_ctx.get_history_kline(
            code=f"HK.{stock_code}",
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            ktype=ft.KLType.K_DAY,
            max_count=days*2  # 最多獲取的天數
        )
        
        quote_ctx.close()
        
        if ret == ft.RET_OK:
            print(f"✅ 成功獲取 {len(data)} 天數據")
            
            # 重命名列以匹配我們的系統
            data.rename(columns={
                'time_key': 'date',
                'open': 'open',
                'high': 'high', 
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }, inplace=True)
            
            # 設置日期索引
            data['date'] = pd.to_datetime(data['date'])
            data.set_index('date', inplace=True)
            
            # 只保留需要的列
            data = data[['open', 'high', 'low', 'close', 'volume']]
            
            print(f"   日期範圍: {data.index[0].date()} 至 {data.index[-1].date()}")
            print(f"   價格範圍: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
            
            return data
        else:
            print(f"❌ 獲取數據失敗: {data}")
            return None
            
    except Exception as e:
        print(f"❌ 富途API連接失敗: {e}")
        print("💡 請確保:")
        print("   1. 富途OpenD正在運行 (端口11111)")
        print("   2. 已安裝futu-api: pip install futu-api")
        print("   3. 有有效的市場數據訂閱")
        
        # 返回模擬數據作為備用
        print("\n📊 使用模擬數據作為備用...")
        return create_simulation_data(days)

def create_simulation_data(days=365):
    """創建模擬數據（備用）"""
    np.random.seed(42)
    
    time = np.arange(days)
    trend = 0.0003 * time
    seasonal = 0.015 * np.sin(2 * np.pi * time / 60)
    noise = np.random.normal(0, 0.02, days)
    
    returns = 0.0005 + trend + seasonal + noise
    prices = 100 * np.exp(np.cumsum(returns))
    
    dates = pd.date_range(end=datetime.now(), periods=days)
    data = pd.DataFrame({
        'date': dates,
        'open': prices * (1 + np.random.normal(0, 0.005, days)),
        'high': prices * (1 + np.abs(np.random.normal(0, 0.01, days))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.01, days))),
        'close': prices,
        'volume': np.random.lognormal(14, 0.5, days)
    })
    
    data.set_index('date', inplace=True)
    print(f"✅ 創建模擬數據 {days} 天")
    return data

def calculate_fibonacci_features(data):
    """計算費波那契特徵"""
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
    data['high_55'] = data['high'].rolling(lookback).max()
    data['low_55'] = data['low'].rolling(lookback).min()
    data['price_range_55'] = data['high_55'] - data['low_55']
    
    # 黃金分割比率
    golden_ratios = {
        '236': 0.236,
        '382': 0.382, 
        '500': 0.5,
        '618': 0.618,  # 最重要的黃金分割
        '786': 0.786
    }
    
    for name, ratio in golden_ratios.items():
        data[f'golden_{name}'] = data['low_55'] + data['price_range_55'] * ratio
    
    # 特別關注0.618
    if 'golden_618' in data.columns:
        data['near_golden_618'] = (abs(data['close'] - data['golden_618']) / data['close'] < 0.02).astype(int)
    
    return data

def calculate_technical_indicators(data):
    """計算技術指標"""
    # RSI
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
    
    # 成交量
    data['volume_ma_20'] = data['volume'].rolling(20).mean()
    data['volume_ratio'] = data['volume'] / data['volume_ma_20']
    data['volume_spike'] = (data['volume_ratio'] > 2).astype(int)
    
    return data

def prepare_features(data):
    """準備特徵數據"""
    data = calculate_fibonacci_features(data)
    data = calculate_golden_ratio_features(data)
    data = calculate_technical_indicators(data)
    
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
    
    return features, available_features

def train_and_evaluate(features, target_days=1):
    """訓練和評估模型"""
    # 創建標籤（預測未來target_d天上漲）
    future_return = features['close'].shift(-target_days) / features['close'] - 1
    labels = (future_return > 0).astype(int)
    
    # 對齊數據
    aligned_idx = ~(features.isna().any(axis=1) | labels.isna())
    X = features[aligned_idx]
    y = labels[aligned_idx]
    
    print(f"\n📊 數據統計:")
    print(f"   總樣本: {len(X)}")
    print(f"   上漲天數: {y.sum()} ({y.mean()*100:.1f}%)")
    print(f"   下跌天數: {len(y)-y.sum()} ({(1-y.mean())*100:.1f}%)")
    
    # 時間序列分割（不隨機打亂）
    split_idx = int(len(X) * 0.8)
    X_train = X.iloc[:split_idx]
    X_test = X.iloc[split_idx:]
    y_train = y.iloc[:split_idx]
    y_test = y.iloc[split_idx:]
    
    print(f"\n🤖 訓練XGBoost模型...")
    print(f"   訓練集: {len(X_train)} 樣本")
    print(f"   測試集: {len(X_test)} 樣本")
    
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
        'feature': X.columns,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    print(f"\n🏆 最重要的特徵排名:")
    print("-" * 40)
    for i, (_, row) in enumerate(feature_importance.head(8).iterrows(), 1):
        print(f"  {i:2d}. {row['feature']:25s} {row['importance']:.4f}")
    
    return model, X_test, y_test, y_pred, y_pred_proba, feature_importance

def generate_signal(model, features, data):
    """生成交易信號"""
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
        
        return {
            'signal': signal,
            'action': action,
            'probability': probability,
            'confidence': confidence,
            'price': current_price,
            'golden_618': golden_618 if 'golden_618' in data.columns else None,
            'distance_to_golden': distance_pct if 'golden_618' in data.columns else None
        }
    
    return None

def main():
    """主函數"""
    # 測試多個股票
    stock_codes = ["00005", "00700", "09988"]  # 匯豐、騰訊、阿里
    
    results = {}
    
    for stock_code in stock_codes:
        print(f"\n{'='*70}")
        print(f"📊 分析股票: HK.{stock_code}")
        print(f"{'='*70}")
        
        # 1. 獲取數據
        data = get_real_stock_data(stock_code, days=365)
        
        if data is None or len(data) < 100:
            print(f"❌ 數據不足，跳過 {stock_code}")
            continue
        
        # 2. 準備特徵
        features, feature_names = prepare_features(data)
        
        if len(features) < 50:
            print(f"❌ 特徵數據不足，跳過 {stock_code}")
            continue
        
        # 3. 訓練模型
        model, X_test, y_test, y_pred, y_pred_proba, feature_importance = train_and_evaluate(features)
        
        # 4. 生成信號
        signal = generate_signal(model, features, data)
        
        if signal:
            results[stock_code] = {
                'accuracy': accuracy_score(y_test, y_pred),
                'signal': signal,
                'feature_importance': feature_importance.head(5).to_dict('records')
            }
    
    # 總結報告
    print(f"\n{'='*70}")
    print(f"📋 分析總結報告")
    print(f"{'='*70}")
    
    if results:
        print(f"\n🎯 推薦股票排名:")
        print("-" * 40)
        
        # 按信心程度排序
        sorted_stocks = sorted(results.items(), 
                              key=lambda x: x[1]['signal']['confidence'], 
                              reverse=True)
        
        for i, (stock_code, result) in enumerate(sorted_stocks, 1):
            signal = result['signal']
            print(f"{i:2d}. HK.{stock_code}")
            print(f"   信號: {signal['signal']}")
            print(f"   信心: {signal['confidence']:.3f}")
            print(f"   價格: ${signal['price']:.2f}")
            print(f"   準確率: {result['accuracy']:.3f}")
            
            if signal['golden_618']:
                print(f"   黃金分割位: ${signal['golden_618']:.2f}")
                print(f"   距離: {signal['distance_to_golden']:+.2f}%")
            print()
        
        print(f"💡 投資建議:")
        print(f"  1. 優先考慮信心程度高的股票")
        print(f"  2. 結合黃金分割位分析")
        print(f"  3. 控制倉位，分散風險")
        print(f"  4. 設置止損位 (-5% 至 -8%)")
        
    else:
        print("❌ 沒有成功分析的股票")
    
    print(f"\n✅ 真實數據分析完成!")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
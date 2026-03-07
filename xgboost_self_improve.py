#!/usr/bin/env python3
"""
XGBoost 自我學習系統 - 擴展版 (15-20隻股票)
每日17:00自動運行
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np

WORKSPACE = Path('/Users/gordonlui/.openclaw/workspace')
MODEL_DIR = WORKSPACE / 'models'
REPORT_DIR = WORKSPACE / 'models'
MODEL_DIR.mkdir(exist_ok=True)

# 擴展股票列表 (20隻)
STOCKS = [
    'HK.00992',  # 聯想集團
    'HK.00700',  # 騰訊控股
    'HK.09988',  # 阿里巴巴
    'HK.02800',  # 盈富基金
    'HK.07500',  # 兩倍看空恆指
    'HK.01211',  # 比亞迪
    'HK.09618',  # 京東集團
    'HK.00005',  # 匯豐控股
    'HK.01398',  # 工商銀行
    'HK.02638',  # 港燈
    'HK.01810',  # 小米集團
    'HK.00857',  # 中國石油
    'HK.01024',  # 快手
    'HK.02318',  # 中國銀行
    'HK.02331',  # 李寧
    'HK.02343',  # 太平洋航運
    'HK.00358',  # 江西銅業
    'HK.03750',  # 寧德時代
    'HK.02333',  # POP MART
    'HK.09999',  # 網易
]

def get_kline_data(code, days=90):
    try:
        from futu import OpenQuoteContext, KLType
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        ret, data, _ = quote_ctx.request_history_kline(
            code,
            start=(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            end=datetime.now().strftime('%Y-%m-%d'),
            ktype=KLType.K_DAY,
            max_count=500
        )
        quote_ctx.close()
        if ret == 0 and data is not None and not data.empty:
            return data
        return None
    except Exception as e:
        print(f"  ❌ {code}: {e}")
        return None

def create_features(df):
    features = pd.DataFrame()
    close = df['close'].astype(float)
    high = df['high'].astype(float)
    low = df['low'].astype(float)
    volume = df['volume'].astype(float)
    
    # 價格變化
    features['return_1d'] = close.pct_change(1).fillna(0)
    features['return_5d'] = close.pct_change(5).fillna(0)
    features['return_10d'] = close.pct_change(10).fillna(0)
    
    # 黃金分割位 (20日, 60日)
    for window in [20, 60]:
        rolling_high = high.rolling(window).max()
        rolling_low = low.rolling(window).min()
        for key in ['0.382', '0.5', '0.618']:
            golden_level = rolling_low + (rolling_high - rolling_low) * float(key)
            features[f'golden_{key}_{window}d'] = (close / golden_level - 1).fillna(0)
    
    # 均線 (8, 13, 21, 34, 55)
    for window in [8, 13, 21, 34, 55]:
        ma = close.rolling(window).mean()
        features[f'MA{window}'] = (close / ma - 1).fillna(0)
    
    # EMA (8, 13, 21, 34)
    for span in [8, 13, 21, 34]:
        ema = close.ewm(span=span, adjust=False).mean()
        features[f'EMA{span}'] = (close / ema - 1).fillna(0)
    
    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    features['RSI'] = (100 - (100 / (1 + rs))).fillna(50)
    
    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    features['MACD'] = macd.fillna(0)
    features['MACD_hist'] = (macd - signal).fillna(0)
    
    # 布林線
    bb20 = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    bb_upper = bb20 + 2 * bb_std
    bb_lower = bb20 - 2 * bb_std
    features['BB_position'] = ((close - bb_lower) / (bb_upper - bb_lower) * 100).fillna(50)
    
    # 成交量
    avg_volume = volume.rolling(20).mean()
    features['volume_ratio'] = (volume / avg_volume).fillna(1)
    
    # 目標標籤: 未來5日回報
    future_return = close.shift(-5) / close - 1
    features['label'] = pd.cut(future_return, bins=[-float('inf'), -0.02, 0.02, float('inf')], labels=[-1, 0, 1])
    features['label'] = features['label'].astype(float).fillna(0)
    
    return features.fillna(0)

def train_model(all_features):
    print("🔄 訓練模型...")
    
    feature_cols = [c for c in all_features.columns if c != 'label']
    X = all_features[feature_cols]
    y = all_features['label']
    
    # 移除中立數據
    valid_idx = y != 0
    X = X[valid_idx]
    y = y[valid_idx]
    
    if len(X) < 50:
        print("⚠️ 數據不足")
        return None, {}
    
    try:
        from xgboost import XGBClassifier
        model = XGBClassifier(n_estimators=150, max_depth=6, learning_rate=0.1, random_state=42, use_label_encoder=False, eval_metric='logloss')
        y_transformed = y + 1
        model.fit(X, y_transformed)
    except:
        from sklearn.ensemble import GradientBoostingClassifier
        model = GradientBoostingClassifier(n_estimators=150, max_depth=6, random_state=42)
        y_transformed = y + 1
        model.fit(X, y_transformed)
    
    importance = dict(zip(feature_cols, model.feature_importances_))
    
    import joblib
    model_path = MODEL_DIR / 'xgboost_model_real.pkl'
    joblib.dump(model, model_path)
    
    print(f"✅ 模型已保存: {model_path}")
    print(f"📊 訓練樣本: {len(X)}")
    
    return model, importance

def generate_report(importance, total_stocks, total_data):
    importance_sorted = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    
    report = f"""# XGBoost 自我學習報告
**日期:** {datetime.now().strftime('%Y%m%d')}

## 訓練數據
- 股票數: {total_stocks}隻
- 數據總量: {total_data}條
- 週期: 過去90日
- 來源: 富途API (真實數據)

## 特徵重要性排序

"""
    for feat, imp in importance_sorted[:20]:
        report += f"- {feat}: {imp:.4f}\n"
    
    top_5 = [f for f, _ in importance_sorted[:5]]
    report += f"""
## 關鍵發現
模型主要依靠以下特徵進行預測:
{', '.join(top_5)}

---
*此報告由 XGBoost 自我學習系統自動生成*
"""
    
    report_path = REPORT_DIR / f'improvement_report_{datetime.now().strftime("%Y%m%d")}.md'
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"📄 報告: {report_path}")
    return report_path

def main():
    print(f"🚀 XGBoost自我學習系統 (擴展版) - {datetime.now()}")
    print("=" * 50)
    print(f"📊 目標: {len(STOCKS)}隻股票")
    
    all_features = []
    success_count = 0
    
    for code in STOCKS:
        print(f"📥 {code}...", end=" ")
        df = get_kline_data(code, days=90)
        if df is not None and len(df) > 30:
            features = create_features(df)
            all_features.append(features)
            success_count += 1
            print(f"✅ {len(df)}條")
        else:
            print("❌")
    
    if not all_features:
        print("❌ 無數據")
        return
    
    all_features = pd.concat(all_features, ignore_index=True)
    print(f"\n📊 總數據: {len(all_features)}條 ({success_count}隻股票)")
    
    model, importance = train_model(all_features)
    if importance:
        generate_report(importance, success_count, len(all_features))
    
    print("✅ 完成")

if __name__ == '__main__':
    main()

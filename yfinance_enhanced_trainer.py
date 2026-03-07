#!/usr/bin/env python3
"""yFinance 80隻股票訓練"""

import yfinance as yf
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

STOCKS = [
    "9618.HK","9988.HK","1810.HK","1024.HK","9888.HK","9999.HK","3690.HK","2328.HK","1177.HK","2269.HK",
    "9961.HK","1044.HK","2833.HK","0722.HK","0772.HK","0669.HK","0384.HK","3659.HK","1211.HK","2015.HK",
    "9868.HK","175.HK","0025.HK","1908.HK","3333.HK","0981.HK","0980.HK","0005.HK","1398.HK","2628.HK",
    "3968.HK","0939.HK","0388.HK","3328.HK","0881.HK","0941.HK","0233.HK","3969.HK","0688.HK","1988.HK",
    "0001.HK","2388.HK","2319.HK","291.HK","1880.HK","1515.HK","0195.HK","0870.HK","1970.HK","0836.HK",
    "1488.HK","2138.HK","1928.HK","1122.HK","0813.HK","0175.HK","0178.HK","1548.HK","2259.HK","0185.HK",
    "0192.HK","0661.HK","1088.HK","1171.HK","1919.HK","1109.HK","0969.HK","1071.HK","6098.HK","1093.HK",
    "2186.HK","1876.HK","1521.HK","1448.HK","0170.HK","0048.HK","0930.HK","0220.HK","1038.HK","1044.HK",
]

PERIODS = ["2y","3y"]
THRESHOLDS = [0.005, 0.01]

def calc_features(df):
    # Flatten columns if needed
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    
    close, high, low, vol = df['Close'], df['High'], df['Low'], df['Volume']
    e12, e26 = close.ewm(span=12), close.ewm(span=26)
    macd, sig = e12-e26, macd.ewm(span=9)
    df['MACD'], df['MACD_hist'] = macd, macd-sig
    df['MA8'], df['MA34'] = close.rolling(8).mean(), close.rolling(34).mean()
    df['EMA8'] = close.ewm(span=8)
    df['volume_ratio'] = vol/vol.rolling(20).mean()
    d = close.diff()
    g = d.where(d>0,0).rolling(14).mean()
    l = (-d.where(d<0,0)).rolling(14).mean()
    df['RSI'] = 100-(100/(1+g/l))
    h55, l55 = high.rolling(55).max(), low.rolling(55).min()
    df['golden_0.618'] = (close-(l55+(h55-l55)*0.618))/(h55-l55+1e-8)
    return df

print(f"🚀 80隻股票訓練...")
all_data = []
for t in STOCKS:
    for p in PERIODS:
        try:
            df = yf.download(t, period=p, auto_adjust=True, progress=False)
            if df is None or len(df) < 100: continue
            df = calc_features(df)
            for th in THRESHOLDS:
                df['target'] = (df['Close'].shift(-1)>df['Close']*(1+th)).astype(int)
                dc = df[['MACD_hist','MACD','MA8','MA34','EMA8','volume_ratio','RSI','golden_0.618','target']].dropna()
                if len(dc) > 50: all_data.append(dc)
        except: continue

if not all_data: print("❌ No data"); exit(1)

all_df = pd.concat(all_data, ignore_index=True)
print(f"📊 總數據: {len(all_df)} 條")

X = all_df.drop('target', axis=1)
y = all_df['target']
s = int(len(X)*0.8)

model = XGBClassifier(n_estimators=150, max_depth=5, learning_rate=0.1, random_state=42, eval_metric='logloss')
model.fit(X.iloc[:s], y.iloc[:s])

acc = accuracy_score(y.iloc[s:], model.predict(X.iloc[s:]))
print(f"✅ 準確率: {acc:.1%}")

imp = pd.Series(model.feature_importances_,index=X.columns).sort_values(ascending=False)*100
print(imp.round(1))

model.save_model('/Users/gordonlui/.openclaw/workspace/models/yfinance_enhanced_model.json')
print("✅ Saved")

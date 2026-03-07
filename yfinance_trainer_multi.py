import yfinance as yf
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

# 推薦股票池 (12隻)
RECOMMENDED = [
    "9618.HK",   # 京東
    "9988.HK",   # 阿里巴巴
    "3690.HK",   # 美團
    "700.HK",    # 騰訊
    "1810.HK",   # 小米
    "1024.HK",   # 快手
    "9888.HK",   # 百度
    "9999.HK",   # 網易
    "2015.HK",   # 理想汽車
    "9868.HK",   # 小鵬汽車
    "1211.HK",   # 比亞迪
    "6618.HK",   # 京東健康
]

# 自己挑多18隻
ADDITIONAL = [
    "2319.HK",   # 李寧
    "2388.HK",   # 香港交易所
    "0005.HK",   # 匯豐
    "1398.HK",   # 工商銀行
    "2628.HK",   # 中國人壽
    "3968.HK",   # 招商銀行
    "0388.HK",   # 香港交易所
    "6837.HK",   # 華潤燃氣
    "0881.HK",   # 中國移動
    "0941.HK",   # 中國電信
    "0762.HK",   # 中國聯通
    "0728.HK",   # 中國鐵塔
    "1171.HK",   # 兗州煤業
    "1088.HK",   # 中國神華
    "1177.HK",   # 中國生物製藥
    "1093.HK",   # 石藥集團
    "0669.HK",   # 中國創新藥
    "2259.HK",   # 諾誠健康
]

ALL_STOCKS = RECOMMENDED + ADDITIONAL
PERIOD = "2y"
TARGET_THRESHOLD = 0.005

def calculate_features(df):
    """計算8個feature"""
    close = df['Close']
    high = df['High']
    low = df['Low']
    volume = df['Volume']
    
    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    df['MACD'] = macd
    df['MACD_hist'] = macd - signal
    
    # MA
    df['MA8'] = close.rolling(8).mean()
    df['MA34'] = close.rolling(34).mean()
    df['EMA8'] = close.ewm(span=8, adjust=False).mean()
    
    # Volume
    df['vol_ma20'] = volume.rolling(20).mean()
    df['volume_ratio'] = volume / df['vol_ma20']
    
    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Golden 0.618
    window = 55
    swing_high = high.rolling(window).max()
    swing_low = low.rolling(window).min()
    fib_618 = swing_low + (swing_high - swing_low) * 0.618
    df['golden_0.618'] = (close - fib_618) / (swing_high - swing_low + 1e-8)
    
    return df

print(f"🚀 開始訓練 {len(ALL_STOCKS)} 隻股票...")
print("=" * 50)

all_X = []
all_y = []
results = []

for ticker in ALL_STOCKS:
    try:
        print(f"📥 {ticker}...", end=" ")
        df = yf.download(ticker, period=PERIOD, auto_adjust=True)
        df.columns = [c[0] for c in df.columns]
        
        if len(df) < 200:
            print(f"❌ 數據不足")
            continue
        
        df = calculate_features(df)
        df['target'] = (df['Close'].shift(-1) > df['Close'] * (1 + TARGET_THRESHOLD)).astype(int)
        
        feature_cols = ['MACD_hist', 'MACD', 'MA8', 'MA34', 'EMA8', 'volume_ratio', 'RSI', 'golden_0.618']
        df_clean = df[feature_cols + ['target']].dropna()
        
        if len(df_clean) < 100:
            print(f"❌ 清洗後數據不足")
            continue
        
        X = df_clean[feature_cols]
        y = df_clean['target']
        
        # 簡單訓練
        model = XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42, eval_metric='logloss')
        model.fit(X, y)
        
        # 預測
        y_pred = model.predict(X)
        acc = accuracy_score(y, y_pred)
        
        all_X.append(X)
        all_y.append(y)
        
        results.append({
            'ticker': ticker,
            'accuracy': acc,
            'samples': len(df_clean),
            'model': model
        })
        
        print(f"✅ {len(df_clean)}樣本, acc={acc:.1%}")
        
    except Exception as e:
        print(f"❌ {e}")

print("\n" + "=" * 50)
print(f"📊 成功訓練 {len(results)} 隻股票")

# 合併所有數據訓練最終模型
print("\n🔄 訓練最終模型...")
all_X = pd.concat(all_X)
all_y = pd.concat(all_y)

# 時間序列split
split_idx = int(len(all_X) * 0.8)
X_train = all_X.iloc[:split_idx]
X_test = all_X.iloc[split_idx:]
y_train = all_y.iloc[:split_idx]
y_test = all_y.iloc[split_idx:]

final_model = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42, eval_metric='logloss')
final_model.fit(X_train, y_train)

# 評估
y_pred_final = final_model.predict(X_test)
acc_final = accuracy_score(y_test, y_pred_final)
print(f"最終模型測試準確率: {acc_final:.1%}")

# Feature Importance
feature_cols = ['MACD_hist', 'MACD', 'MA8', 'MA34', 'EMA8', 'volume_ratio', 'RSI', 'golden_0.618']
importance = pd.Series(final_model.feature_importances_, index=feature_cols).sort_values(ascending=False) * 100
print("\nFeature Importance:")
print(importance.round(1))

# 保存最終模型
final_model.save_model('/Users/gordonlui/.openclaw/workspace/models/yfinance_multi_model.json')
print(f"\n✅ 最終模型已保存: models/yfinance_multi_model.json")

# 保存個別模型供日後使用
import joblib
for r in results:
    ticker_clean = r['ticker'].replace('.HK', '')
    joblib.dump(r['model'], f'/Users/gordonlui/.openclaw/workspace/models/{ticker_clean}_model.pkl')
print(f"✅ {len(results)} 隻個別模型已保存")

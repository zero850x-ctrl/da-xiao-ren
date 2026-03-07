import yfinance as yf
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

TICKER = "9618.HK"
PERIOD = "2y"
TARGET_THRESHOLD = 0.005

print(f"拉取 {TICKER} 數據...")
df = yf.download(TICKER, period=PERIOD, auto_adjust=True)
df.columns = [c[0] for c in df.columns]

# 計算feature
close = df['Close']
high = df['High']
low = df['Low']
volume = df['Volume']

ema12 = close.ewm(span=12, adjust=False).mean()
ema26 = close.ewm(span=26, adjust=False).mean()
macd = ema12 - ema26
signal = macd.ewm(span=9, adjust=False).mean()
df['MACD'] = macd
df['MACD_hist'] = macd - signal
df['MA8'] = close.rolling(8).mean()
df['MA34'] = close.rolling(34).mean()
df['EMA8'] = close.ewm(span=8, adjust=False).mean()
df['vol_ma20'] = volume.rolling(20).mean()
df['volume_ratio'] = volume / df['vol_ma20']
delta = close.diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
df['RSI'] = 100 - (100 / (1 + rs))
window = 55
swing_high = high.rolling(window).max()
swing_low = low.rolling(window).min()
fib_618 = swing_low + (swing_high - swing_low) * 0.618
df['golden_0.618'] = (close - fib_618) / (swing_high - swing_low + 1e-8)

df['target'] = (close.shift(-1) > close * (1 + TARGET_THRESHOLD)).astype(int)
df['close_orig'] = close

feature_cols = ['MACD_hist', 'MACD', 'MA8', 'MA34', 'EMA8', 'volume_ratio', 'RSI', 'golden_0.618']
df_clean = df[feature_cols + ['target', 'close_orig']].dropna()

X = df_clean[feature_cols]
y = df_clean['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

model = XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42, eval_metric='logloss')
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\n測試準確率: {acc:.1%}")
print(classification_report(y_test, y_pred))

importance = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False) * 100
print("\nFeature Importance:")
print(importance.round(1))

# Backtest
test_idx = df_clean.index[-len(y_test):]
backtest_df = pd.DataFrame({
    'Close': df_clean.loc[test_idx, 'close_orig'].values,
    'signal': y_pred
})
backtest_df['daily_ret'] = backtest_df['Close'].pct_change()
backtest_df['strategy_ret'] = backtest_df['signal'].shift(1) * backtest_df['daily_ret']

cum_ret = (1 + backtest_df['strategy_ret'].fillna(0)).cumprod()
print(f"\nBacktest 總回報: {cum_ret.iloc[-1]:.1%}")
print(f"最大回撤: {((cum_ret / cum_ret.cummax()) - 1).min():.1%}")
print(f"勝率: {(backtest_df['strategy_ret'] > 0).mean():.1%}")

model.save_model('/Users/gordonlui/.openclaw/workspace/models/yfinance_jd_model.json')
print("\n模型已保存")

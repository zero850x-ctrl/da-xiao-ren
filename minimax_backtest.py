#!/usr/bin/env python3
"""
Minimax 回測系統 - 2%風險 + R/R 1:2 + 圖表
"""
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 參數
TICKER = "9988.HK"
START_DATE = "2022-01-01"
INITIAL_CAPITAL = 100_000
RISK_PER_TRADE = 0.02
MIN_RR_RATIO = 2.0
VOLUME_THRESHOLD = 1.3

print(f"🚀 正在為 {TICKER} 回測...")

df = yf.download(TICKER, start=START_DATE, progress=False)
df.columns = [c[0] for c in df.columns]

# 指標
df['MA34'] = df['Close'].rolling(34).mean()
df['MA8'] = df['Close'].rolling(8).mean()
df['EMA8'] = df['Close'].ewm(span=8, adjust=False).mean()

df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
df['MACD_hist'] = df['MACD'] - df['MACD_signal']

delta = df['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
df['RSI'] = 100 - 100 / (1 + rs)

df['vol_ma'] = df['Volume'].rolling(20).mean()
df['volume_ratio'] = df['Volume'] / df['vol_ma']

tr = pd.concat([df['High']-df['Low'], 
                abs(df['High']-df['Close'].shift()), 
                abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
df['ATR'] = tr.rolling(14).mean()

df = df.dropna().copy()

# 回測
equity = INITIAL_CAPITAL
equity_curve = [equity]
trades = []
in_position = False

for i in range(1, len(df)):
    row = df.iloc[i]
    
    if not in_position:
        if (row['Close'] > row['MA34'] and 
            (row['EMA8'] > row['MA8'] or row['Close'] > row['EMA8']) and 
            row['MACD_hist'] > 0 and 
            row['volume_ratio'] > VOLUME_THRESHOLD and 
            row['RSI'] < 70):
            
            sl_distance = row['ATR'] * 1.8
            sl_price = row['Close'] - sl_distance
            
            reward_needed = sl_distance * MIN_RR_RATIO
            tp_price = row['Close'] + reward_needed
            
            risk_per_share = row['Close'] - sl_price
            if risk_per_share <= 0:
                continue
            
            risk_amount = INITIAL_CAPITAL * RISK_PER_TRADE
            shares = int(risk_amount / risk_per_share)
            if shares < 5:
                continue
            
            in_position = True
            entry_price = row['Close']
            stop_loss = sl_price
            take_profit = tp_price
            position_shares = shares
            
            trades.append({
                'entry_date': row.name.date(),
                'entry': entry_price,
                'sl': stop_loss,
                'tp': take_profit,
                'shares': shares
            })
            
    elif in_position:
        if row['High'] >= take_profit:
            profit = (take_profit - entry_price) * position_shares
            equity += profit
            trades[-1]['exit_date'] = row.name.date()
            trades[-1]['exit'] = take_profit
            trades[-1]['profit'] = profit
            in_position = False
        elif row['Low'] <= stop_loss:
            profit = (stop_loss - entry_price) * position_shares
            equity += profit
            trades[-1]['exit_date'] = row.name.date()
            trades[-1]['exit'] = stop_loss
            trades[-1]['profit'] = profit
            in_position = False
    
    equity_curve.append(equity)

# === 最終報告 ===
completed = [t for t in trades if 'profit' in t]
wins = [t for t in completed if t['profit'] > 0]
win_rate = len(wins) / len(completed) * 100 if completed else 0

print("\n" + "="*50)
print("=== MINIMAX 完整回測結果 ===")
print("="*50)
print(f"股票: {TICKER}")
print(f"期間: {df.index[0].date()} ~ {df.index[-1].date()}")
print(f"初始資金: HKD ${INITIAL_CAPITAL:,.0f}")
print(f"最終資金: HKD ${equity:,.0f}")
print(f"總報酬率: {((equity / INITIAL_CAPITAL) - 1)*100:.2f}%")
print(f"交易次數: {len(completed)}")
print(f"勝率: {win_rate:.1f}%")
print(f"總盈利: HKD ${sum(t.get('profit', 0) for t in completed):,.0f}")

if wins:
    avg_win = sum(t['profit'] for t in wins) / len(wins)
    print(f"平均盈利: HKD ${avg_win:,.0f}")
losses = [t for t in completed if t['profit'] <= 0]
if losses:
    avg_loss = sum(t['profit'] for t in losses) / len(losses)
    print(f"平均虧損: HKD ${avg_loss:,.0f}")

print("\n=== 最近5筆交易 ===")
for t in completed[-5:]:
    p = t.get('profit', 0)
    print(f"{t['entry_date']}: 入 ${t['entry']:.2f} -> 出 ${t['exit']:.2f} | {'✅' if p>0 else '❌'} HKD ${p:,.0f}")

# 畫資金曲線
plt.figure(figsize=(12, 6))
plt.plot(equity_curve, label='資金曲線', color='green')
plt.title(f'{TICKER} - Minimax策略 (2%風險 + R/R 1:2)')
plt.ylabel('資金 (HKD)')
plt.xlabel('交易日')
plt.legend()
plt.grid(True)
plt.savefig(f'backtest_{TICKER.replace(".", "_")}.png', dpi=100)
print(f"\n✅ 圖表已保存: backtest_{TICKER.replace('.', '_')}.png")

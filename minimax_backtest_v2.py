#!/usr/bin/env python3
"""
Minimax v2.0 回測 - Golden 0.618 + Trailing Stop + MACD Exit
"""
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

TICKER = "9988.HK"
START_DATE = "2022-01-01"
INITIAL_CAPITAL = 100_000
RISK_PER_TRADE = 0.02
MIN_RR_RATIO = 2.0
VOLUME_THRESHOLD = 1.3

print(f"🚀 Minimax v2.0 回測啟動 → {TICKER}")

df = yf.download(TICKER, start=START_DATE, progress=False)
df.columns = [c[0] for c in df.columns]

# === 指標 ===
df['MA34'] = df['Close'].rolling(34).mean()
df['MA8'] = df['Close'].rolling(8).mean()
df['EMA8'] = df['Close'].ewm(span=8, adjust=False).mean()

df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
df['MACD_hist'] = df['MACD'] - df['MACD_signal']

delta = df['Close'].diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = -delta.where(delta < 0, 0).rolling(14).mean()
rs = gain / loss
df['RSI'] = 100 - 100 / (1 + rs)

df['vol_ma'] = df['Volume'].rolling(20).mean()
df['volume_ratio'] = df['Volume'] / df['vol_ma']

tr = pd.concat([df['High']-df['Low'], 
                abs(df['High']-df['Close'].shift()), 
                abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
df['ATR'] = tr.rolling(14).mean()

# Golden 0.618
df['swing_high'] = df['High'].rolling(55).max()
df['swing_low'] = df['Low'].rolling(55).min()
df['golden_0.618_support'] = df['swing_high'] - (df['swing_high'] - df['swing_low']) * 0.618

df = df.dropna().copy()

# === 回測 v2.0 ===
equity = INITIAL_CAPITAL
equity_curve = [equity]
trades = []
in_position = False
position_shares = 0
entry_price = 0
stop_loss = 0
take_profit_1 = 0
partial_sold = False

for i in range(1, len(df)):
    row = df.iloc[i]
    
    if not in_position:
        near_golden = abs(row['Close'] - row['golden_0.618_support']) < row['ATR'] * 1.5
        
        if (row['Close'] > row['MA34'] and 
            (row['EMA8'] > row['MA8'] or row['Close'] > row['EMA8']) and 
            row['MACD_hist'] > 0 and 
            row['volume_ratio'] > VOLUME_THRESHOLD and 
            row['RSI'] < 70 and 
            near_golden):
            
            sl_distance = row['ATR'] * 1.8
            sl_price = row['Close'] - sl_distance
            
            reward_needed = sl_distance * MIN_RR_RATIO
            tp_price = row['Close'] + reward_needed
            
            risk_per_share = row['Close'] - sl_price
            if risk_per_share <= 0: continue
            
            risk_amount = INITIAL_CAPITAL * RISK_PER_TRADE
            shares = int(risk_amount / risk_per_share)
            if shares < 5: continue
            
            in_position = True
            entry_price = row['Close']
            stop_loss = sl_price
            take_profit_1 = tp_price
            position_shares = shares
            partial_sold = False
            
            trades.append({
                'entry_date': row.name.date(),
                'entry': entry_price,
                'sl': stop_loss,
                'tp1': take_profit_1,
                'shares': shares
            })
            
    else:
        # Trailing Stop
        trailing_sl = row['Close'] - row['ATR'] * 2.0
        stop_loss = max(stop_loss, trailing_sl)
        
        exit_price = None
        exit_reason = ""
        
        # 1:2 先出50%
        if row['High'] >= take_profit_1 and not partial_sold:
            sell_shares = position_shares // 2
            profit = (take_profit_1 - entry_price) * sell_shares
            equity += profit
            position_shares -= sell_shares
            partial_sold = True
            trades[-1]['partial_exit'] = take_profit_1
            trades[-1]['partial_profit'] = profit
        
        # Trailing Stop 出場
        if row['Low'] <= stop_loss and position_shares > 0:
            exit_price = stop_loss
            exit_reason = "Trailing Stop"
        
        # MACD死叉 + 價格跌破EMA8 出場
        elif partial_sold and row['MACD_hist'] < 0 and row['Close'] < row['EMA8']:
            exit_price = row['Close']
            exit_reason = "MACD死叉"
        
        if exit_price is not None and position_shares > 0:
            profit = (exit_price - entry_price) * position_shares
            equity += profit
            trades[-1]['exit_date'] = row.name.date()
            trades[-1]['exit'] = exit_price
            trades[-1]['profit'] = profit
            trades[-1]['exit_reason'] = exit_reason
            in_position = False
            position_shares = 0
    
    equity_curve.append(equity)

# === v2.0 完整報告 ===
completed = [t for t in trades if 'profit' in t]
wins = [t for t in completed if t.get('profit', 0) > 0]
losses = [t for t in completed if t.get('profit', 0) <= 0]
win_rate = len(wins) / len(completed) * 100 if completed else 0
total_profit = sum(t.get('profit', 0) for t in completed)
avg_win = sum(t.get('profit', 0) for t in wins) / len(wins) if wins else 0
avg_loss = sum(t.get('profit', 0) for t in losses) / len(losses) if losses else 0

print("\n" + "="*50)
print("=== MINIMAX v2.0 完整回測結果 ===")
print("="*50)
print(f"股票: {TICKER}")
print(f"期間: {df.index[0].date()} ~ {df.index[-1].date()}")
print(f"初始資金: HKD ${INITIAL_CAPITAL:,.0f} → 最終資金: HKD ${equity:,.0f}")
print(f"總報酬率: {((equity / INITIAL_CAPITAL) - 1)*100:.2f}%")
print(f"交易次數: {len(completed)}")
print(f"勝率: {win_rate:.1f}%")
if avg_loss != 0:
    print(f"盈虧比: {abs(avg_win/avg_loss):.2f}")
print(f"期望值/筆: HKD ${total_profit/len(completed):,.0f}" if completed else "")

# Max drawdown
min_equity = min(equity_curve)
max_dd = (min_equity / INITIAL_CAPITAL - 1) * 100
print(f"最大回撤: {max_dd:.1f}%")

print("\n=== 最近5筆交易 ===")
for t in completed[-5:]:
    print(f"{t['entry_date']}: ${t['entry']:.2f} -> ${t.get('exit', 0):.2f} | {t.get('exit_reason', '')} | {'✅' if t['profit']>0 else '❌'} ${t['profit']:,.0f}")

# Plot
plt.figure(figsize=(12, 6))
plt.plot(equity_curve, color='green', linewidth=2)
plt.title(f'{TICKER} - Minimax v2.0 (Golden 0.618 + Trailing Stop)')
plt.ylabel('資金 (HKD)')
plt.xlabel('交易日')
plt.grid(True)
plt.savefig(f'backtest_v2_{TICKER.replace(".", "_")}.png', dpi=100)
print(f"\n✅ 圖表已保存: backtest_v2_{TICKER.replace('.', '_')}.png")

#!/usr/bin/env python3
"""
Minimax v2.0 交易執行器
基於 Golden 0.618 + Trailing Stop + MACD Exit
"""
import yfinance as yf
import pandas as pd
import numpy as np
from futu import OpenSecTradeContext, TrdEnv, OrderType
import sys
import json

# === 參數 ===
TICKER = sys.argv[1] if len(sys.argv) > 1 else "9988.HK"
TRADING_MODE = "SIMULATE"  # SIMULATE 或 REAL
RISK_PER_TRADE = 0.02
MIN_RR_RATIO = 2.0
VOLUME_THRESHOLD = 1.3

def get_indicators(ticker):
    """獲取技術指標"""
    code = ticker.replace('.HK', '')
    df = yf.download(ticker, period="3mo", progress=False)
    if df is None or len(df) < 50:
        return None
    df.columns = [c[0] for c in df.columns]
    
    close = df['Close']
    df['MA34'] = close.rolling(34).mean()
    df['MA8'] = close.rolling(8).mean()
    df['EMA8'] = close.ewm(span=8, adjust=False).mean()
    df['MACD'] = close.ewm(span=12).mean() - close.ewm(span=26).mean()
    df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']
    
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + gain/loss))
    
    df['vol_ma'] = df['Volume'].rolling(20).mean()
    df['volume_ratio'] = df['Volume'] / df['vol_ma']
    
    tr = pd.concat([df['High']-df['Low'], 
                    abs(df['High']-df['Close'].shift()), 
                    abs(df['Low']-df['Close'].shift())], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(14).mean()
    
    df['swing_high'] = df['High'].rolling(55).max()
    df['swing_low'] = df['Low'].rolling(55).min()
    df['golden_0.618_support'] = df['swing_high'] - (df['swing_high'] - df['swing_low']) * 0.618
    
    return df.iloc[-1]

def check_signal(row):
    """檢查是否符合買入信號"""
    if row is None:
        return False, "No data"
    
    near_golden = abs(row['Close'] - row['golden_0.618_support']) < row['ATR'] * 1.5
    
    conditions = {
        'MA34': row['Close'] > row['MA34'],
        'EMA8/MA8': row['EMA8'] > row['MA8'] or row['Close'] > row['EMA8'],
        'MACD_hist': row['MACD_hist'] > 0,
        'volume_ratio': row['volume_ratio'] > VOLUME_THRESHOLD,
        'RSI': row['RSI'] < 70,
        'near_golden': near_golden
    }
    
    all_met = all(conditions.values())
    met_list = [k for k, v in conditions.items() if v]
    
    if all_met:
        return True, f"BUY: {', '.join(met_list)}"
    else:
        missing = [k for k, v in conditions.items() if not v]
        return False, f"HOLD: missing {', '.join(missing)}"

def calculate_position(current_price, atr, total_assets):
    """計算倉位大小"""
    risk_amount = total_assets * RISK_PER_TRADE
    sl_distance = atr * 1.8
    sl_price = current_price - sl_distance
    risk_per_share = current_price - sl_price
    
    if risk_per_share <= 0:
        return 0, 0, 0
    
    shares = int(risk_amount / risk_per_share)
    # Round to lot size (100 shares)
    shares = (shares // 100) * 100
    
    return shares, sl_price, sl_distance

def main():
    print(f"🚀 Minimax v2.0 交易信號檢查: {TICKER}")
    print("=" * 50)
    
    # Get indicators
    row = get_indicators(TICKER)
    if row is None:
        print(f"❌ 無法獲取數據: {TICKER}")
        return
    
    current_price = row['Close']
    print(f"現價: ${current_price:.2f}")
    print(f"RSI: {row['RSI']:.1f}")
    print(f"MACD_hist: {row['MACD_hist']:.2f}")
    print(f"Volume_ratio: {row['volume_ratio']:.2f}")
    print(f"ATR: ${row['ATR']:.2f}")
    print(f"Golden 0.618: ${row['golden_0.618_support']:.2f}")
    
    # Check signal
    signal, reason = check_signal(row)
    print(f"\n信號: {reason}")
    
    if signal:
        print(f"\n✅ 符合買入條件!")
        
        # Get account balance
        if TRADING_MODE == "SIMULATE":
            trd_ctx = OpenSecTradeContext(host='127.0.0.1', port=11111)
            ret, acc = trd_ctx.accinfo_query(trd_env=TrdEnv.SIMULATE)
            if ret == 0:
                total_assets = acc['total_assets'].iloc[0]
                print(f"模擬倉總資產: HKD {total_assets:,.0f}")
                
                # Calculate position
                shares, sl_price, sl_dist = calculate_position(current_price, row['ATR'], total_assets)
                print(f"\n倉位計算:")
                print(f"  可買: {shares}股 ({shares//100}手)")
                print(f"  止蝕位: ${sl_price:.2f}")
                print(f"  風險: HKD {shares * sl_dist:,.0f}")
                
                # Save signal
                signal_data = {
                    "ticker": TICKER,
                    "signal": "BUY",
                    "price": current_price,
                    "shares": shares,
                    "stop_loss": sl_price,
                    "reason": reason,
                    "timestamp": pd.Timestamp.now().isoformat()
                }
                with open('/Users/gordonlui/.openclaw/workspace/trading_reports/minimax_signal.json', 'w') as f:
                    json.dump(signal_data, f, indent=2)
                print(f"\n✅ 信號已保存")
            trd_ctx.close()
    else:
        print(f"\n❌ 不符合買入條件，保持觀望")

if __name__ == "__main__":
    main()

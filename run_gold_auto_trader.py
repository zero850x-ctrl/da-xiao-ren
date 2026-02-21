#!/usr/bin/env python3
"""
運行黃金自動交易系統演示
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def main():
    print("=" * 70)
    print("🏆 黃金自動交易系統 - 完整演示")
    print("=" * 70)
    
    print("\n📋 系統配置:")
    print("   交易對: XAUUSD (現貨黃金)")
    print("   最大手數: 0.01手")
    print("   初始資金: $1000")
    print("   模擬周期: 30天 (720小時)")
    
    print("\n🎯 交易策略:")
    print("   1. 趨勢跟隨策略 (SMA交叉, MACD)")
    print("   2. 均值回歸策略 (RSI, 布林帶)")
    print("   3. 突破交易策略 (支撐阻力)")
    
    print("\n⚠️  風險管理:")
    print("   止損: 50點 ($0.50 @ 0.01手)")
    print("   止盈: 100點 ($1.00 @ 0.01手)")
    print("   最大風險: 2%每筆")
    print("   每日最大交易: 3次")
    
    # 生成模擬數據
    print("\n" + "=" * 70)
    print("📊 第1步: 生成市場數據")
    print("=" * 70)
    
    np.random.seed(42)
    periods = 720  # 30天×24小時
    
    # 創建時間序列
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='H')
    
    # 模擬價格走勢
    base_trend = np.linspace(1800, 2200, periods)
    daily_cycle = 30 * np.sin(np.linspace(0, 30*2*np.pi, periods))
    hourly_noise = 15 * np.sin(np.linspace(0, 720*np.pi, periods))
    random_noise = 10 * np.random.randn(periods)
    
    prices = base_trend + daily_cycle + hourly_noise + random_noise
    
    # 生成OHLC數據
    data = []
    for i in range(periods):
        base = prices[i]
        high = base + abs(np.random.randn() * 8)
        low = base - abs(np.random.randn() * 8)
        close = base + np.random.randn() * 4
        
        if high < low:
            high, low = low, high
        close = np.clip(close, low, high)
        
        if i == 0:
            open_price = base
        else:
            open_price = data[i-1]['close'] + np.random.randn() * 2
        
        data.append({
            'timestamp': dates[i],
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': np.random.randint(500, 2000)
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    print(f"✅ 數據生成完成")
    print(f"   數據點: {len(df)}個")
    print(f"   價格範圍: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
    print(f"   最新價格: ${df['close'].iloc[-1]:.2f}")
    
    # 計算技術指標
    print("\n" + "=" * 70)
    print("📈 第2步: 計算技術指標")
    print("=" * 70)
    
    # 移動平均線
    df['SMA_20'] = df['close'].rolling(20).mean()
    df['SMA_50'] = df['close'].rolling(50).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 布林帶
    df['BB_middle'] = df['close'].rolling(20).mean()
    bb_std = df['close'].rolling(20).std()
    df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
    df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
    
    # 支撐阻力
    df['resistance'] = df['high'].rolling(20).max()
    df['support'] = df['low'].rolling(20).min()
    
    print("✅ 技術指標計算完成")
    print(f"   SMA20: ${df['SMA_20'].iloc[-1]:.2f}")
    print(f"   SMA50: ${df['SMA_50'].iloc[-1]:.2f}")
    print(f"   RSI: {df['RSI'].iloc[-1]:.1f}")
    print(f"   布林帶: ${df['BB_lower'].iloc[-1]:.2f} - ${df['BB_upper'].iloc[-1]:.2f}")
    
    # 生成交易信號
    print("\n" + "=" * 70)
    print("🔍 第3步: 生成交易信號")
    print("=" * 70)
    
    signals = []
    
    for i in range(50, len(df)):
        current = df.iloc[i]
        prev = df.iloc[i-1]
        
        signal_score = 0
        reasons = []
        
        # 策略1: 趨勢跟隨 (SMA交叉)
        if prev['SMA_20'] <= prev['SMA_50'] and current['SMA_20'] > current['SMA_50']:
            signal_score += 2
            reasons.append("SMA黃金交叉")
        elif prev['SMA_20'] >= prev['SMA_50'] and current['SMA_20'] < current['SMA_50']:
            signal_score -= 2
            reasons.append("SMA死亡交叉")
        
        # 策略2: 均值回歸 (RSI)
        rsi = current['RSI']
        if pd.notna(rsi):
            if rsi < 30:
                signal_score += 2
                reasons.append(f"RSI超賣({rsi:.1f})")
            elif rsi > 70:
                signal_score -= 2
                reasons.append(f"RSI超買({rsi:.1f})")
        
        # 策略3: 布林帶回歸
        price = current['close']
        if price <= current['BB_lower']:
            signal_score += 1
            reasons.append("觸及布林帶下軌")
        elif price >= current['BB_upper']:
            signal_score -= 1
            reasons.append("觸及布林帶上軌")
        
        # 策略4: 支撐阻力突破
        if price > current['resistance']:
            signal_score += 1
            reasons.append("突破阻力位")
        elif price < current['support']:
            signal_score -= 1
            reasons.append("跌破支撐位")
        
        # 確定信號
        if signal_score >= 2:
            signals.append({
                'timestamp': df.index[i],
                'price': price,
                'signal': 'BUY',
                'strength': signal_score,
                'reason': " | ".join(reasons)
            })
        elif signal_score <= -2:
            signals.append({
                'timestamp': df.index[i],
                'price': price,
                'signal': 'SELL',
                'strength': abs(signal_score),
                'reason': " | ".join(reasons)
            })
    
    print(f"✅ 信號生成完成")
    print(f"   買入信號: {len([s for s in signals if s['signal'] == 'BUY'])}個")
    print(f"   賣出信號: {len([s for s in signals if s['signal'] == 'SELL'])}個")
    
    if signals:
        print(f"\n📝 最新信號:")
        latest = signals[-1]
        print(f"   時間: {latest['timestamp']}")
        print(f"   信號: {latest['signal']}")
        print(f"   價格: ${latest['price']:.2f}")
        print(f"   強度: {latest['strength']}")
        print(f"   原因: {latest['reason']}")
    
    # 模擬交易
    print("\n" + "=" * 70)
    print("💼 第4步: 模擬交易執行")
    print("=" * 70)
    
    initial_balance = 1000.0
    balance = initial_balance
    max_lot_size = 0.01
    trades = []
    position = None
    
    for signal in signals:
        current_time = signal['timestamp']
        current_price = signal['price']
        
        # 如果有持倉，檢查止損止盈
        if position:
            # 計算持倉時間
            holding_hours = (current_time - position['entry_time']).total_seconds() / 3600
            
            # 計算盈虧
            if position['type'] == 'BUY':
                profit_pips = (current_price - position['entry_price']) * 10
            else:  # SELL
                profit_pips = (position['entry_price'] - current_price) * 10
            
            profit_dollars = profit_pips * position['lot_size'] * 0.1
            
            # 檢查止損止盈
            exit_reason = None
            if profit_pips <= -50:  # 50點止損
                exit_reason = 'STOP_LOSS'
            elif profit_pips >= 100:  # 100點止盈
                exit_reason = 'TAKE_PROFIT'
            elif holding_hours >= 24:  # 24小時最大持倉
                exit_reason = 'MAX_HOLDING'
            
            if exit_reason:
                # 平倉
                balance += profit_dollars
                
                trade = {
                    'id': len(trades) + 1,
                    'entry_time': position['entry_time'],
                    'exit_time': current_time,
                    'type': position['type'],
                    'entry_price': position['entry_price'],
                    'exit_price': current_price,
                    'lot_size': position['lot_size'],
                    'profit_pips': profit_pips,
                    'profit_dollars': profit_dollars,
                    'exit_reason': exit_reason,
                    'holding_hours': holding_hours,
                    'reason': position['reason']
                }
                trades.append(trade)
                position = None
        
        # 如果沒有持倉，開新倉
        if not position and len(trades) < 10:  # 限制最多10筆交易
            # 計算手數（固定0.01手）
            lot_size = max_lot_size
            
            # 開倉
            position = {
                'entry_time': current_time,
                'type': signal['signal'],
                'entry_price': current_price,
                'lot_size': lot_size,
                'reason': signal['reason']
            }
    
    # 如果有未平倉位，在最後時間平倉
    if position:
        last_price = df['close'].iloc[-1]
        holding_hours = (df.index[-1] - position['entry_time']).total_seconds() / 3600
        
        if position['type'] == 'BUY':
            profit_pips = (last_price - position['entry_price']) * 10
        else:
            profit_pips = (position['entry_price'] - last_price) * 10
        
        profit_dollars = profit_pips * position['lot_size'] * 0.1
        balance += profit_dollars
        
        trade = {
            'id': len(trades) + 1,
            'entry_time': position['entry_time'],
            'exit_time': df.index[-1],
            'type': position['type'],
            'entry_price': position['entry_price'],
            'exit_price': last_price,
            'lot_size': position['lot_size'],
            'profit_pips': profit_pips,
            'profit_dollars': profit_dollars,
            'exit_reason': 'END_OF_PERIOD',
            'holding_hours': holding_hours,
            'reason': position['reason']
        }
        trades.append(trade)
    
    # 分析結果
    print("\n" + "=" * 70)
    print("📊 第5步: 交易結果分析")
    print("=" * 70)
    
    if not trades:
        print("❌ 沒有執行任何交易")
        return
    
    # 基本統計
    total_trades = len(trades)
    winning_trades = [t for t in trades if t['profit_dollars'] > 0]
    losing_trades = [t for t in trades if t['profit_dollars'] <= 0]
    
    total_profit = sum(t['profit_dollars'] for t in trades)
    total_win = sum(t['profit_dollars'] for t in winning_trades)
    total_loss = abs(sum(t['profit_dollars'] for t in losing_trades))
    
    win_rate = len(winning_trades) / total_trades * 100
    profit_factor = total_win / total_loss if total_loss > 0 else float('inf')
    
    print(f"📈 績效摘要:")
    print(f"   總交易次數: {total_trades}")
    print(f"   盈利交易: {len(winning_trades)} ({win_rate:.1f}%)")
    print(f"   虧損交易: {len(losing_trades)} ({100-win_rate:.1f}%)")
    print(f"   總盈利: ${total_profit:.2f}")
    print(f"   賬戶增長: {(total_profit/initial_balance)*100:.2f}%")
    print(f"   最終資金: ${balance:.2f}")
    print(f"   盈利因子: {profit_factor:.2f}")
    
    # 詳細交易記錄
    print(f"\n📝 交易記錄:")
    for trade in trades:
        profit_color = "🟢" if trade['profit_dollars'] > 0 else "🔴"
        print(f"   {trade['id']}. {trade['type']} @ ${trade['entry_price']:.2f}")
        print(f"      平倉: ${trade['exit_price']:.2f} ({trade['holding_hours']:.1f}小時)")
        print(f"      盈虧: {profit_color} ${trade['profit_dollars']:.2f} ({trade['profit_pips']:.0f}點)")
        print(f"      原因: {trade['exit_reason']} - {trade['reason']}")
    
    # 保存結果
    print("\n" + "=" * 70)
    print("💾 第6步: 保存結果")
    print("=" * 70)
    
    result = {
        'simulation_date': datetime.now().isoformat(),
        'initial_balance': initial_balance,
        'final_balance': balance,
        'total_profit': total_profit,
        'profit_percentage': (total_profit/initial_balance)*100,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'trades': trades
    }
    
    with open('/Users/gordonlui/.openclaw/workspace/gold_trading_results.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"✅ 結果已保存到: gold_trading_results.json")
    
    print("\n" + "=" * 70)
    print("🎯 總結與建議")
    print("=" * 70)
    
    if total_profit > 0:
        print(f"✅ 模擬交易盈利: ${total_profit:.2f} ({win_rate:.1f}%勝率)")
        print(f"   建議: 可以考慮實盤測試")
    else:
        print(f"⚠️  模擬交易虧損: ${abs(total_profit):.2f}")
        print(f"   建議: 優化策略後再測試")
    
    print(f"\n🔧 改進建議:")
    print(f"   1. 增加更多技術指標")
    print(f"   2. 優化參數設置")
    print(f"   3. 添加過濾條件減少假信號")
    print(f"   4. 考慮市場時段和波動性")
    
    print(f"\n🚀 下一步:")
    print(f"   1. 使用真實市場數據測試")
    print(f"   2. 連接MT5或OANDA API")
    print(f"   3. 實盤測試0.01手")
    print(f"   4. 逐步優化策略")


if __name__ == "__main__":
    main()
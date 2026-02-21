#!/usr/bin/env python3
"""
策略參數優化器 - 第二部分
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def main():
    print("=" * 70)
    print("🔧 黃金交易策略參數優化")
    print("=" * 70)
    
    print("\n🎯 優化目標:")
    print("   1. 最大化盈利因子")
    print("   2. 最大化勝率")
    print("   3. 最小化最大回撤")
    print("   4. 穩定0.01手交易")
    
    print("\n📊 測試配置:")
    print("   測試周期: 90天 (2160小時)")
    print("   初始資金: $1000")
    print("   最大手數: 0.01手")
    print("   參數組合: 50種")
    
    # 生成測試數據
    print("\n" + "=" * 70)
    print("📈 生成測試數據")
    print("=" * 70)
    
    np.random.seed(42)
    periods = 90 * 24  # 90天×24小時
    
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='h')
    
    # 生成更真實的價格序列
    base_trend = np.linspace(1800, 2200, periods)
    
    # 多重周期
    trend_component = 0.0001 * np.arange(periods)  # 長期趨勢
    seasonal = 50 * np.sin(np.linspace(0, 6*np.pi, periods))  # 季節性
    cyclical = 30 * np.sin(np.linspace(0, 30*np.pi, periods))  # 周期性
    noise = 20 * np.random.randn(periods)  # 隨機噪聲
    
    prices = base_trend + trend_component + seasonal + cyclical + noise
    
    # 生成OHLC
    data = []
    for i in range(periods):
        base = prices[i]
        volatility = 0.002 + 0.001 * np.sin(i/100)  # 動態波動
        
        high = base * (1 + abs(np.random.normal(0, volatility)))
        low = base * (1 - abs(np.random.normal(0, volatility)))
        close = base * (1 + np.random.normal(0, volatility/2))
        
        if high < low:
            high, low = low, high
        close = np.clip(close, low, high)
        
        if i == 0:
            open_price = base
        else:
            open_price = data[i-1]['close'] * (1 + np.random.normal(0, volatility/3))
        
        data.append({
            'timestamp': dates[i],
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': np.random.randint(800, 2500)
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    print(f"✅ 生成 {len(df)} 小時數據")
    print(f"   價格範圍: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
    print(f"   最新價格: ${df['close'].iloc[-1]:.2f}")
    
    # 定義參數測試組合
    print("\n" + "=" * 70)
    print("🔍 測試參數組合")
    print("=" * 70)
    
    param_combinations = []
    
    # 生成參數組合
    base_params = {
        'use_sma': True,
        'use_rsi': True,
        'use_bb': True,
        'use_macd': False,
        'max_lot_size': 0.01,
        'initial_balance': 1000,
        'max_trades': 50,
        'max_holding_hours': 72
    }
    
    # 測試不同的參數組合
    test_cases = [
        # 案例1: 保守策略
        {
            'name': '保守策略',
            'sma_short': 20,
            'sma_long': 50,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'bb_period': 20,
            'bb_std': 2.0,
            'stop_loss_pips': 40,
            'take_profit_pips': 80,
            'signal_threshold': 0.6,
            'sma_weight': 0.3,
            'rsi_weight': 0.4,
            'bb_weight': 0.3
        },
        # 案例2: 積極策略
        {
            'name': '積極策略',
            'sma_short': 15,
            'sma_long': 40,
            'rsi_period': 10,
            'rsi_oversold': 25,
            'rsi_overbought': 75,
            'bb_period': 15,
            'bb_std': 1.5,
            'stop_loss_pips': 60,
            'take_profit_pips': 120,
            'signal_threshold': 0.4,
            'sma_weight': 0.4,
            'rsi_weight': 0.3,
            'bb_weight': 0.3
        },
        # 案例3: 平衡策略
        {
            'name': '平衡策略',
            'sma_short': 20,
            'sma_long': 50,
            'rsi_period': 14,
            'rsi_oversold': 35,
            'rsi_overbought': 65,
            'bb_period': 20,
            'bb_std': 2.0,
            'stop_loss_pips': 50,
            'take_profit_pips': 100,
            'signal_threshold': 0.5,
            'sma_weight': 0.35,
            'rsi_weight': 0.35,
            'bb_weight': 0.3
        },
        # 案例4: 趨勢跟隨
        {
            'name': '趨勢跟隨',
            'sma_short': 10,
            'sma_long': 30,
            'rsi_period': 20,
            'rsi_oversold': 40,
            'rsi_overbought': 60,
            'bb_period': 25,
            'bb_std': 2.5,
            'stop_loss_pips': 80,
            'take_profit_pips': 160,
            'signal_threshold': 0.5,
            'sma_weight': 0.5,
            'rsi_weight': 0.3,
            'bb_weight': 0.2
        },
        # 案例5: 均值回歸
        {
            'name': '均值回歸',
            'sma_short': 25,
            'sma_long': 60,
            'rsi_period': 10,
            'rsi_oversold': 20,
            'rsi_overbought': 80,
            'bb_period': 15,
            'bb_std': 1.5,
            'stop_loss_pips': 30,
            'take_profit_pips': 60,
            'signal_threshold': 0.7,
            'sma_weight': 0.2,
            'rsi_weight': 0.5,
            'bb_weight': 0.3
        }
    ]
    
    results = []
    
    for case in test_cases:
        print(f"\n🔍 測試: {case['name']}")
        print(f"   參數: SMA{case['sma_short']}/{case['sma_long']}, "
              f"RSI{case['rsi_period']}({case['rsi_oversold']}/{case['rsi_overbought']}), "
              f"止損{case['stop_loss_pips']}/止盈{case['take_profit_pips']}")
        
        # 合併參數
        params = {**base_params, **case}
        
        # 計算技術指標
        df_test = df.copy()
        
        # SMA
        df_test['SMA_short'] = df_test['close'].rolling(params['sma_short']).mean()
        df_test['SMA_long'] = df_test['close'].rolling(params['sma_long']).mean()
        
        # RSI
        delta = df_test['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(params['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(params['rsi_period']).mean()
        rs = gain / loss
        df_test['RSI'] = 100 - (100 / (1 + rs))
        
        # 布林帶
        df_test['BB_middle'] = df_test['close'].rolling(params['bb_period']).mean()
        bb_std = df_test['close'].rolling(params['bb_period']).std()
        df_test['BB_upper'] = df_test['BB_middle'] + (bb_std * params['bb_std'])
        df_test['BB_lower'] = df_test['BB_middle'] - (bb_std * params['bb_std'])
        
        # 生成信號
        signals = []
        for i in range(50, len(df_test)):
            current = df_test.iloc[i]
            prev = df_test.iloc[i-1]
            
            score = 0.0
            
            # SMA信號
            if params['use_sma']:
                if prev['SMA_short'] <= prev['SMA_long'] and current['SMA_short'] > current['SMA_long']:
                    score += params['sma_weight']
                elif prev['SMA_short'] >= prev['SMA_long'] and current['SMA_short'] < current['SMA_long']:
                    score -= params['sma_weight']
            
            # RSI信號
            if params['use_rsi']:
                rsi = current['RSI']
                if pd.notna(rsi):
                    if rsi < params['rsi_oversold']:
                        score += params['rsi_weight']
                    elif rsi > params['rsi_overbought']:
                        score -= params['rsi_weight']
            
            # 布林帶信號
            if params['use_bb']:
                price = current['close']
                if price <= current['BB_lower']:
                    score += params['bb_weight']
                elif price >= current['BB_upper']:
                    score -= params['bb_weight']
            
            # 確定信號
            if score >= params['signal_threshold']:
                signals.append({
                    'timestamp': df_test.index[i],
                    'price': current['close'],
                    'signal': 'BUY',
                    'strength': score
                })
            elif score <= -params['signal_threshold']:
                signals.append({
                    'timestamp': df_test.index[i],
                    'price': current['close'],
                    'signal': 'SELL',
                    'strength': abs(score)
                })
        
        # 模擬交易
        initial_balance = 1000.0
        balance = initial_balance
        trades = []
        position = None
        
        for signal in signals[:params['max_trades']]:  # 限制交易次數
            current_time = signal['timestamp']
            current_price = signal['price']
            
            # 檢查持倉
            if position:
                # 計算盈虧
                if position['type'] == 'BUY':
                    profit_pips = (current_price - position['entry_price']) * 10
                else:
                    profit_pips = (position['entry_price'] - current_price) * 10
                
                # 檢查止損止盈
                exit_reason = None
                if profit_pips <= -params['stop_loss_pips']:
                    exit_reason = 'STOP_LOSS'
                elif profit_pips >= params['take_profit_pips']:
                    exit_reason = 'TAKE_PROFIT'
                
                if exit_reason:
                    # 平倉
                    profit_amount = profit_pips * position['lot_size'] * 0.1
                    balance += profit_amount
                    
                    trade = {
                        'entry_time': position['entry_time'],
                        'exit_time': current_time,
                        'type': position['type'],
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'lot_size': position['lot_size'],
                        'profit_pips': profit_pips,
                        'profit_amount': profit_amount,
                        'exit_reason': exit_reason
                    }
                    trades.append(trade)
                    position = None
            
            # 開新倉
            if not position:
                # 計算手數（考慮信號強度）
                base_lot = params['max_lot_size']
                strength = signal['strength']
                lot_size = min(base_lot * strength * 2, base_lot)
                lot_size = max(0.01, lot_size)
                
                position = {
                    'entry_time': current_time,
                    'type': signal['signal'],
                    'entry_price': current_price,
                    'lot_size': lot_size,
                    'signal_strength': strength
                }
        
        # 評估表現
        if trades:
            winning_trades = [t for t in trades if t['profit_amount'] > 0]
            losing_trades = [t for t in trades if t['profit_amount'] <= 0]
            
            total_profit = sum(t['profit_amount'] for t in trades)
            total_win = sum(t['profit_amount'] for t in winning_trades)
            total_loss = abs(sum(t['profit_amount'] for t in losing_trades))
            
            win_rate = len(winning_trades) / len(trades) * 100
            profit_percentage = (total_profit / initial_balance) * 100
            profit_factor = total_win / total_loss if total_loss > 0 else float('inf')
            
            # 計算最大回撤
            cumulative = np.cumsum([t['profit_amount'] for t in trades])
            running_max = np.maximum.accumulate(cumulative)
            drawdowns = running_max - cumulative
            max_drawdown = drawdowns.max() if len(drawdowns) > 0 else 0
            
            # 計算綜合評分
            score = (win_rate * 0.3 + 
                    profit_percentage * 0.4 + 
                    (profit_factor if profit_factor < 10 else 10) * 0.2 -
                    (max_drawdown / initial_balance * 100) * 0.1)
        else:
            win_rate = 0
            total_profit = 0
            profit_percentage = 0
            profit_factor = 0
            max_drawdown = 0
            score = 0
        
        result = {
            'strategy_name': case['name'],
            'parameters': params,
            'performance': {
                'total_trades': len(trades),
                'win_rate': win_rate,
                'total_profit': total_profit,
                'profit_percentage': profit_percentage,
                'profit_factor': profit_factor,
                'max_drawdown': max_drawdown,
                'final_balance': balance,
                'score': score
            },
            'trades_count': len(trades)
        }
        
        results.append(result)
        
        print(f"   交易次數: {len(trades)}")
        print(f"   勝率: {win_rate:.1f}%")
        print(f"   盈利: ${total_profit:.2f} ({profit_percentage:.2f}%)")
        print(f"   盈利因子: {profit_factor:.2f}")
        print(f"   最大回撤: ${max_drawdown:.2f}")
        print(f"   綜合評分: {score:.2f}")
    
    # 找出最佳策略
    print("\n" + "=" * 70)
    print("🏆 最佳策略評選")
    print("=" * 70)
    
    best_result = max(results, key=lambda x: x['performance']['score'])
    
    print(f"\n🎯 最佳策略: {best_result['strategy_name']}")
    print(f"   綜合評分: {best_result['performance']['score']:.2f}")
    print(f"   盈利: ${best_result['performance']['total_profit']:.2f}")
    print(f"   勝率: {best_result['performance']['win_rate']:.1f}%")
    print(f"   盈利因子: {best_result['performance']['profit_factor']:.2f}")
    
    print(f"\n📋 最佳參數:")
    params = best_result['parameters']
    print(f"   SMA: {params['sma_short']}/{params['sma_long']}")
    print(f"   RSI: {params['rsi_period']} ({params['rsi_oversold']}/{params['rsi_overbought']})")
    print(f"   布林帶: {params['bb_period']}期, {params['bb_std']}倍標準差")
    print(f"   止損/止盈: {params['stop_loss_pips']}/{params['take_profit_pips']}點")
    print(f"   信號閾值: {params['signal_threshold']}")
    print(f"   權重: SMA{params['sma_weight']}, RSI{params['rsi_weight']}, BB{params['bb_weight']}")
    
    # 保存結果
    print("\n" + "=" * 70)
    print("💾 保存優化結果")
    print("=" * 70)
    
    output = {
        'optimization_date': datetime.now().isoformat(),
        'test_period_days': 90,
        'initial_balance': 1000,
        'max_lot_size': 0.01,

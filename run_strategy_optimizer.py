#!/usr/bin/env python3
"""
運行策略優化器 - 簡化版本
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def main():
    print("=" * 70)
    print("🔧 黃金交易策略參數優化 (0.01手)")
    print("=" * 70)
    
    # 生成測試數據
    print("\n📊 生成90天測試數據...")
    np.random.seed(42)
    periods = 90 * 24
    
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='h')
    
    # 生成價格
    base_trend = np.linspace(1800, 2200, periods)
    seasonal = 50 * np.sin(np.linspace(0, 6*np.pi, periods))
    noise = 20 * np.random.randn(periods)
    prices = base_trend + seasonal + noise
    
    # 創建DataFrame
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
            'close': close
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    print(f"✅ 數據生成完成: {len(df)}小時")
    
    # 測試策略
    strategies = [
        {
            'name': '保守策略',
            'sma_short': 20,
            'sma_long': 50,
            'rsi_period': 14,
            'rsi_low': 30,
            'rsi_high': 70,
            'stop_loss': 50,
            'take_profit': 100,
            'threshold': 0.6
        },
        {
            'name': '平衡策略',
            'sma_short': 15,
            'sma_long': 40,
            'rsi_period': 10,
            'rsi_low': 25,
            'rsi_high': 75,
            'stop_loss': 60,
            'take_profit': 120,
            'threshold': 0.5
        },
        {
            'name': '積極策略',
            'sma_short': 10,
            'sma_long': 30,
            'rsi_period': 7,
            'rsi_low': 20,
            'rsi_high': 80,
            'stop_loss': 80,
            'take_profit': 160,
            'threshold': 0.4
        }
    ]
    
    results = []
    
    for strategy in strategies:
        print(f"\n🔍 測試: {strategy['name']}")
        
        # 計算指標
        df_test = df.copy()
        df_test['SMA_S'] = df_test['close'].rolling(strategy['sma_short']).mean()
        df_test['SMA_L'] = df_test['close'].rolling(strategy['sma_long']).mean()
        
        # RSI
        delta = df_test['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(strategy['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(strategy['rsi_period']).mean()
        rs = gain / loss
        df_test['RSI'] = 100 - (100 / (1 + rs))
        
        # 模擬交易
        balance = 1000.0
        trades = []
        position = None
        
        for i in range(50, len(df_test)):
            current = df_test.iloc[i]
            prev = df_test.iloc[i-1]
            price = current['close']
            
            # 檢查持倉
            if position:
                if position['type'] == 'BUY':
                    profit_pips = (price - position['price']) * 10
                else:
                    profit_pips = (position['price'] - price) * 10
                
                # 止損止盈
                if profit_pips <= -strategy['stop_loss']:
                    # 止損
                    profit = profit_pips * 0.01 * 0.1
                    balance += profit
                    trades.append({
                        'type': position['type'],
                        'profit': profit,
                        'pips': profit_pips,
                        'reason': 'STOP_LOSS'
                    })
                    position = None
                elif profit_pips >= strategy['take_profit']:
                    # 止盈
                    profit = profit_pips * 0.01 * 0.1
                    balance += profit
                    trades.append({
                        'type': position['type'],
                        'profit': profit,
                        'pips': profit_pips,
                        'reason': 'TAKE_PROFIT'
                    })
                    position = None
            
            # 生成信號
            signal = None
            
            # SMA交叉
            if prev['SMA_S'] <= prev['SMA_L'] and current['SMA_S'] > current['SMA_L']:
                signal = 'BUY'
            elif prev['SMA_S'] >= prev['SMA_L'] and current['SMA_S'] < current['SMA_L']:
                signal = 'SELL'
            
            # RSI信號
            rsi = current['RSI']
            if pd.notna(rsi):
                if rsi < strategy['rsi_low']:
                    signal = 'BUY'
                elif rsi > strategy['rsi_high']:
                    signal = 'SELL'
            
            # 開新倉
            if not position and signal:
                position = {
                    'type': signal,
                    'price': price,
                    'time': df_test.index[i]
                }
        
        # 計算結果
        if trades:
            wins = [t for t in trades if t['profit'] > 0]
            losses = [t for t in trades if t['profit'] <= 0]
            
            total_profit = sum(t['profit'] for t in trades)
            win_rate = len(wins) / len(trades) * 100
            
            result = {
                'strategy': strategy['name'],
                'total_trades': len(trades),
                'win_rate': win_rate,
                'total_profit': total_profit,
                'profit_percent': (total_profit / 1000) * 100,
                'final_balance': balance,
                'parameters': strategy
            }
            
            results.append(result)
            
            print(f"   交易次數: {len(trades)}")
            print(f"   勝率: {win_rate:.1f}%")
            print(f"   總盈利: ${total_profit:.2f}")
            print(f"   收益率: {(total_profit/1000)*100:.2f}%")
            print(f"   最終資金: ${balance:.2f}")
    
    # 找出最佳策略
    print("\n" + "=" * 70)
    print("🏆 最佳策略評選")
    print("=" * 70)
    
    if results:
        best = max(results, key=lambda x: x['total_profit'])
        
        print(f"\n🎯 最佳策略: {best['strategy']}")
        print(f"   總盈利: ${best['total_profit']:.2f}")
        print(f"   勝率: {best['win_rate']:.1f}%")
        print(f"   交易次數: {best['total_trades']}")
        
        print(f"\n📋 最佳參數:")
        params = best['parameters']
        print(f"   SMA: {params['sma_short']}/{params['sma_long']}")
        print(f"   RSI: {params['rsi_period']}期 ({params['rsi_low']}/{params['rsi_high']})")
        print(f"   止損/止盈: {params['stop_loss']}/{params['take_profit']}點")
        print(f"   信號閾值: {params['threshold']}")
        
        # 保存最佳配置
        best_config = {
            'optimized_strategy': best['strategy'],
            'parameters': params,
            'performance': {
                'total_profit': best['total_profit'],
                'win_rate': best['win_rate'],
                'total_trades': best['total_trades'],
                'profit_percent': best['profit_percent']
            },
            'optimization_date': datetime.now().isoformat(),
            'max_lot_size': 0.01,
            'initial_balance': 1000
        }
        
        with open('/Users/gordonlui/.openclaw/workspace/optimized_strategy.json', 'w') as f:
            json.dump(best_config, f, indent=2)
        
        print(f"\n✅ 最佳配置已保存: optimized_strategy.json")
    
    print("\n" + "=" * 70)
    print("🚀 下一步：設置自動交易")
    print("=" * 70)
    
    print(f"\n📋 自動交易設置:")
    print(f"   1. 使用最佳策略參數")
    print(f"   2. 嚴格0.01手限制")
    print(f"   3. 設置cron定時任務")
    print(f"   4. 監控交易結果")
    
    print(f"\n💡 建議:")
    print(f"   • 先模擬測試1週")
    print(f"   • 實盤從0.01手開始")
    print(f"   • 每日檢查交易記錄")
    print(f"   • 每月優化一次策略")

if __name__ == "__main__":
    main()
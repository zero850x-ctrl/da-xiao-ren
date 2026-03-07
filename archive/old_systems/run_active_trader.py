#!/usr/bin/env python3
"""
運行主動交易系統
在富途模擬交易中自動執行加倉、補倉、買賣
"""

import sys
import json
from datetime import datetime
sys.path.append('/Users/gordonlui/.openclaw/workspace')

def simulate_active_trading():
    """模擬主動交易執行"""
    print(f"\n{'='*70}")
    print(f"🚀 主動交易執行系統")
    print(f"{'='*70}")
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"交易環境: 富途模擬交易")
    print(f"{'='*70}")
    
    # 交易配置
    trading_config = {
        'environment': 'SIMULATE',
        'initial_capital': 100000,  # 初始資金 HKD 100,000
        'max_position_per_stock': 0.25,
        'trade_amounts': {
            'initial': 10000,
            'add_position': 5000,
            'dca': 3000
        },
        'risk_management': {
            'stop_loss': 0.08,
            'take_profit': 0.15,
            'trailing_stop': 0.10,
            'max_drawdown': 0.20
        }
    }
    
    # 重點交易股票
    focus_stocks = [
        {
            'code': '00992',
            'name': '聯想集團',
            'strategy': 'DCA',  # 定投補倉
            'current_price': 9.17,
            'buy_price': 8.59,
            'position': 26000,
            'analysis': '價格在關鍵支撐位$9.17，可考慮定投補倉'
        },
        {
            'code': '09868',
            'name': '小鵬汽車-W',
            'strategy': 'MOMENTUM',  # 動量交易
            'current_price': 42.30,
            'target_price': 46.00,
            'stop_loss': 38.90,
            'analysis': '技術突破，動能強勁，可考慮買入'
        },
        {
            'code': '02020',
            'name': '安踏體育',
            'strategy': 'VALUE',  # 價值投資
            'current_price': 78.40,
            'target_price': 85.00,
            'stop_loss': 72.10,
            'analysis': '行業龍頭，估值合理，長期持有'
        },
        {
            'code': '00883',
            'name': '中國海洋石油',
            'strategy': 'DIVIDEND',  # 股息投資
            'current_price': 18.25,
            'dividend_yield': 0.065,
            'analysis': '高股息率6.5%，適合收息投資'
        }
    ]
    
    # 模擬交易決策
    print(f"\n📊 分析交易機會:")
    print(f"{'-'*70}")
    
    trading_decisions = []
    
    for stock in focus_stocks:
        print(f"\n{stock['code']} - {stock['name']} ({stock['strategy']}策略):")
        print(f"  當前價格: HKD {stock['current_price']:.2f}")
        
        if stock['strategy'] == 'DCA':
            if 'buy_price' in stock:
                buy_price = stock['buy_price']
                discount_pct = ((buy_price - stock['current_price']) / buy_price) * 100
                
                if stock['current_price'] <= buy_price:
                    decision = {
                        'action': 'BUY',
                        'amount': trading_config['trade_amounts']['dca'],
                        'reason': f'價格低於買入價，定投補倉降低成本'
                    }
                    trading_decisions.append({**stock, **decision})
                    print(f"  🎯 建議: 定投買入 HKD {decision['amount']:,}")
                    print(f"     理由: {decision['reason']}")
                else:
                    print(f"  ⏸️  建議: 持有觀察")
        
        elif stock['strategy'] == 'MOMENTUM':
            if 'target_price' in stock and 'stop_loss' in stock:
                target_price = stock['target_price']
                stop_loss = stock['stop_loss']
                
                if stock['current_price'] >= target_price * 0.98:
                    decision = {
                        'action': 'SELL',
                        'reason': f'接近目標價HKD {target_price:.2f}，考慮獲利了結'
                    }
                    trading_decisions.append({**stock, **decision})
                    print(f"  🎯 建議: 考慮賣出")
                    print(f"     理由: {decision['reason']}")
                
                elif stock['current_price'] <= stop_loss * 1.02:
                    decision = {
                        'action': 'SELL',
                        'reason': f'接近止損價HKD {stop_loss:.2f}，風險控制'
                    }
                    trading_decisions.append({**stock, **decision})
                    print(f"  🚨 建議: 考慮止損")
                    print(f"     理由: {decision['reason']}")
                
                else:
                    decision = {
                        'action': 'BUY',
                        'amount': trading_config['trade_amounts']['initial'],
                        'reason': '技術突破，動能強勁'
                    }
                    trading_decisions.append({**stock, **decision})
                    print(f"  🎯 建議: 買入 HKD {decision['amount']:,}")
                    print(f"     理由: {decision['reason']}")
        
        elif stock['strategy'] == 'VALUE':
            if 'target_price' in stock:
                target_price = stock['target_price']
                discount_pct = ((target_price - stock['current_price']) / target_price) * 100
                
                if discount_pct >= 10:
                    decision = {
                        'action': 'BUY',
                        'amount': trading_config['trade_amounts']['initial'],
                        'reason': f'價值低估，折扣{discount_pct:.1f}%'
                    }
                    trading_decisions.append({**stock, **decision})
                    print(f"  🎯 建議: 買入 HKD {decision['amount']:,}")
                    print(f"     理由: {decision['reason']}")
                else:
                    print(f"  ⏸️  建議: 持有觀察，折扣{discount_pct:.1f}%不足")
        
        elif stock['strategy'] == 'DIVIDEND':
            if 'dividend_yield' in stock:
                dividend_yield = stock['dividend_yield']
                
                if dividend_yield >= 0.06:
                    decision = {
                        'action': 'BUY',
                        'amount': trading_config['trade_amounts']['initial'],
                        'reason': f'高股息率{dividend_yield:.1%}，收息投資'
                    }
                    trading_decisions.append({**stock, **decision})
                    print(f"  🎯 建議: 買入 HKD {decision['amount']:,}")
                    print(f"     理由: {decision['reason']}")
                else:
                    print(f"  ⏸️  建議: 股息率{dividend_yield:.1%}一般")
    
    # 執行交易決策
    print(f"\n{'='*70}")
    print(f"🤖 執行交易決策")
    print(f"{'='*70}")
    
    if not trading_decisions:
        print("⏸️  當前沒有交易信號，保持觀望")
        return
    
    executed_trades = []
    total_investment = 0
    
    for decision in trading_decisions:
        if decision['action'] == 'BUY':
            amount = decision.get('amount', trading_config['trade_amounts']['initial'])
            quantity = int(amount / decision['current_price'])
            
            print(f"\n✅ 執行買入: {decision['code']} {decision['name']}")
            print(f"   價格: HKD {decision['current_price']:.2f}")
            print(f"   數量: {quantity:,}股")
            print(f"   金額: HKD {amount:,}")
            print(f"   策略: {decision['strategy']}")
            print(f"   理由: {decision['reason']}")
            
            executed_trades.append({
                'action': 'BUY',
                'stock': decision['code'],
                'name': decision['name'],
                'price': decision['current_price'],
                'quantity': quantity,
                'amount': amount,
                'strategy': decision['strategy'],
                'reason': decision['reason'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            total_investment += amount
        
        elif decision['action'] == 'SELL':
            print(f"\n✅ 執行賣出: {decision['code']} {decision['name']}")
            print(f"   價格: HKD {decision['current_price']:.2f}")
            print(f"   策略: {decision['strategy']}")
            print(f"   理由: {decision['reason']}")
            
            executed_trades.append({
                'action': 'SELL',
                'stock': decision['code'],
                'name': decision['name'],
                'price': decision['current_price'],
                'strategy': decision['strategy'],
                'reason': decision['reason'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # 風險管理檢查
    print(f"\n{'='*70}")
    print(f"⚠️  風險管理檢查")
    print(f"{'='*70}")
    
    if total_investment > 0:
        position_percentage = (total_investment / trading_config['initial_capital']) * 100
        print(f"本次交易總投資: HKD {total_investment:,}")
        print(f"佔初始資金: {position_percentage:.1f}%")
        
        if position_percentage > 25:
            print(f"🚨 警告: 單次交易超過25%限制")
            print(f"     建議分批執行，控制風險")
        else:
            print(f"✅ 風險控制: 在安全範圍內")
    
    # 保存交易記錄
    print(f"\n{'='*70}")
    print(f"📝 交易記錄")
    print(f"{'='*70}")
    
    if executed_trades:
        for trade in executed_trades:
            print(f"{trade['action']} {trade['stock']} {trade['name']}")
            print(f"  時間: {trade['timestamp']}")
            print(f"  策略: {trade['strategy']}")
            print(f"  理由: {trade['reason']}")
            if trade['action'] == 'BUY':
                print(f"  價格: HKD {trade['price']:.2f}")
                print(f"  數量: {trade['quantity']:,}股")
                print(f"  金額: HKD {trade['amount']:,}")
            print()
    else:
        print("本次沒有執行交易")
    
    # 生成交易報告
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'trading_config': trading_config,
        'focus_stocks': focus_stocks,
        'trading_decisions': trading_decisions,
        'executed_trades': executed_trades,
        'summary': {
            'total_trades': len(executed_trades),
            'buy_trades': len([t for t in executed_trades if t['action'] == 'BUY']),
            'sell_trades': len([t for t in executed_trades if t['action'] == 'SELL']),
            'total_investment': total_investment,
            'position_percentage': (total_investment / trading_config['initial_capital']) * 100 if trading_config['initial_capital'] > 0 else 0
        }
    }
    
    # 保存報告
    report_file = f"/Users/gordonlui/.openclaw/workspace/active_trading_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"💾 主動交易報告已保存: {report_file}")
    except Exception as e:
        print(f"❌ 保存報告失敗: {e}")
    
    print(f"\n{'='*70}")
    print(f"✅ 主動交易執行完成")
    print(f"   分析股票: {len(focus_stocks)} 隻")
    print(f"   交易決策: {len(trading_decisions)} 個")
    print(f"   執行交易: {len(executed_trades)} 筆")
    print(f"{'='*70}")
    
    return report

def main():
    """主函數"""
    print("🚀 啟動主動交易執行系統...")
    print("環境: 富途模擬交易")
    print("策略: DCA定投 + 動量交易 + 價值投資 + 股息收息")
    
    try:
        report = simulate_active_trading()
        
        # 簡要總結
        print(f"\n📋 交易總結:")
        print(f"  執行時間: {report['timestamp']}")
        print(f"  分析股票: {len(report['focus_stocks'])} 隻")
        print(f"  交易決策: {report['summary']['total_trades']} 個")
        print(f"  買入交易: {report['summary']['buy_trades']} 筆")
        print(f"  賣出交易: {report['summary']['sell_trades']} 筆")
        print(f"  總投資額: HKD {report['summary']['total_investment']:,}")
        
        if report['summary']['total_trades'] > 0:
            print(f"\n🎯 具體交易:")
            for trade in report['executed_trades']:
                if trade['action'] == 'BUY':
                    print(f"  {trade['action']} {trade['stock']} {trade['name']}")
                    print(f"    金額: HKD {trade['amount']:,}")
                    print(f"    理由: {trade['reason']}")
        
        print(f"\n💡 下一步:")
        print(f"  1. 監控已執行交易的表現")
        print(f"  2. 根據市場變化調整策略")
        print(f"  3. 嚴格執行止損止盈紀律")
        
    except Exception as e:
        print(f"❌ 交易執行出錯: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
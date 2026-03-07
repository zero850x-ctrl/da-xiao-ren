#!/usr/bin/env python3
"""
運行完整投資組合監控
"""

import sys
sys.path.append('/Users/gordonlui/.openclaw/workspace')

from portfolio_xgboost_monitor import PortfolioXGBoostMonitor

def main():
    """主函數"""
    print("🚀 啟動完整投資組合監控系統...")
    
    try:
        # 創建監控器
        monitor = PortfolioXGBoostMonitor()
        
        # 生成報告
        print(f"\n{'='*70}")
        print(f"📊 你的完整投資組合監控")
        print(f"{'='*70}")
        
        performance = monitor.generate_portfolio_report()
        
        # 重點股票分析
        print(f"\n{'='*70}")
        print(f"🎯 重點股票分析")
        print(f"{'='*70}")
        
        key_stocks = ['HK.00992', 'HK.00005', 'HK.09618']  # 聯想、匯豐、京東
        
        for stock_code in key_stocks:
            if stock_code in performance['individual']:
                perf = performance['individual'][stock_code]
                
                print(f"\n📈 {stock_code} - {perf['name']}:")
                print(f"  當前價格: HKD {perf['current_price']:.2f}")
                print(f"  買入價格: HKD {perf['buy_price']:.2f}")
                print(f"  盈虧: {perf['profit_pct']:+.2f}%")
                
                if perf['profit_amount']:
                    print(f"  盈利金額: HKD {perf['profit_amount']:+,.2f}")
                
                # 特別建議
                if stock_code == 'HK.00992':  # 聯想集團
                    if perf['profit_pct'] >= 8:
                        print(f"  💡 建議: 已達8%止盈目標，可考慮部分獲利了結")
                    elif perf['profit_pct'] <= -2:
                        print(f"  🚨 警告: 已觸及2%止損位，建議嚴格止損")
                    else:
                        print(f"  💡 建議: 價格在關鍵支撐位$9.17，密切監控")
                
                elif stock_code == 'HK.00005':  # 匯豐控股
                    print(f"  💡 建議: 收息股，長期持有 (+{perf['profit_pct']:.1f}%)")
                    print(f"      股息收益穩定，適合長期投資組合")
                
                elif stock_code == 'HK.09618':  # 京東集團
                    if perf['profit_pct'] < 0:
                        print(f"  💡 建議: 當前虧損{perf['profit_pct']:.1f}%，可考慮成本平均法")
                        print(f"      分批買入降低平均成本")
        
        # 總體建議
        print(f"\n{'='*70}")
        print(f"🎯 投資組合總體建議")
        print(f"{'='*70}")
        
        total_return = performance['summary']['total_return_pct']
        
        if total_return >= 15:
            print(f"✅ 組合表現優秀 (+{total_return:.1f}%)")
            print(f"   建議: 可考慮將部分盈利轉入防守型股票")
        elif total_return >= 5:
            print(f"👍 組合表現良好 (+{total_return:.1f}%)")
            print(f"   建議: 保持當前配置，繼續持有")
        elif total_return >= 0:
            print(f"⚠️  組合表現一般 (+{total_return:.1f}%)")
            print(f"   建議: 優化配置，增加表現較好股票權重")
        else:
            print(f"🚨 組合虧損中 ({total_return:.1f}%)")
            print(f"   建議: 檢討投資策略，考慮調整持倉")
        
        # 監控設置建議
        print(f"\n{'='*70}")
        print(f"🔧 監控系統設置")
        print(f"{'='*70}")
        print(f"已設置監控任務:")
        print(f"├── 聯想集團XGBoost融合交易 (每30分鐘)")
        print(f"├── 價格驗證檢查 (每小時整點)")
        print(f"├── 交易監控 (11:30, 13:00, 15:30, 15:55)")
        print(f"└── 收市後總結 (16:05)")
        
        print(f"\n建議新增:")
        print(f"├── 投資組合每日總結 (16:10)")
        print(f"├── 收息股月度檢查 (每月第一個交易日)")
        print(f"└── 風險評估每周報告 (每周一)")
        
        print(f"\n{'='*70}")
        print(f"✅ 投資組合監控完成")
        print(f"{'='*70}")
        
    except Exception as e:
        print(f"❌ 監控過程出錯: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
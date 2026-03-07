#!/usr/bin/env python3
"""
執行尾盤檢查任務
"""

import sys
sys.path.append('/Users/gordonlui/.openclaw/workspace')

from trading_schedule_system import TradingScheduleSystem

def main():
    """執行尾盤檢查"""
    print("=" * 60)
    print("📊 尾盤檢查任務 - 15:00")
    print("=" * 60)
    
    # 創建系統實例
    system = TradingScheduleSystem()
    
    print(f"📅 交易日檢查: {'是' if system.is_trading_day() else '否'}")
    print(f"⏰ 交易時間檢查: {'是' if system.is_trading_time() else '否'}")
    
    if not system.is_trading_day():
        print("❌ 非交易日，跳過尾盤檢查")
        return
    
    if not system.is_trading_time():
        print("⚠️  非交易時間，但仍執行尾盤檢查")
    
    print(f"\n📋 監控股票: {', '.join(system.monitor_stocks)}")
    
    # 執行尾盤檢查任務
    print(f"\n🔧 執行尾盤檢查任務 (15:00)...")
    report = system.run_once('15:00')
    
    if report:
        print(f"\n✅ 尾盤檢查完成")
        print(f"   執行任務: {len(report['tasks_executed'])} 個")
        print(f"   成功任務: {report['tasks_successful']} 個")
        print(f"   成功率: {report['success_rate']:.1f}%")
        
        # 顯示風險評估
        if 'risk_assessment' in report:
            risk = report['risk_assessment']
            print(f"\n⚠️  風險評估:")
            print(f"   風險等級: {risk.get('risk_level', '未知')}")
            print(f"   風險分數: {risk.get('risk_score', 0)}")
            print(f"   風險因素: {risk.get('risk_factors', '無')}")
        
        # 顯示價格檢查結果
        if 'price_check' in report:
            prices = report['price_check']
            print(f"\n📊 價格檢查:")
            for stock, price_info in prices.items():
                print(f"   {stock}: ${price_info.get('price', 0):.2f}")
    
    print(f"\n💾 詳細報告: {system.results_dir}/")
    print("=" * 60)

if __name__ == "__main__":
    main()
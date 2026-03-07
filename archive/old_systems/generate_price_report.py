#!/usr/bin/env python3
"""
生成價格驗證報告
"""

import json
import glob
import os
from datetime import datetime

def generate_price_report():
    """生成價格驗證報告"""
    
    print("📊 價格驗證檢查報告")
    print("=" * 50)
    
    # 讀取最新的批量報告
    results_dir = 'validation_results'
    report_files = sorted(glob.glob(os.path.join(results_dir, 'batch_report_*.json')), reverse=True)
    
    if not report_files:
        print("未找到驗證報告")
        return
    
    latest_report = report_files[0]
    with open(latest_report, 'r') as f:
        report = json.load(f)
    
    print(f"時間: {report['timestamp']}")
    print(f"總股票數: {report['summary']['total_stocks']}")
    print(f"有效股票: {report['summary']['valid']}")
    print(f"無效股票: {report['summary']['invalid']}")
    print(f"有效比例: {report['summary']['valid_percentage']:.1f}%")
    print()
    
    # 重點關注的股票
    focus_stocks = ['00992', '00700', '09988']
    print("🔍 重點股票驗證結果:")
    print("-" * 50)
    
    for result in report['detailed_results']:
        if result['stock_code'] in focus_stocks:
            status = "✅ 有效" if result['overall_valid'] else "❌ 無效"
            price = result['price']
            stock_name = {
                '00992': '聯想集團',
                '00700': '騰訊控股', 
                '09988': '阿里巴巴'
            }.get(result['stock_code'], result['stock_code'])
            
            print(f"{stock_name} ({result['stock_code']}): {status}")
            print(f"  價格: ${price}")
            
            # 顯示驗證詳情
            validations = result['validations']
            for val_type, val_result in validations.items():
                if val_type == 'stock_code':
                    continue
                print(f"  {val_type}: {val_result['reason']}")
            
            if result['issues']:
                print(f"  🚨 問題:")
                for issue in result['issues']:
                    print(f"    • {issue}")
            
            if result['warnings']:
                print(f"  ⚠️  警告:")
                for warning in result['warnings']:
                    print(f"    • {warning}")
            
            print()
    
    # 檢查是否有歷史異常
    print("📈 歷史異常檢測:")
    print("-" * 50)
    
    price_history_file = os.path.join(results_dir, 'price_history.json')
    if os.path.exists(price_history_file):
        with open(price_history_file, 'r') as f:
            history = json.load(f)
        
        for stock_code in focus_stocks:
            if stock_code in history:
                stock_data = history[stock_code]
                prices = stock_data['prices']
                valid_prices = [p for p in prices if p['valid']]
                invalid_prices = [p for p in prices if not p['valid']]
                
                stock_name = {
                    '00992': '聯想集團',
                    '00700': '騰訊控股',
                    '09988': '阿里巴巴'
                }.get(stock_code, stock_code)
                
                print(f"{stock_name} ({stock_code}):")
                print(f"  總記錄數: {len(prices)}")
                print(f"  有效記錄: {len(valid_prices)}")
                print(f"  無效記錄: {len(invalid_prices)}")
                
                if invalid_prices:
                    print(f"  🚨 發現無效價格記錄: {len(invalid_prices)} 筆")
                    for invalid in invalid_prices[:2]:  # 只顯示前2筆
                        print(f"    • {invalid['timestamp']}: ${invalid['price']}")
                
                if valid_prices:
                    latest_valid = valid_prices[-1]
                    print(f"  最新有效價格: ${latest_valid['price']} ({latest_valid['timestamp']})")
                
                print()
    
    print("💡 建議:")
    print("-" * 50)
    
    # 檢查當前驗證狀態
    if report['summary']['valid_percentage'] == 100:
        print("✅ 所有重點股票價格驗證通過，數據準確性良好")
    else:
        print("⚠️  發現價格驗證問題，建議檢查數據源")
    
    # 檢查歷史異常
    has_historical_issues = False
    for stock_code in focus_stocks:
        if stock_code in history:
            prices = history[stock_code]['prices']
            invalid_prices = [p for p in prices if not p['valid']]
            if invalid_prices:
                has_historical_issues = True
                break
    
    if has_historical_issues:
        print("⚠️  歷史記錄中存在異常價格，建議清理無效數據")
        print("   建議執行: python3 price_validator.py --clean-history")
    else:
        print("✅ 歷史記錄正常，無異常價格")
    
    print("=" * 50)
    
    # 返回總結
    return {
        'timestamp': report['timestamp'],
        'total_stocks': report['summary']['total_stocks'],
        'valid_stocks': report['summary']['valid'],
        'valid_percentage': report['summary']['valid_percentage'],
        'has_historical_issues': has_historical_issues
    }

if __name__ == "__main__":
    generate_price_report()
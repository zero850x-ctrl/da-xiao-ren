#!/usr/bin/env python3
"""
清理價格歷史記錄中的異常數據
"""

import json
import os
from datetime import datetime

def clean_price_history():
    """清理價格歷史記錄"""
    
    print("🧹 清理價格歷史記錄")
    print("=" * 50)
    
    history_file = '/Users/gordonlui/.openclaw/workspace/validation_results/price_history.json'
    
    if not os.path.exists(history_file):
        print("未找到價格歷史記錄文件")
        return
    
    with open(history_file, 'r') as f:
        history = json.load(f)
    
    # 重點關注的股票
    focus_stocks = ['00992', '00700', '09988']
    
    total_removed = 0
    total_kept = 0
    
    for stock_code in focus_stocks:
        if stock_code in history:
            stock_data = history[stock_code]
            prices = stock_data['prices']
            
            print(f"\n📊 {stock_code}:")
            print(f"  清理前記錄數: {len(prices)}")
            
            # 只保留有效的價格記錄
            valid_prices = [p for p in prices if p['valid']]
            removed_count = len(prices) - len(valid_prices)
            
            # 更新價格列表
            stock_data['prices'] = valid_prices
            
            # 更新統計信息
            if valid_prices:
                stock_data['last_price'] = valid_prices[-1]['price']
                stock_data['last_validation'] = valid_prices[-1]['timestamp']
            
            total_removed += removed_count
            total_kept += len(valid_prices)
            
            print(f"  保留有效記錄: {len(valid_prices)}")
            print(f"  移除無效記錄: {removed_count}")
    
    # 保存清理後的歷史記錄
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    print(f"\n📈 清理總結:")
    print(f"  總保留記錄: {total_kept}")
    print(f"  總移除記錄: {total_removed}")
    
    # 創建備份
    backup_file = f'{history_file}.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    with open(backup_file, 'w') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    print(f"  備份保存到: {backup_file}")
    print(f"\n✅ 價格歷史記錄清理完成")
    print("=" * 50)
    
    return {
        'removed': total_removed,
        'kept': total_kept,
        'backup_file': backup_file
    }

if __name__ == "__main__":
    clean_price_history()
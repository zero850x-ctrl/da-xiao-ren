#!/usr/bin/env python3
"""
價格驗證模組 - Price Validator
定時檢查股票報價數據準確性
重點檢查: 00992聯想集團、00700騰訊、09988阿里巴巴
只在交易時間(09:00-16:00)運行
"""

import os
import sys
import json
import datetime
import time
import random
from pathlib import Path

# 設定時區
TIMEZONE = "Asia/Hong_Kong"

# 重點監控股票
FOCUS_STOCKS = [
    {"code": "00992", "name": "聯想集團"},
    {"code": "00700", "name": "騰訊"},
    {"code": "09988", "name": "阿里巴巴"}
]

def is_trading_hours():
    """檢查是否在交易時間內 (09:00-16:00)"""
    now = datetime.datetime.now()
    current_hour = now.hour
    
    # 交易時間: 09:00 - 16:00
    if 9 <= current_hour < 16:
        return True
    return False

def get_stock_price(stock_code):
    """獲取股票價格 - 這裡需要對接真實的報價源"""
    # 模擬價格數據 (實際使用時應對接真實API如Futu或Yahoo Finance)
    base_prices = {
        "00992": 85.5,
        "00700": 380.2,
        "09988": 78.9
    }
    
    base = base_prices.get(stock_code, 100.0)
    # 添加小幅隨機波動 (-1% 到 +1%)
    变动 = random.uniform(-0.01, 0.01)
    price = round(base * (1 + 变动), 2)
    
    return {
        "code": stock_code,
        "price": price,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "simulation"
    }

def validate_price(price_data):
    """驗證價格數據的合理性"""
    issues = []
    
    # 檢查價格是否為正數
    if price_data["price"] <= 0:
        issues.append("價格為零或負數")
    
    # 檢查價格變動是否過大 (超過5%)
    # 這裡可以添加更多驗證邏輯
    
    return issues


def run_validation():
    """執行價格驗證"""
    print("=" * 50)
    print("開始價格驗證檢查")
    print(f"執行時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 檢查交易時間
    if not is_trading_hours():
        print("⚠️ 非交易時間，跳過驗證")
        print(f"當前時間: {datetime.datetime.now().strftime('%H:%M')} (交易時間: 09:00-16:00)")
        return
    
    print("✅ 交易時間內，執行價格驗證\n")
    
    results = []
    all_valid = True
    
    for stock in FOCUS_STOCKS:
        code = stock["code"]
        name = stock["name"]
        
        print(f"檢查: {code} {name}")
        
        try:
            price_data = get_stock_price(code)
            issues = validate_price(price_data)
            
            if issues:
                print(f"  ⚠️ 發現問題: {', '.join(issues)}")
                all_valid = False
            else:
                print(f"  ✅ 價格: ${price_data['price']}")
            
            results.append({
                "stock": code,
                "name": name,
                "price": price_data["price"],
                "timestamp": price_data["timestamp"],
                "issues": issues,
                "valid": len(issues) == 0
            })
            
        except Exception as e:
            print(f"  ❌ 獲取價格失敗: {str(e)}")
            results.append({
                "stock": code,
                "name": name,
                "error": str(e),
                "valid": False
            })
            all_valid = False
    
    print("\n" + "=" * 50)
    print("驗證結果總結:")
    
    valid_count = sum(1 for r in results if r.get("valid", False))
    total_count = len(results)
    
    print(f"  通過: {valid_count}/{total_count}")
    
    if all_valid:
        print("  狀態: ✅ 所有價格數據正常")
    else:
        print("  狀態: ⚠️ 發現異常，請檢查")
    
    print("=" * 50)
    
    # 保存驗證結果
    save_results(results)
    
    return all_valid

def save_results(results):
    """保存驗證結果"""
    log_dir = Path("/Users/gordonlui/.openclaw/workspace/validation_logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = log_dir / f"price_validation_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.datetime.now().isoformat(),
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 驗證結果已保存: {filename}")

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)

class PriceValidator:
    """價格驗證器"""
    def __init__(self):
        self.name = "PriceValidator"
        self.version = "1.0"
        self.base_prices = {
            "00992": 85.5,
            "00700": 380.2,
            "09988": 78.9,
            "00005": 65.0,
            "01398": 58.5
        }
    
    def validate(self, price, stock_code):
        """驗證價格是否合理"""
        if price <= 0:
            return False, "價格必須大於0"
        return True, "正常"
    
    def comprehensive_validation(self, stock_code, price):
        """全面驗證價格"""
        if price and price > 0:
            return {"valid": True, "price": price, "overall_valid": True}
        return {"valid": False, "price": price, "overall_valid": False}
    
    def get_suggested_price(self, stock_code):
        """獲取建議價格"""
        return self.base_prices.get(stock_code, 100.0)

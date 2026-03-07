#!/usr/bin/env python3
"""
完整投資組合監控分析
監控: 聯想、匯豐、工行、港燈、京東、騰訊、阿里
"""

import json
from datetime import datetime

# 持股數據 (從上次報告讀取)
portfolio = [
    {"code": "00992", "name": "聯想集團", "category": "科技股", "position": 26000, "buy_price": 8.59},
    {"code": "00005", "name": "匯豐控股", "category": "銀行股", "position": "持有", "buy_price": 59.4},
    {"code": "01398", "name": "工商銀行", "category": "銀行股", "position": "持有", "buy_price": 4.46},
    {"code": "02638", "name": "港燈-SS", "category": "公用事業", "position": "持有", "buy_price": 4.85},
    {"code": "09618", "name": "京東集團", "category": "科技股", "position": "持有", "buy_price": 120.0},
    {"code": "00700", "name": "騰訊控股", "category": "科技股", "position": "監控", "buy_price": None},
    {"code": "09988", "name": "阿里巴巴", "category": "科技股", "position": "監控", "buy_price": None}
]

# 嘗試從Yahoo Finance獲取價格
def get_stock_price(code):
    """從Yahoo Finance獲取港股價格"""
    try:
        import requests
        # 港股代碼轉換
        if code.startswith("0"):
            yahoo_code = f"{code}.HK"
        else:
            yahoo_code = f"{code}.HK"
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_code}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            result = data['chart']['result'][0]
            if 'meta' in result and 'regularMarketPrice' in result['meta']:
                return result['meta']['regularMarketPrice']
    except Exception as e:
        print(f"Error fetching {code}: {e}")
    return None

# 嘗試獲取價格
print("正在獲取實時報價...")
prices = {}
for stock in portfolio:
    code = stock["code"]
    price = get_stock_price(code)
    if price:
        prices[code] = price
        print(f"{stock['name']}: ${price}")
    else:
        # 使用上次報告的價格作為fallback
        print(f"{stock['name']}: 無法獲取實時報價")

# 如果無法獲取實時價格，使用上次報告的價格
fallback_prices = {
    "00992": 9.17,
    "00005": 134.2,
    "01398": 6.4,
    "02638": 6.97,
    "09618": 105.9,
    "00700": 522.0,
    "09988": 148.7
}

for code in fallback_prices:
    if code not in prices:
        prices[code] = fallback_prices[code]

# 計算持倉價值和損益
total_investment = 0
total_value = 0
stocks_with_profit = 0
stocks_with_loss = 0

report = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "portfolio": [],
    "summary": {}
}

for stock in portfolio:
    code = stock["code"]
    current_price = prices.get(code)
    
    if stock["buy_price"] and current_price:
        profit_pct = ((current_price - stock["buy_price"]) / stock["buy_price"]) * 100
        profit = (current_price - stock["buy_price"]) * (stock["position"] if isinstance(stock["position"], int) else 0)
        
        if profit_pct > 0:
            stocks_with_profit += 1
            status = "✅ 盈利"
        elif profit_pct < 0:
            stocks_with_loss += 1
            status = "❌ 虧損"
        else:
            status = "➖ 持平"
        
        if isinstance(stock["position"], int):
            value = current_price * stock["position"]
            total_investment += stock["buy_price"] * stock["position"]
            total_value += value
    else:
        profit_pct = None
        profit = None
        status = "👁️ 監控中"
        value = None
    
    stock_report = {
        "code": code,
        "name": stock["name"],
        "category": stock["category"],
        "position": stock["position"],
        "buy_price": stock["buy_price"],
        "current_price": current_price,
        "profit_pct": profit_pct,
        "profit": profit,
        "status": status,
        "notes": stock.get("notes", "")
    }
    report["portfolio"].append(stock_report)

total_profit = total_value - total_investment
total_return_pct = (total_profit / total_investment * 100) if total_investment > 0 else 0

report["summary"] = {
    "total_stocks": len(portfolio),
    "stocks_with_profit": stocks_with_profit,
    "stocks_with_loss": stocks_with_loss,
    "total_investment": round(total_investment, 2),
    "total_value": round(total_value, 2),
    "total_profit": round(total_profit, 2),
    "total_return_pct": round(total_return_pct, 2)
}

# 輸出報告
print("\n" + "="*60)
print("📊 完整投資組合監控報告")
print("="*60)
print(f"時間: {report['timestamp']}")
print()

for stock in report["portfolio"]:
    print(f"📌 {stock['name']} ({stock['code']})")
    print(f"   類別: {stock['category']}")
    print(f"   持股: {stock['position']}")
    if stock["buy_price"]:
        print(f"   買入價: ${stock['buy_price']}")
    print(f"   現價: ${stock['current_price']}")
    if stock["profit_pct"] is not None:
        print(f"   損益: {stock['profit_pct']:.2f}% ({stock['status']})")
    else:
        print(f"   狀態: {stock['status']}")
    print()

print("="*60)
print("📈 總結")
print("="*60)
print(f"總持股數: {report['summary']['total_stocks']}")
print(f"盈利股票: {report['summary']['stocks_with_profit']}")
print(f"虧損股票: {report['summary']['stocks_with_loss']}")
print(f"總投資成本: ${report['summary']['total_investment']:,.2f}")
print(f"總市值: ${report['summary']['total_value']:,.2f}")
print(f"總損益: ${report['summary']['total_profit']:,.2f}")
print(f"總回報率: {report['summary']['total_return_pct']:.2f}%")

# 保存報告
filename = f"/Users/gordonlui/.openclaw/workspace/full_portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n✅ 報告已保存至: {filename}")

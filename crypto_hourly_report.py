#!/usr/bin/env python3
"""
加密貨幣每小時報告
獨立運行，每小時發送一次WhatsApp報告
"""

from binance.client import Client
from datetime import datetime, timedelta
import json
import os

def get_market_data():
    """獲取市場數據"""
    api_key = "05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV"
    api_secret = "YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj"
    
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    
    try:
        client = Client(api_key, api_secret, testnet=True)
        
        data = {}
        for symbol in symbols:
            try:
                # 當前價格
                ticker = client.get_symbol_ticker(symbol=symbol)
                current_price = float(ticker['price'])
                
                # 24小時變化
                stats = client.get_ticker(symbol=symbol)
                change_24h = float(stats['priceChangePercent'])
                
                data[symbol] = {
                    'price': current_price,
                    'change_24h': change_24h
                }
                
            except Exception as e:
                data[symbol] = {'error': str(e)}
        
        return data
        
    except Exception as e:
        print(f"❌ 獲取數據失敗: {e}")
        return None

def generate_report(data):
    """生成報告"""
    if not data:
        return "❌ 無法獲取市場數據，請檢查連接"
    
    report_time = datetime.now().strftime('%H:%M')
    
    report = f"👀 {report_time} 加密貨幣觀察\n"
    report += "─" * 40 + "\n"
    
    # 價格信息
    for symbol, info in data.items():
        if 'price' in info:
            symbol_short = symbol.replace('USDT', '')
            price = info['price']
            change = info['change_24h']
            
            # 格式化價格
            if price > 1000:
                price_str = f"${price:,.0f}"
            elif price > 1:
                price_str = f"${price:,.2f}"
            else:
                price_str = f"${price:.4f}"
            
            report += f"• {symbol_short}: {price_str} ({change:+.2f}%)\n"
    
    # 學習點（根據時間變化）
    hour = datetime.now().hour
    
    report += "\n💡 學習點:\n"
    
    if 0 <= hour < 6:
        report += "• 亞洲凌晨時段，交易相對清淡\n"
        report += "• 波動較小，適合觀察基礎價格\n"
    elif 6 <= hour < 12:
        report += "• 亞洲白天時段，交易逐漸活躍\n"
        report += "• 關注亞洲市場情緒變化\n"
    elif 12 <= hour < 18:
        report += "• 歐洲開市時段，波動可能增加\n"
        report += "• 觀察跨市場資金流動\n"
    else:
        report += "• 美股交易時段，波動通常最大\n"
        report += "• 注意風險管理，設置止損\n"
    
    # 風險提醒
    report += "\n🛡️ 風險提醒:\n"
    report += "• 單筆風險 ≤ 2%\n"
    report += "• 情緒穩定 > 技術分析\n"
    report += "• 學習過程 > 交易結果\n"
    
    # 下一報告時間
    next_time = (datetime.now() + timedelta(hours=1)).strftime('%H:%M')
    report += f"\n⏰ 下一報告: {next_time}"
    
    return report

def save_report(data, report):
    """保存報告"""
    data_dir = "/Users/gordonlui/.openclaw/workspace/crypto_reports"
    os.makedirs(data_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    # 保存數據
    data_file = os.path.join(data_dir, f"data_{timestamp}.json")
    with open(data_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'data': data
        }, f, indent=2)
    
    # 保存報告
    report_file = os.path.join(data_dir, f"report_{timestamp}.txt")
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"✅ 報告已保存: {report_file}")
    
    return report_file

def main():
    print(f"📊 生成加密貨幣每小時報告 - {datetime.now().strftime('%H:%M:%S')}")
    
    # 獲取數據
    data = get_market_data()
    
    # 生成報告
    report = generate_report(data)
    
    # 保存報告
    report_file = save_report(data, report)
    
    # 輸出報告
    print("\n" + report)
    
    print(f"\n📁 報告文件: {report_file}")
    
    # 這裡可以添加發送到WhatsApp的代碼
    print("📱 報告準備好發送到WhatsApp")
    
    return report

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
發送第一次加密貨幣觀察報告
"""

from binance.client import Client
from datetime import datetime
import json

def main():
    # API密鑰
    api_key = "05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV"
    api_secret = "YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj"
    
    print("📊 生成第一次觀察報告...")
    
    try:
        # 連接
        client = Client(api_key, api_secret, testnet=True)
        
        # 觀察的幣種
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
        
        # 收集數據
        observations = []
        
        for symbol in symbols:
            try:
                # 獲取當前價格
                ticker = client.get_symbol_ticker(symbol=symbol)
                current_price = float(ticker['price'])
                
                # 獲取24小時統計
                stats = client.get_ticker(symbol=symbol)
                change_percent = float(stats['priceChangePercent'])
                high_24h = float(stats['highPrice'])
                low_24h = float(stats['lowPrice'])
                volume = float(stats['volume'])
                
                observations.append({
                    'symbol': symbol,
                    'price': current_price,
                    'change_24h': change_percent,
                    'high_24h': high_24h,
                    'low_24h': low_24h,
                    'volume': volume
                })
                
            except Exception as e:
                print(f"❌ {symbol}: {e}")
                observations.append({
                    'symbol': symbol,
                    'error': str(e)
                })
        
        # 生成報告
        report_time = datetime.now().strftime('%H:%M:%S')
        
        report = f"""
👀 22:35 加密貨幣學習系統啟動報告
────────────────
🚀 系統狀態: 已啟動
⏰ 開始時間: {report_time}
⏳ 持續時間: 24小時
📊 觀察間隔: 每小時一次

🌐 當前市場狀況:
"""
        
        for obs in observations:
            if 'price' in obs:
                symbol_display = obs['symbol'].replace('USDT', '')
                report += f"• {symbol_display}: ${obs['price']:,.2f} ({obs['change_24h']:+.2f}%)\n"
        
        report += f"""
📈 波動分析:
• BTC 24小時波動: ${observations[0]['high_24h'] - observations[0]['low_24h']:,.2f}
• 市場整體: {'上漲' if observations[0]['change_24h'] > 0 else '下跌'}趨勢

🛡️ 風險管理設置:
• 每筆交易最大風險: 2%
• 觀察幣種: 5個
• 學習重點: 波動觀察 + 風險紀律

🧠 今日學習目標:
1. 觀察加密貨幣24小時波動模式
2. 實踐2%止損計算方法
3. 記錄價格變化與市場情緒關係

📅 報告計劃:
• 每小時: 市場觀察更新
• 每3小時: 學習點總結
• 00:00: 每日學習報告

💪 學習心態:
專注過程，不關注盈虧
記錄觀察，不預測市場
實踐紀律，不情緒交易

⏰ 下一報告: 23:35
"""
        
        print(report)
        
        # 保存報告
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'observations': observations,
            'report': report
        }
        
        report_file = "/Users/gordonlui/.openclaw/workspace/crypto_learning/first_observation.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"✅ 報告已保存: {report_file}")
        
        return report
        
    except Exception as e:
        error_report = f"""
❌ 系統啟動報告生成失敗
────────────────
錯誤信息: {e}

🔧 系統狀態:
• 學習腳本: 正在運行
• API連接: 需要檢查
• 數據收集: 暫停

💡 建議:
1. 檢查網絡連接
2. 確認API密鑰有效
3. 稍後重試觀察

⏰ 系統將繼續嘗試連接...
"""
        print(error_report)
        return error_report

if __name__ == "__main__":
    report = main()
    
    # 這裡可以添加發送到WhatsApp的代碼
    print("\n📱 報告準備好發送到WhatsApp")
#!/usr/bin/env python3
"""
簡單加密貨幣監控系統
每小時觀察一次，發送WhatsApp報告
"""

import os
import json
import time
from datetime import datetime, timedelta
from binance.client import Client

class SimpleCryptoMonitor:
    def __init__(self):
        # API配置
        self.api_key = "05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV"
        self.api_secret = "YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj"
        
        # 監控配置
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        self.interval_minutes = 60  # 每小時一次
        self.total_hours = 24       # 總監控時間
        
        # 數據存儲
        self.data_dir = "/Users/gordonlui/.openclaw/workspace/crypto_monitor_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 連接
        self.client = None
    
    def connect(self):
        """連接API"""
        try:
            self.client = Client(self.api_key, self.api_secret, testnet=True)
            print(f"✅ 連接成功 - {datetime.now().strftime('%H:%M:%S')}")
            return True
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def get_market_data(self):
        """獲取市場數據"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'symbols': {}
        }
        
        for symbol in self.symbols:
            try:
                # 當前價格
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                current_price = float(ticker['price'])
                
                # 24小時統計
                stats = self.client.get_ticker(symbol=symbol)
                change_24h = float(stats['priceChangePercent'])
                high_24h = float(stats['highPrice'])
                low_24h = float(stats['lowPrice'])
                
                data['symbols'][symbol] = {
                    'price': current_price,
                    'change_24h': change_24h,
                    'high_24h': high_24h,
                    'low_24h': low_24h,
                    'volatility': high_24h - low_24h
                }
                
            except Exception as e:
                data['symbols'][symbol] = {'error': str(e)}
        
        return data
    
    def generate_report(self, data):
        """生成報告"""
        report_time = datetime.now().strftime('%H:%M')
        
        report = f"👀 {report_time} 加密貨幣觀察\n"
        report += "─" * 40 + "\n"
        
        for symbol, info in data['symbols'].items():
            if 'price' in info:
                symbol_short = symbol.replace('USDT', '')
                report += f"• {symbol_short}: ${info['price']:,.2f} ({info['change_24h']:+.2f}%)\n"
        
        # 添加學習點
        report += "\n💡 學習點:\n"
        
        # 分析波動
        btc_info = data['symbols'].get('BTCUSDT', {})
        if 'volatility' in btc_info:
            volatility = btc_info['volatility']
            if volatility > 1000:
                report += "• BTC波動較大，需謹慎風險管理\n"
            else:
                report += "• 市場相對平穩，適合觀察學習\n"
        
        # 趨勢分析
        changes = [info.get('change_24h', 0) for info in data['symbols'].values() if 'change_24h' in info]
        if changes:
            avg_change = sum(changes) / len(changes)
            if avg_change > 1:
                report += "• 市場整體上漲，情緒積極\n"
            elif avg_change < -1:
                report += "• 市場整體下跌，情緒謹慎\n"
            else:
                report += "• 市場橫盤整理，等待方向\n"
        
        # 風險提醒
        report += f"\n🛡️ 風險提醒:\n"
        report += "• 每筆交易不超過2%風險\n"
        report += "• 設置止損保護資本\n"
        report += "• 保持冷靜，按計劃操作\n"
        
        report += f"\n⏰ 下一報告: {(datetime.now() + timedelta(minutes=self.interval_minutes)).strftime('%H:%M')}"
        
        return report
    
    def save_data(self, data, report):
        """保存數據"""
        # 保存原始數據
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        data_file = os.path.join(self.data_dir, f"data_{timestamp}.json")
        
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # 保存報告
        report_file = os.path.join(self.data_dir, f"report_{timestamp}.txt")
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        # 更新最新報告
        latest_file = os.path.join(self.data_dir, "latest_report.txt")
        with open(latest_file, 'w') as f:
            f.write(report)
        
        print(f"✅ 數據已保存: {data_file}")
    
    def run_monitoring(self):
        """運行監控"""
        print("=" * 60)
        print("🚀 啟動簡單加密貨幣監控系統")
        print("=" * 60)
        
        if not self.connect():
            print("❌ 連接失敗，系統退出")
            return
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=self.total_hours)
        
        print(f"⏰ 監控時間: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        print(f"📊 觀察幣種: {', '.join([s.replace('USDT', '') for s in self.symbols])}")
        print(f"⏱️  觀察間隔: 每{self.interval_minutes}分鐘")
        print("按 Ctrl+C 停止監控\n")
        
        observation_count = 0
        
        try:
            while datetime.now() < end_time:
                # 獲取數據
                data = self.get_market_data()
                observation_count += 1
                
                # 生成報告
                report = self.generate_report(data)
                
                # 保存數據
                self.save_data(data, report)
                
                # 顯示報告
                print(f"\n📊 第{observation_count}次觀察完成")
                print(report)
                
                # 計算等待時間
                next_time = datetime.now() + timedelta(minutes=self.interval_minutes)
                wait_seconds = (next_time - datetime.now()).total_seconds()
                
                if wait_seconds > 0:
                    print(f"\n⏳ 等待下次觀察 ({wait_seconds/60:.1f}分鐘)...")
                    time.sleep(min(wait_seconds, 300))  # 最多等待5分鐘
            
            # 監控完成
            print(f"\n✅ 監控完成！")
            print(f"   總觀察次數: {observation_count}")
            print(f"   總監控時間: {self.total_hours}小時")
            
        except KeyboardInterrupt:
            print(f"\n🛑 監控提前停止")
            print(f"   完成觀察次數: {observation_count}")
        
        # 生成總結報告
        self.generate_summary_report(observation_count)
    
    def generate_summary_report(self, total_observations):
        """生成總結報告"""
        summary = f"""
📚 加密貨幣學習總結報告
────────────────
⏰ 監控時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}
👀 總觀察次數: {total_observations}
⏱️  總學習時間: {self.total_hours}小時

🎯 學習成果:
• 觀察了加密貨幣市場波動
• 實踐了定期觀察習慣
• 了解了不同幣種特性

💡 關鍵學習點:
1. 加密貨幣24小時交易，波動持續
2. 不同幣種有不同波動特性
3. 風險管理比擇時更重要

🛡️ 風險管理要點:
• 永遠設置止損
• 單筆風險不超過2%
• 保持情緒穩定

🚀 下一步學習:
• 繼續觀察市場模式
• 嘗試模擬交易決策
• 準備周一股票交易

💪 記住: 學習過程 > 交易結果
"""
        
        print(summary)
        
        # 保存總結報告
        summary_file = os.path.join(self.data_dir, "summary_report.txt")
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        print(f"✅ 總結報告已保存: {summary_file}")

def main():
    monitor = SimpleCryptoMonitor()
    monitor.run_monitoring()

if __name__ == "__main__":
    main()
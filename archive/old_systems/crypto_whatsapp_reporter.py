#!/usr/bin/env python3
"""
加密貨幣WhatsApp報告生成器
定時生成並發送學習報告
"""

from binance.client import Client
from datetime import datetime, timedelta
import json
import os
import time

class CryptoWhatsAppReporter:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = None
        
        # 報告配置
        self.report_interval = 3600  # 1小時
        self.data_dir = "/Users/gordonlui/.openclaw/workspace/crypto_reports"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def connect(self):
        """連接API"""
        try:
            self.client = Client(self.api_key, self.api_secret, testnet=True)
            self.client.get_server_time()  # 測試連接
            return True
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def get_market_summary(self):
        """獲取市場摘要"""
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
        summary = []
        
        for symbol in symbols:
            try:
                ticker = self.client.get_ticker(symbol=symbol)
                summary.append({
                    'symbol': symbol,
                    'price': float(ticker['lastPrice']),
                    'change_24h': float(ticker['priceChangePercent']),
                    'high_24h': float(ticker['highPrice']),
                    'low_24h': float(ticker['lowPrice']),
                    'volume': float(ticker['volume'])
                })
            except:
                continue
        
        return summary
    
    def get_account_status(self):
        """獲取賬戶狀態"""
        try:
            account = self.client.get_account()
            
            # 計算總資產
            total_usdt = 0
            positions = []
            
            for balance in account['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0:
                    asset = balance['asset']
                    
                    if asset == 'USDT':
                        total_usdt += total
                        positions.append(f"USDT: ${total:.2f}")
                    else:
                        symbol = asset + 'USDT'
                        try:
                            ticker = self.client.get_symbol_ticker(symbol=symbol)
                            price = float(ticker['price'])
                            value = total * price
                            total_usdt += value
                            
                            if value > 10:  # 只顯示價值大於$10的持倉
                                positions.append(f"{asset}: {total:.4f} (${value:.2f})")
                        except:
                            positions.append(f"{asset}: {total:.4f}")
            
            return {
                'total_usdt': total_usdt,
                'positions': positions,
                'position_count': len([p for p in positions if '(' in p])  # 計算加密貨幣持倉數量
            }
            
        except Exception as e:
            print(f"❌ 獲取賬戶狀態失敗: {e}")
            return None
    
    def generate_whatsapp_report(self):
        """生成WhatsApp格式報告"""
        now = datetime.now()
        
        # 獲取數據
        market = self.get_market_summary()
        account = self.get_account_status()
        
        if not market or not account:
            return "❌ 無法生成報告：數據獲取失敗"
        
        # 構建報告
        report_lines = []
        
        # 標題
        report_lines.append(f"📊 加密貨幣學習報告")
        report_lines.append(f"⏰ {now.strftime('%Y-%m-%d %H:%M')}")
        report_lines.append("─" * 30)
        
        # 市場概況
        report_lines.append(f"🌐 市場概況:")
        
        for item in market[:3]:  # 只顯示前3個
            change = item['change_24h']
            emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            report_lines.append(f"  {item['symbol']}: ${item['price']:,.2f}")
            report_lines.append(f"    {emoji} {change:+.2f}% (24h)")
        
        # 賬戶狀態
        report_lines.append(f"\n💰 賬戶狀態:")
        report_lines.append(f"  總資產: ${account['total_usdt']:,.2f}")
        report_lines.append(f"  持倉數量: {account['position_count']}個")
        
        if account['positions']:
            report_lines.append(f"  主要持倉:")
            for pos in account['positions'][:3]:  # 只顯示前3個
                report_lines.append(f"    • {pos}")
        
        # 風險管理
        max_risk = account['total_usdt'] * 0.02
        report_lines.append(f"\n🛡️ 風險管理:")
        report_lines.append(f"  2%止損限額: ${max_risk:,.2f}")
        
        # 學習進度
        report_lines.append(f"\n🎯 學習進度:")
        report_lines.append(f"  • API操作: ✅ 已掌握")
        report_lines.append(f"  • 市場分析: 🔄 進行中")
        report_lines.append(f"  • 風險管理: 🔄 實踐中")
        report_lines.append(f"  • 24小時交易: 🕒 適應中")
        
        # 下一報告時間
        next_report = now + timedelta(hours=1)
        report_lines.append(f"\n⏰ 下一報告: {next_report.strftime('%H:%M')}")
        
        return "\n".join(report_lines)
    
    def generate_detailed_report(self):
        """生成詳細報告（用於保存）"""
        now = datetime.now()
        
        market = self.get_market_summary()
        account = self.get_account_status()
        
        report = {
            'timestamp': now.isoformat(),
            'market_summary': market,
            'account_status': account,
            'risk_management': {
                'total_capital': account['total_usdt'] if account else 0,
                'max_risk_per_trade': (account['total_usdt'] * 0.02) if account else 0,
                'risk_percentage': 2
            }
        }
        
        return report
    
    def save_report(self, report):
        """保存報告到文件"""
        try:
            # 按日期保存
            date_str = datetime.now().strftime('%Y-%m-%d')
            report_file = os.path.join(self.data_dir, f"report_{date_str}.json")
            
            # 讀取現有報告
            if os.path.exists(report_file):
                with open(report_file, 'r') as f:
                    existing_reports = json.load(f)
            else:
                existing_reports = []
            
            # 添加新報告
            existing_reports.append(report)
            
            # 保存
            with open(report_file, 'w') as f:
                json.dump(existing_reports, f, indent=2)
            
            print(f"💾 報告已保存: {report_file}")
            
        except Exception as e:
            print(f"❌ 保存報告失敗: {e}")
    
    def run_reporting_service(self):
        """運行報告服務"""
        print("🚀 啟動加密貨幣WhatsApp報告服務")
        print("=" * 60)
        
        if not self.connect():
            print("❌ 連接失敗，服務停止")
            return
        
        print("✅ 連接成功")
        print(f"📅 報告間隔: 每{self.report_interval//3600}小時")
        print("🔧 按Ctrl+C停止服務")
        print("\n開始生成報告...")
        
        last_report_time = datetime.now()
        
        try:
            while True:
                current_time = datetime.now()
                
                # 檢查是否到達報告時間
                if (current_time - last_report_time).seconds >= self.report_interval:
                    print(f"\n⏰ {current_time.strftime('%H:%M:%S')} - 生成報告")
                    
                    # 生成報告
                    whatsapp_report = self.generate_whatsapp_report()
                    detailed_report = self.generate_detailed_report()
                    
                    # 顯示報告
                    print("\n" + "=" * 60)
                    print(whatsapp_report)
                    print("=" * 60)
                    
                    # 保存詳細報告
                    self.save_report(detailed_report)
                    
                    # 更新時間
                    last_report_time = current_time
                    
                    print(f"\n✅ 報告生成完成")
                    print(f"⏰ 下一報告: {(current_time + timedelta(seconds=self.report_interval)).strftime('%H:%M')}")
                
                # 等待下一分鐘
                time.sleep(60)
                
        except KeyboardInterrupt:
            print("\n\n🛑 報告服務停止")
            
            # 生成最終報告
            final_report = self.generate_whatsapp_report()
            print("\n" + "=" * 60)
            print("📋 最終報告")
            print("=" * 60)
            print(final_report)
    
    def send_test_report(self):
        """發送測試報告"""
        print("🧪 生成測試報告...")
        
        if not self.connect():
            return
        
        report = self.generate_whatsapp_report()
        
        print("\n" + "=" * 60)
        print("📱 WhatsApp測試報告")
        print("=" * 60)
        print(report)
        print("=" * 60)
        
        print("\n📋 報告內容:")
        print("• 市場概況 (BTC/ETH/BNB)")
        print("• 賬戶狀態 (總資產/持倉)")
        print("• 風險管理 (2%止損)")
        print("• 學習進度")
        print("• 下一報告時間")
        
        return report

def main():
    print("📱 加密貨幣WhatsApp報告生成器")
    print("=" * 60)
    
    # API密鑰
    api_key = "05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV"
    api_secret = "YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj"
    
    reporter = CryptoWhatsAppReporter(api_key, api_secret)
    
    print("選擇模式:")
    print("1. 測試報告 (單次)")
    print("2. 持續服務 (每小時自動)")
    print("3. 退出")
    
    choice = input("\n請選擇 (1-3): ").strip()
    
    if choice == "1":
        reporter.send_test_report()
    elif choice == "2":
        print("\n🚀 啟動持續報告服務...")
        print("報告將每小時自動生成")
        print("按Ctrl+C停止")
        reporter.run_reporting_service()
    else:
        print("退出")

if __name__ == "__main__":
    main()
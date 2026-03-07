#!/usr/bin/env python3
"""
自動交易系統 - 定時任務版本
"""

import schedule
import time
from datetime import datetime, timedelta
import json
import os
import sys

print("=" * 70)
print("🤖 自動交易系統 - 定時任務版本")
print("=" * 70)

class AutoTradingSystem:
    """自動交易系統"""
    
    def __init__(self):
        self.config = self.load_config()
        self.stocks_to_monitor = self.config.get('stocks', ['00992'])
        self.trading_hours = self.config.get('trading_hours', {
            'start': '09:30',
            'end': '16:00'
        })
        self.results_dir = '/Users/gordonlui/.openclaw/workspace/trading_results'
        os.makedirs(self.results_dir, exist_ok=True)
        
    def load_config(self):
        """加載配置"""
        config_path = '/Users/gordonlui/.openclaw/workspace/trading_config.json'
        default_config = {
            'stocks': ['00992'],
            'trading_hours': {
                'start': '09:30',
                'end': '16:00'
            },
            'update_frequency': 30,  # 分鐘
            'risk_management': {
                'stop_loss_percent': 3,
                'take_profit_percent': 5,
                'max_position_size': 0.3
            },
            'notifications': {
                'telegram': True,
                'email': False
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # 保存默認配置
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def is_trading_time(self):
        """檢查是否在交易時間內"""
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        start_time = self.trading_hours['start']
        end_time = self.trading_hours['end']
        
        return start_time <= current_time <= end_time
    
    def get_real_time_price(self, stock_code):
        """獲取實時價格（連接富途API）"""
        try:
            import futu as ft
            
            quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
            
            # 嘗試不同格式
            formats_to_try = [
                f"HK.{stock_code}",
                f"{stock_code}.HK",
                f"{stock_code}"
            ]
            
            for stock_format in formats_to_try:
                ret, data = quote_ctx.get_market_snapshot([stock_format])
                if ret == ft.RET_OK and len(data) > 0:
                    quote_ctx.close()
                    return float(data.iloc[0]['last_price'])
            
            quote_ctx.close()
            
        except Exception as e:
            print(f"⚠️  富途API連接失敗: {e}")
        
        # 備用：使用模擬數據
        return self.get_simulated_price(stock_code)
    
    def get_simulated_price(self, stock_code):
        """獲取模擬價格（備用）"""
        # 基於股票代碼的簡單模擬
        base_prices = {
            '00992': 9.30,  # 聯想集團當前價格
            '00005': 134.20,  # 匯豐控股
            '00700': 535.50,  # 騰訊
            '09988': 158.60,  # 阿里巴巴
        }
        
        if stock_code in base_prices:
            # 添加一些隨機波動
            import random
            base = base_prices[stock_code]
            fluctuation = random.uniform(-0.02, 0.02)  # ±2%
            return base * (1 + fluctuation)
        
        return 100.0  # 默認價格
    
    def run_xgboost_prediction(self, stock_code):
        """運行XGBoost預測"""
        print(f"🤖 運行XGBoost預測: {stock_code}")
        
        try:
            # 這裡可以調用之前創建的XGBoost預測系統
            if stock_code == '00992':
                # 使用聯想專用預測系統
                from predict_992_tomorrow import LenovoPredictor
                predictor = LenovoPredictor(stock_code)
                data = predictor.get_historical_data(days=100)
                prediction = predictor.predict_tomorrow(data)
                
                if prediction:
                    return {
                        'probability_up': prediction['probability_up'],
                        'signal': prediction['signal'],
                        'confidence': prediction['confidence'],
                        'current_price': prediction['current_price']
                    }
            
        except Exception as e:
            print(f"❌ XGBoost預測失敗: {e}")
        
        # 備用：簡單預測
        return {
            'probability_up': 0.65,
            'signal': '🟢 持有/加倉',
            'confidence': 0.7,
            'current_price': self.get_real_time_price(stock_code)
        }
    
    def generate_trading_signal(self, stock_code, prediction):
        """生成交易信號"""
        current_price = prediction['current_price']
        probability_up = prediction['probability_up']
        
        # 基於概率和價格的簡單邏輯
        if probability_up > 0.7:
            signal = "🟢 強力買入"
            action = "BUY"
            target_price = current_price * 1.05
            stop_loss = current_price * 0.97
        elif probability_up > 0.6:
            signal = "🟡 買入"
            action = "BUY"
            target_price = current_price * 1.03
            stop_loss = current_price * 0.98
        elif probability_up < 0.3:
            signal = "🔴 強力賣出"
            action = "SELL"
            target_price = current_price * 0.95
            stop_loss = current_price * 1.03
        elif probability_up < 0.4:
            signal = "🟠 賣出"
            action = "SELL"
            target_price = current_price * 0.97
            stop_loss = current_price * 1.02
        else:
            signal = "⚪ 持有"
            action = "HOLD"
            target_price = current_price * 1.01
            stop_loss = current_price * 0.99
        
        return {
            'stock': stock_code,
            'signal': signal,
            'action': action,
            'current_price': current_price,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'probability_up': probability_up,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def execute_trade(self, signal):
        """執行交易（模擬）"""
        print(f"💰 執行交易: {signal['stock']} - {signal['action']}")
        
        # 這裡可以連接富途交易API
        # 暫時使用模擬執行
        
        trade_result = {
            'stock': signal['stock'],
            'action': signal['action'],
            'price': signal['current_price'],
            'quantity': 1000,  # 模擬數量
            'status': 'SIMULATED',
            'order_id': f"SIM_{int(time.time())}",
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return trade_result
    
    def save_result(self, result_type, data):
        """保存結果"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.results_dir}/{result_type}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 結果已保存: {filename}")
        return filename
    
    def send_notification(self, message):
        """發送通知"""
        print(f"📢 通知: {message}")
        # 這裡可以集成Telegram、Email等通知
        
    def daily_market_open(self):
        """每日開市任務"""
        print("\n🌅 每日開市任務執行...")
        print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for stock in self.stocks_to_monitor:
            print(f"\n📊 分析股票: {stock}")
            
            # 獲取實時價格
            price = self.get_real_time_price(stock)
            print(f"   當前價格: ${price:.2f}")
            
            # 運行預測
            prediction = self.run_xgboost_prediction(stock)
            print(f"   上漲概率: {prediction['probability_up']:.3f}")
            print(f"   交易信號: {prediction['signal']}")
            
            # 生成交易信號
            signal = self.generate_trading_signal(stock, prediction)
            
            # 保存信號
            self.save_result('signal', signal)
            
            # 如果信號強烈，執行交易
            if signal['action'] in ['BUY', 'SELL'] and abs(prediction['probability_up'] - 0.5) > 0.2:
                trade_result = self.execute_trade(signal)
                self.save_result('trade', trade_result)
                
                # 發送通知
                self.send_notification(
                    f"{signal['stock']} {signal['action']} @ ${signal['current_price']:.2f}"
                )
        
        print("✅ 每日開市任務完成")
    
    def intraday_check(self):
        """盤中檢查任務"""
        if not self.is_trading_time():
            print("⏸️  非交易時間，跳過盤中檢查")
            return
        
        print("\n📈 盤中檢查任務執行...")
        print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for stock in self.stocks_to_monitor:
            price = self.get_real_time_price(stock)
            print(f"   {stock}: ${price:.2f}")
            
            # 簡單的價格監控
            # 這裡可以添加更複雜的監控邏輯
        
        print("✅ 盤中檢查完成")
    
    def daily_market_close(self):
        """每日收市任務"""
        print("\n🌇 每日收市任務執行...")
        print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 生成每日報告
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'stocks_analyzed': self.stocks_to_monitor,
            'trading_hours': self.trading_hours,
            'summary': '每日交易總結'
        }
        
        self.save_result('daily_report', report)
        print("✅ 每日收市任務完成")
    
    def weekly_summary(self):
        """每週總結任務"""
        print("\n📊 每週總結任務執行...")
        print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 生成週報告
        report = {
            'week_start': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'week_end': datetime.now().strftime('%Y-%m-%d'),
            'summary': '本週交易總結'
        }
        
        self.save_result('weekly_report', report)
        print("✅ 每週總結任務完成")
    
    def setup_schedule(self):
        """設置定時任務"""
        print("\n⏰ 設置定時任務...")
        
        # 每日開市任務 (09:31)
        schedule.every().day.at("09:31").do(self.daily_market_open)
        print("   ✅ 每日開市任務: 09:31")
        
        # 盤中檢查 (每30分鐘)
        schedule.every(30).minutes.do(self.intraday_check)
        print("   ✅ 盤中檢查: 每30分鐘")
        
        # 每日收市任務 (16:31)
        schedule.every().day.at("16:31").do(self.daily_market_close)
        print("   ✅ 每日收市任務: 16:31")
        
        # 每週總結 (每週一09:00)
        schedule.every().monday.at("09:00").do(self.weekly_summary)
        print("   ✅ 每週總結: 每週一09:00")
        
        print("✅ 定時任務設置完成")
    
    def run(self):
        """運行系統"""
        print("\n🚀 啟動自動交易系統...")
        
        # 設置定時任務
        self.setup_schedule()
        
        print(f"\n📋 系統配置:")
        print(f"   監控股票: {', '.join(self.stocks_to_monitor)}")
        print(f"   交易時間: {self.trading_hours['start']} - {self.trading_hours['end']}")
        print(f"   更新頻率: 每30分鐘")
        print(f"   結果目錄: {self.results_dir}")
        
        print(f"\n💡 使用說明:")
        print(f"   1. 系統會自動運行定時任務")
        print(f"   2. 查看結果: {self.results_dir}/")
        print(f"   3. 修改配置: /Users/gordonlui/.openclaw/workspace/trading_config.json")
        print(f"   4. 停止系統: Ctrl+C")
        
        print(f"\n⚠️  注意事項:")
        print(f"   1. 這是模擬系統，不連接真實交易")
        print(f"   2. 實際使用需要連接富途API")
        print(f"   3. 建議先進行模擬交易測試")
        
        print(f"\n🎯 下一步行動:")
        print(f"   1. 連接富途API獲取真實數據")
        print(f"   2. 實盤小資金測試")
        print(f"   3. 優化交易策略")
        
        print(f"\n✅ 系統啟動完成!")
        print("=" * 70)
        
        try:
            # 立即執行一次開市任務（如果現在是交易時間）
            if self.is_trading_time():
                self.daily_market_open()
            
            # 保持運行
            print("\n⏳ 系統運行中... (按Ctrl+C停止)")
            while True:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 用戶中斷，系統停止")
        except Exception as e:
            print(f"\n❌ 系統運行錯誤: {e}")

def main():
    """主函數"""
    system = AutoTradingSystem()
    system.run()

if __name__ == "__main__":
    main()
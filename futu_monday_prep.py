#!/usr/bin/env python3
"""
富途周一模擬交易準備系統
"""

import sys
import time
import json
from datetime import datetime, timedelta
from futu import *

class FutuSimTrader:
    """富途模擬交易器"""
    
    def __init__(self):
        self.trd_ctx = None
        self.quote_ctx = None
        self.initial_capital = 979000  # 初始資金
        self.risk_per_trade = 0.02  # 每筆2%風險
        
    def connect(self):
        """連接富途API"""
        print("🔗 連接富途API...")
        try:
            self.trd_ctx = OpenSecTradeContext(
                host='127.0.0.1',
                port=11111,
                security_firm=SecurityFirm.FUTUSECURITIES
            )
            print("✅ 交易連接成功")
            
            self.quote_ctx = OpenQuoteContext(
                host='127.0.0.1',
                port=11111
            )
            print("✅ 報價連接成功")
            
            return True
            
        except Exception as e:
            print(f"❌ 連接失敗: {e}")
            return False
    
    def check_sim_account(self):
        """檢查模擬賬戶"""
        print("\n📋 檢查模擬賬戶...")
        
        try:
            # 1. 檢查持倉
            print("1. 檢查持倉...")
            ret, positions = self.trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
            
            if ret == RET_OK:
                if len(positions) > 0:
                    print(f"  找到 {len(positions)} 個持倉:")
                    total_value = 0
                    for idx, row in positions.iterrows():
                        market_val = row.get('market_val', 0)
                        total_value += market_val
                        print(f"    {row['code']}: {row['qty']}股, 市值: HKD {market_val:,.2f}")
                    print(f"  持倉總市值: HKD {total_value:,.2f}")
                else:
                    print("  無持倉")
            else:
                print(f"  獲取持倉失敗: {positions}")
            
            # 2. 檢查資金（使用正確的方法）
            print("\n2. 檢查資金信息...")
            ret, data = self.trd_ctx.get_acc_assets(trd_env=TrdEnv.SIMULATE)
            
            if ret == RET_OK and not data.empty:
                print("  資金數據:")
                print(data)
                
                # 嘗試提取關鍵信息
                for col in data.columns:
                    print(f"  {col}: {data[col].iloc[0]}")
            
            # 3. 檢查賬戶列表
            print("\n3. 檢查賬戶列表...")
            ret, accounts = self.trd_ctx.get_acc_list()
            
            if ret == RET_OK:
                print(f"  找到 {len(accounts)} 個賬戶")
                print(accounts)
            
            return True
            
        except Exception as e:
            print(f"❌ 檢查賬戶失敗: {e}")
            return False
    
    def calculate_position_size(self, entry_price, stop_loss_price):
        """計算符合2%風險的倉位大小"""
        risk_per_share = abs(entry_price - stop_loss_price)
        
        if risk_per_share <= 0:
            return 0
        
        # 每筆最大風險金額
        max_risk_amount = self.initial_capital * self.risk_per_trade
        
        # 計算可買數量
        max_shares = int(max_risk_amount / risk_per_share)
        
        return max_shares
    
    def get_market_data(self, symbol):
        """獲取市場數據"""
        try:
            ret, data = self.quote_ctx.get_market_snapshot([symbol])
            if ret == RET_OK and not data.empty:
                return data.iloc[0]
            return None
        except:
            return None
    
    def prepare_monday_plan(self):
        """準備周一交易計劃"""
        print("\n🎯 準備周一交易計劃")
        print("=" * 60)
        
        plan = {
            "start_date": "2026-02-09",
            "trading_hours": "09:30-16:00",
            "initial_capital": self.initial_capital,
            "risk_per_trade": self.risk_per_trade,
            "monitoring_interval": 30,  # 分鐘
            "products_to_watch": [
                "HK.999010",  # 恆生指數
                "HK.02800",   # 盈富基金
                "HK.02828",   # 恆生中國企業ETF
                # 可以添加牛熊證代碼
            ],
            "trading_rules": {
                "max_positions": 3,
                "stop_loss": "2% of capital",
                "take_profit": "risk_reward_1_2",
                "position_sizing": "calculated_by_risk"
            },
            "monitoring_schedule": [
                "09:30", "10:00", "10:30", "11:00", "11:30",
                "12:00", "13:00", "13:30", "14:00", "14:30",
                "15:00", "15:30", "16:00"
            ]
        }
        
        print("📅 交易時間: 09:30-16:00")
        print("💰 初始資金: HKD 979,000")
        print("⚠️  每筆風險: 2% (HKD 19,580)")
        print("⏰ 監控頻率: 每30分鐘")
        
        print("\n📊 關注產品:")
        for product in plan["products_to_watch"]:
            print(f"  • {product}")
        
        print("\n📋 交易規則:")
        print("  1. 最大持倉: 3個")
        print("  2. 止損: 每筆不超過總資金2%")
        print("  3. 獲利: 風險回報比至少1:2")
        print("  4. 倉位計算: 基於風險計算")
        
        # 保存計劃
        with open('monday_trading_plan.json', 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 交易計劃已保存: monday_trading_plan.json")
        
        return plan
    
    def create_monitoring_script(self):
        """創建監控腳本"""
        script_content = '''#!/usr/bin/env python3
"""
富途模擬交易監控腳本
每30分鐘運行一次
"""

import sys
import time
import json
from datetime import datetime
from futu import *

def monitor_portfolio():
    """監控投資組合"""
    print(f"📊 監控時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # 連接
        trd_ctx = OpenSecTradeContext(
            host='127.0.0.1',
            port=11111,
            security_firm=SecurityFirm.FUTUSECURITIES
        )
        
        # 檢查持倉
        ret, positions = trd_ctx.position_list_query(trd_env=TrdEnv.SIMULATE)
        
        if ret == RET_OK and len(positions) > 0:
            print(f"📦 當前持倉 ({len(positions)}個):")
            
            total_pnl = 0
            total_value = 0
            
            for idx, row in positions.iterrows():
                code = row['code']
                qty = row['qty']
                cost = row.get('cost_price', 0)
                market_val = row.get('market_val', 0)
                pnl = row.get('pl_ratio', 0)  # 盈虧百分比
                
                print(f"  {code}: {qty}股")
                print(f"    成本: {cost:.2f}, 市值: {market_val:,.2f}")
                print(f"    盈虧: {pnl:.2f}%")
                
                total_pnl += pnl
                total_value += market_val
            
            print(f"\\n💰 持倉總市值: HKD {total_value:,.2f}")
            print(f"📈 總盈虧: {total_pnl:.2f}%")
        else:
            print("📭 無持倉")
        
        trd_ctx.close()
        
    except Exception as e:
        print(f"❌ 監控錯誤: {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    monitor_portfolio()
'''
        
        with open('futu_monitor.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print("📜 監控腳本已創建: futu_monitor.py")
        print("  運行: python3 futu_monitor.py")
        
        # 創建定時任務說明
        cron_guide = '''# 設置每30分鐘運行監控
# 在Terminal中執行:
crontab -e

# 添加這行（交易時間 09:30-16:00）:
30,0 9-15 * * 1-5 cd /path/to/workspace && python3 futu_monitor.py >> trading_log.txt

# 或者手動運行:
python3 futu_monitor.py
'''
        
        with open('cron_setup.txt', 'w', encoding='utf-8') as f:
            f.write(cron_guide)
        
        print("⏰ 定時任務指南: cron_setup.txt")
    
    def close(self):
        """關閉連接"""
        if self.trd_ctx:
            self.trd_ctx.close()
        if self.quote_ctx:
            self.quote_ctx.close()
        print("🔒 連接已關閉")

def main():
    print("🚀 富途周一模擬交易準備系統")
    print("=" * 60)
    print("準備時間:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("目標: 為2026-02-09周一交易做好準備")
    print("=" * 60)
    
    trader = FutuSimTrader()
    
    # 1. 連接測試
    if not trader.connect():
        print("❌ 無法連接，請檢查:")
        print("   1. 富途牛牛是否運行")
        print("   2. OpenD是否啟動")
        print("   3. 網絡連接")
        return
    
    # 2. 檢查賬戶
    print("\n" + "=" * 60)
    trader.check_sim_account()
    
    # 3. 準備交易計劃
    print("\n" + "=" * 60)
    plan = trader.prepare_monday_plan()
    
    # 4. 創建監控系統
    print("\n" + "=" * 60)
    trader.create_monitoring_script()
    
    # 5. 創建風險計算示例
    print("\n" + "=" * 60)
    print("📐 風險計算示例:")
    print("初始資金: HKD 979,000")
    print("每筆最大風險: 979,000 × 2% = HKD 19,580")
    print()
    print("例子: 買入價格100，止損95")
    print("  每股風險: 100 - 95 = 5")
    print("  可買股數: 19,580 ÷ 5 = 3,916股")
    print("  倉位價值: 3,916 × 100 = HKD 391,600 (約40%資金)")
    
    # 6. 關閉連接
    trader.close()
    
    print("\n" + "=" * 60)
    print("🎉 周一交易準備完成！")
    print()
    print("📁 創建的文件:")
    print("  1. monday_trading_plan.json - 交易計劃")
    print("  2. futu_monitor.py - 監控腳本")
    print("  3. cron_setup.txt - 定時任務指南")
    print()
    print("🚀 周一操作:")
    print("  1. 09:15 - 啟動系統，檢查市場")
    print("  2. 09:30 - 開始交易")
    print("  3. 每30分鐘 - 運行監控")
    print("  4. 16:00 - 結束交易，記錄總結")
    print()
    print("⚠️  重要提醒:")
    print("  • 嚴格執行2%止損")
    print("  • 每筆交易前計算風險")
    print("  • 記錄每筆交易和分析")
    print("  • 保持紀律，不情緒化交易")
    
    print("\n" + "=" * 60)
    print("準備完成時間:", datetime.now().strftime("%H:%M:%S"))

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
OANDA黃金自動交易啟動腳本
在Mac上直接運行，無需虛擬機
"""

import sys
import os
import json
import time
import schedule
from datetime import datetime
from oanda_trader_final import OANDAGoldTrader

def run_trading_cycle():
    """運行交易週期"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 開始OANDA交易週期檢查")
    
    try:
        # 使用模擬賬戶
        trader = OANDAGoldTrader(use_demo=True)
        
        # 檢查交易時間
        if not trader.check_trading_hours():
            print(f"[{datetime.now().strftime('%H:%M')}] 非主要交易時段，跳過檢查")
            return
        
        # 檢查現有持倉
        positions = trader.check_existing_positions()
        max_positions = trader.config.get('max_concurrent_trades', 2)
        
        if positions >= max_positions:
            print(f"[{datetime.now().strftime('%H:%M')}] 已達最大持倉限制: {positions}/{max_positions}")
            return
        
        # 獲取市場數據
        data = trader.get_market_data()
        if data is None:
            print(f"[{datetime.now().strftime('%H:%M')}] 無法獲取市場數據")
            return
        
        df, current_data = data
        
        # 分析市場，生成信號
        signal = trader.analyze_market(df, current_data)
        
        if signal:
            # 執行交易
            success = trader.execute_trade(signal)
            
            if success:
                print(f"[{datetime.now().strftime('%H:%M')}] ✅ 交易執行成功: {signal['type']}")
            else:
                print(f"[{datetime.now().strftime('%H:%M')}] ❌ 交易執行失敗")
        else:
            print(f"[{datetime.now().strftime('%H:%M')}] ⏸️  無交易信號")
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M')}] ❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

def setup_scheduler():
    """設置定時任務"""
    print("=" * 70)
    print("📅 OANDA黃金自動交易調度器")
    print("=" * 70)
    
    # 黃金主要交易時段（GMT+8）
    trading_hours = [
        "09:30",  # 亞洲開盤
        "10:30",
        "11:30",
        "12:30",
        "13:30",
        "14:30",
        "15:30",  # 倫敦開盤
        "16:30",
        "17:30",
        "18:30",
        "19:30",
        "20:30",  # 紐約開盤
        "21:30",
        "22:30",
        "23:30",
        "00:30",
        "01:30",
        "02:30",
        "03:30",
        "04:30",
    ]
    
    # 註冊定時任務
    for hour in trading_hours:
        schedule.every().day.at(hour).do(run_trading_cycle)
        print(f"  已註冊: 每天 {hour} 運行交易檢查")
    
    print(f"\n總計: {len(trading_hours)} 個交易檢查點")
    print("\n📊 交易時段分佈:")
    print("   亞洲時段: 09:30-14:30 (6次)")
    print("   倫敦時段: 15:30-19:30 (5次)")
    print("   紐約時段: 20:30-04:30 (9次)")
    
    return schedule

def check_system_status():
    """檢查系統狀態"""
    print("\n🔍 系統狀態檢查:")
    print("-" * 40)
    
    # 檢查Python包
    packages = ['pandas', 'numpy', 'oandapyV20']
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}: 已安裝")
        except ImportError:
            print(f"❌ {package}: 未安裝")
    
    # 檢查配置文件
    config_files = [
        ("oanda_config.json", "OANDA配置"),
        ("optimized_strategy.json", "策略配置"),
        ("gold_trades_log.json", "交易記錄")
    ]
    
    for file, desc in config_files:
        path = f"/Users/gordonlui/.openclaw/workspace/{file}"
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {desc}: {size} 字節")
        else:
            print(f"⚠️  {desc}: 未找到")
    
    # 檢查日誌目錄
    log_dir = "/Users/gordonlui/.openclaw/workspace/logs"
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        print(f"✅ 日誌目錄: {len(log_files)} 個日誌文件")
    else:
        print(f"⚠️  日誌目錄不存在")

def setup_oanda_account_guide():
    """OANDA賬戶設置指南"""
    print("\n" + "=" * 70)
    print("📝 OANDA賬戶設置指南")
    print("=" * 70)
    
    steps = [
        "第1步: 註冊OANDA賬戶",
        "   1. 訪問 https://www.oanda.com/",
        "   2. 點擊'開設模擬賬戶'",
        "   3. 填寫註冊信息",
        "   4. 完成郵箱驗證",
        "",
        "第2步: 獲取API密鑰",
        "   1. 登錄OANDA賬戶",
        "   2. 進入'我的資金' → '管理API訪問'",
        "   3. 點擊'生成新的API密鑰'",
        "   4. 複製API密鑰和賬戶ID",
        "",
        "第3步: 配置系統",
        "   1. 編輯配置文件:",
        "      nano /Users/gordonlui/.openclaw/workspace/oanda_config.json",
        "   2. 填入你的API密鑰和賬戶ID",
        "   3. 保存文件",
        "",
        "第4步: 安裝Python包",
        "   pip install oandapyV20 pandas numpy schedule",
        "",
        "第5步: 測試系統",
        "   python start_oanda_trader.py --test",
    ]
    
    for step in steps:
        print(f"   {step}")

def main():
    """主函數"""
    print("=" * 70)
    print("🚀 OANDA黃金自動交易系統 (Mac原生)")
    print("=" * 70)
    
    # 顯示設置指南
    setup_oanda_account_guide()
    
    # 檢查系統狀態
    check_system_status()
    
    # 運行模式選擇
    print("\n🎯 選擇運行模式:")
    print("   1. 單次運行 (測試)")
    print("   2. 定時運行 (生產)")
    print("   3. 手動運行 (交互)")
    print("   4. 設置OANDA賬戶")
    
    try:
        choice = input("\n請選擇 (1-4): ").strip()
        
        if choice == "1":
            print("\n🧪 單次測試模式...")
            run_trading_cycle()
            
        elif choice == "2":
            print("\n🏭 定時運行模式...")
            scheduler = setup_scheduler()
            
            print("\n⏰ 調度器已啟動，按 Ctrl+C 停止")
            print("交易將在以下時間自動運行:")
            
            # 顯示下一次運行時間
            next_run = scheduler.next_run
            if next_run:
                print(f"下一次運行: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 主循環
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次
                
                # 每小時顯示狀態
                if datetime.now().minute == 0:
                    print(f"[{datetime.now().strftime('%H:%M')}] 調度器運行中...")
                    
        elif choice == "3":
            print("\n👨‍💻 手動交互模式...")
            
            while True:
                print("\n選項:")
                print("  1. 運行交易檢查")
                print("  2. 查看系統狀態")
                print("  3. 查看日誌")
                print("  4. 測試OANDA連接")
                print("  5. 退出")
                
                sub_choice = input("\n請選擇 (1-5): ").strip()
                
                if sub_choice == "1":
                    run_trading_cycle()
                elif sub_choice == "2":
                    check_system_status()
                elif sub_choice == "3":
                    show_logs()
                elif sub_choice == "4":
                    test_oanda_connection()
                elif sub_choice == "5":
                    print("退出系統")
                    break
                else:
                    print("無效選擇")
                    
        elif choice == "4":
            print("\n🔧 OANDA賬戶設置...")
            setup_oanda_account_guide()
            
            # 創建配置文件模板
            config_path = "/Users/gordonlui/.openclaw/workspace/oanda_config.json"
            if not os.path.exists(config_path):
                template = {
                    "api_key": "YOUR_OANDA_API_KEY_HERE",
                    "account_id": "YOUR_OANDA_ACCOUNT_ID_HERE",
                    "environment": "practice",
                    "symbol": "XAU_USD",
                    "lot_size": 0.01,
                    "max_daily_trades": 3,
                    "max_concurrent_trades": 2
                }
                
                with open(config_path, 'w') as f:
                    json.dump(template, f, indent=2)
                
                print(f"\n✅ 創建配置文件模板: {config_path}")
                print("   請編輯此文件，填入你的OANDA API密鑰")
            else:
                print(f"\n✅ 配置文件已存在: {config_path}")
                
        else:
            print("無效選擇，退出")
            
    except KeyboardInterrupt:
        print("\n\n🛑 用戶中斷")
    except Exception as e:
        print(f"\n❌ 系統錯誤: {e}")
        import traceback
        traceback.print_exc()

def show_logs():
    """顯示日誌"""
    print("\n📝 日誌文件:")
    print("-" * 40)
    
    log_dir = "/Users/gordonlui/.openclaw/workspace/logs"
    
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        
        if log_files:
            print(f"目錄: {log_dir}")
            for log_file in sorted(log_files)[-5:]:  # 最近5個
                path = os.path.join(log_dir, log_file)
                size = os.path.getsize(path)
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
                print(f"  • {log_file} ({size} 字節, 修改: {mtime.strftime('%Y-%m-%d %H:%M')})")
        else:
            print(f"目錄 {log_dir} 中無日誌文件")
    else:
        print(f"日誌目錄不存在: {log_dir}")
    
    # 顯示最新日誌內容
    latest_log = None
    latest_time = 0
    
    if os.path.exists(log_dir):
        for file in os.listdir(log_dir):
            if file.endswith('.log'):
                path = os.path.join(log_dir, file)
                mtime = os.path.getmtime(path)
                if mtime > latest_time:
                    latest_time = mtime
                    latest_log = path
    
    if latest_log:
        print(f"\n📄 最新日誌內容 ({os.path.basename(latest_log)}):")
        print("-" * 40)
        
        try:
            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-20:]  # 最後20行
                for line in lines:
                    print(line.rstrip())
        except:
            print("無法讀取日誌文件")

def test_oanda_connection():
    """測試OANDA連接"""
    print("\n🔗 測試OANDA連接...")
    
    try:
        import oandapyV20
        
        config_path = "/Users/gordonlui/.openclaw/workspace/oanda_config.json"
        if not os.path.exists(config_path):
            print("❌ 配置文件不存在")
            return
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        api_key = config.get('api_key', '')
        account_id = config.get('account_id', '')
        
        if not api_key or api_key == 'YOUR_OANDA_API_KEY_HERE':
            print("❌ API密鑰未設置")
            print("   請編輯 oanda_config.json 文件")
            return
        
        # 測試連接
        client = oandapyV20.API(
            access_token=api_key,
            environment='practice'
        )
        
        r = accounts.AccountDetails(accountID=account_id)
        response = client.request(r)
        
        if 'account' in response:
            account_info = response['account']
            print(f"✅ OANDA連接成功")
            print(f"   賬戶: {account_info['id']}")
            print(f"   餘額: {account_info['balance']} {account_info['currency']}")
            print(f"   環境: practice (模擬)")
        else:
            print(f"❌ OANDA連接失敗")
            print(f"   響應: {response}")
            
    except ImportError:
        print("❌ oandapyV20未安裝")
        print("   安裝: pip install oandapyV20")
    except Exception as e:
        print(f"❌ 連接測試失敗: {e}")

if __name__ == "__main__":
    main()
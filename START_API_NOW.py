#!/usr/bin/env python3
"""
🚀 API方案立即啟動 - 1分鐘開始
"""

import os
import sys
import time
from datetime import datetime

print("=" * 70)
print("🚀 方案D：替代API方案 - 立即啟動")
print("=" * 70)

def show_api_architecture():
    """顯示API架構"""
    print("\n🏗️ API架構圖:")
    print("┌─────────────────────────────────────────────┐")
    print("│           你的Mac (macOS)                   │")
    print("│                │                            │")
    print("│         Python程序 (本地運行)               │")
    print("│                │                            │")
    print("│         HTTPS請求 → OANDA REST API         │")
    print("│                │                            │")
    print("│        全球交易服務器 (OANDA)              │")
    print("└─────────────────────────────────────────────┘")
    
    print("\n✅ 確認: 這是純API方案，無虛擬機！")
    print("   • 無需Windows")
    print("   • 無需虛擬機軟件")
    print("   • 無需MT5安裝")
    print("   • 無需環境配置")

def show_start_options():
    """顯示開始選項"""
    print("\n" + "=" * 70)
    print("🎯 選擇開始方式 (推薦順序):")
    print("=" * 70)
    
    options = [
        {
            "number": "1",
            "title": "⚡ 立即模擬API交易",
            "description": "無需註冊，立即開始學習",
            "command": "python3 instant_trader.py",
            "time": "立即",
            "risk": "零風險",
            "recommended": "★★★★★"
        },
        {
            "number": "2",
            "title": "🌐 註冊OANDA API實盤",
            "description": "使用真實OANDA API",
            "command": "1. 訪問 https://www.oanda.com/\n   2. 獲取API密鑰\n   3. python3 start_oanda_trader.py",
            "time": "5分鐘",
            "risk": "模擬零風險",
            "recommended": "★★★★☆"
        },
        {
            "number": "3",
            "title": "🔧 測試API系統",
            "description": "運行完整系統測試",
            "command": "python3 test_api_only.py",
            "time": "2分鐘",
            "risk": "無風險",
            "recommended": "★★★☆☆"
        },
        {
            "number": "4",
            "title": "📊 查看API文檔",
            "description": "查看詳細API方案文檔",
            "command": "cat PURE_API_SOLUTION.md | head -30",
            "time": "3分鐘",
            "risk": "無風險",
            "recommended": "★★☆☆☆"
        }
    ]
    
    for opt in options:
        print(f"\n{opt['number']}. {opt['title']} {opt['recommended']}")
        print(f"   描述: {opt['description']}")
        print(f"   時間: {opt['time']}")
        print(f"   風險: {opt['risk']}")
        print(f"   命令: {opt['command']}")

def start_instant_simulation():
    """啟動即時模擬"""
    print("\n" + "=" * 70)
    print("⚡ 啟動即時模擬API交易")
    print("=" * 70)
    
    print("\n系統將:")
    print("• 使用模擬市場數據")
    print("• 模擬API通信流程")
    print("• 自動執行交易")
    print("• 記錄所有結果")
    
    print("\n📊 風險控制:")
    print("• 每筆交易: 0.01手")
    print("• 每日最多: 3筆交易")
    print("• 止損: 60點 ($6.00)")
    print("• 止盈: 120點 ($12.00)")
    
    print("\n⏰ 運行時間: 24小時 (每小時檢查一次)")
    print("📝 日誌文件: logs/instant_trader_*.log")
    print("📊 交易記錄: instant_trades.json")
    
    print("\n按 Ctrl+C 停止系統")
    print("-" * 70)
    
    # 檢查文件
    if not os.path.exists("instant_trader.py"):
        print("❌ 錯誤: instant_trader.py 文件不存在")
        return False
    
    # 運行系統
    try:
        import subprocess
        process = subprocess.Popen([sys.executable, "instant_trader.py"])
        
        print("✅ 即時模擬API交易已啟動")
        print("   查看實時日誌: tail -f logs/instant_trader_*.log")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 停止系統...")
            process.terminate()
        
        return True
        
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        return False

def setup_oanda_api():
    """設置OANDA API"""
    print("\n" + "=" * 70)
    print("🌐 設置OANDA API實盤")
    print("=" * 70)
    
    steps = [
        ("第1步: 註冊OANDA賬戶", 
         "訪問: https://www.oanda.com/\n點擊'開設模擬賬戶' (免費)"),
        
        ("第2步: 獲取API密鑰",
         "登錄後: 我的資金 → 管理API訪問\n點擊'生成新的API密鑰'"),
        
        ("第3步: 配置系統",
         "編輯文件: oanda_config.json\n填入你的API密鑰和賬戶ID"),
        
        ("第4步: 開始交易",
         "運行: python3 start_oanda_trader.py"),
    ]
    
    for i, (title, description) in enumerate(steps, 1):
        print(f"\n{i}. {title}")
        print(f"   {description}")
    
    print("\n💡 提示:")
    print("• 先用模擬賬戶測試1-2週")
    print("• 嚴格遵守0.01手限制")
    print("• 從小資金開始 ($100-500)")
    
    # 打開瀏覽器
    open_browser = input("\n是否打開OANDA網站？(y/n): ").strip().lower()
    if open_browser == 'y':
        import webbrowser
        webbrowser.open("https://www.oanda.com/")
        print("✅ 瀏覽器已打開")
    
    return True

def test_api_system():
    """測試API系統"""
    print("\n" + "=" * 70)
    print("🔧 測試API系統")
    print("=" * 70)
    
    if not os.path.exists("test_api_only.py"):
        print("❌ 錯誤: test_api_only.py 文件不存在")
        return False
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "test_api_only.py"], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("✅ API系統測試通過")
            return True
        else:
            print("❌ API系統測試失敗")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def show_api_documentation():
    """顯示API文檔"""
    print("\n" + "=" * 70)
    print("📊 API方案文檔")
    print("=" * 70)
    
    docs = [
        ("PURE_API_SOLUTION.md", "純API方案詳細說明"),
        ("OANDA_REGISTRATION_GUIDE.md", "OANDA註冊指南"),
        ("ALTERNATIVE_API_GUIDE.md", "替代API技術指南"),
    ]
    
    for filename, description in docs:
        path = f"/Users/gordonlui/.openclaw/workspace/{filename}"
        
        if os.path.exists(path):
            print(f"\n📄 {description}:")
            print(f"   文件: {filename}")
            
            # 顯示前5行
            try:
                with open(path, 'r') as f:
                    lines = []
                    for i in range(10):
                        line = f.readline()
                        if not line:
                            break
                        lines.append(line.strip())
                    
                    for line in lines[:5]:
                        print(f"   {line}")
                    
                    if len(lines) > 5:
                        print(f"   ... (更多內容查看完整文件)")
            except:
                print(f"   無法讀取文件")
        else:
            print(f"\n❌ 文件不存在: {filename}")
    
    print("\n💡 查看完整文檔:")
    print("   cat PURE_API_SOLUTION.md | less")

def main():
    """主函數"""
    # 顯示歡迎信息
    print("\n歡迎使用方案D：替代API方案！")
    print("這是純API方案，無需虛擬機。")
    
    # 顯示API架構
    show_api_architecture()
    
    # 顯示選項
    show_start_options()
    
    # 獲取用戶選擇
    while True:
        try:
            choice = input("\n請選擇 (1-4, 或 q 退出): ").strip()
            
            if choice.lower() == 'q':
                print("\n退出系統")
                break
            
            if choice == '1':
                start_instant_simulation()
                break
            elif choice == '2':
                setup_oanda_api()
                break
            elif choice == '3':
                test_api_system()
                break
            elif choice == '4':
                show_api_documentation()
                break
            else:
                print("❌ 無效選擇，請輸入 1-4 或 q")
                
        except KeyboardInterrupt:
            print("\n\n🛑 用戶中斷")
            break
        except Exception as e:
            print(f"❌ 錯誤: {e}")
            break
    
    print("\n" + "=" * 70)
    print("🎉 API方案準備就緒！")
    print("=" * 70)
    
    print("\n💡 常用命令:")
    print("• 即時模擬: python3 instant_trader.py")
    print("• OANDA實盤: python3 start_oanda_trader.py")
    print("• 系統測試: python3 test_api_only.py")
    print("• 查看日誌: tail -f logs/*.log")
    
    print("\n📞 需要幫助？")
    print("• 查看文檔: cat PURE_API_SOLUTION.md")
    print("• 重新開始: python3 START_API_NOW.py")
    print("• 一鍵啟動: ./START_NOW.sh")

if __name__ == "__main__":
    main()
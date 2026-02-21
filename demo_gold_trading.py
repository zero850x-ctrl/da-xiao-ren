#!/usr/bin/env python3
"""
黃金交易系統演示
展示如何開始黃金交易
"""

def main():
    print("=" * 60)
    print("🏆 黃金交易系統入門指南")
    print("=" * 60)
    
    print("\n📋 你有幾個選擇開始黃金交易:")
    
    print("\n1️⃣ **MetaTrader 5 (Windows環境)**")
    print("   優點: 功能強大，圖表豐富，EA交易")
    print("   缺點: 需要Windows，Python包有限制")
    print("   適合: 已有MT5賬戶，主要在Windows交易")
    
    print("\n2️⃣ **OANDA API (跨平台)**")
    print("   優點: 跨平台，REST API，Python SDK完善")
    print("   缺點: 需要註冊OANDA賬戶")
    print("   適合: 想在macOS/Linux交易，需要API自動化")
    
    print("\n3️⃣ **Interactive Brokers (專業交易)**")
    print("   優點: 市場接入廣，產品種類多")
    print("   缺點: 複雜度高，費用結構複雜")
    print("   適合: 專業交易者，需要多市場接入")
    
    print("\n4️⃣ **Alpaca API (美股+加密貨幣)**")
    print("   優點: API簡單，文檔完善，免費層級")
    print("   缺點: 主要針對美股")
    print("   適合: 想從美股開始，API開發者")
    
    print("\n" + "=" * 60)
    print("🎯 基於你的情況，我建議:")
    print("=" * 60)
    
    print("\n🔧 **如果你有Windows環境:**")
    print("   1. 安裝MetaTrader 5")
    print("   2. 使用賬戶 20889483 登錄")
    print("   3. 運行 mt5_gold_trader.py (需要調整為Windows)")
    
    print("\n🍎 **如果你只有macOS/Linux:**")
    print("   1. 註冊OANDA模擬賬戶 (免費)")
    print("   2. 獲取API密鑰")
    print("   3. 運行 oanda_gold_trader.py")
    
    print("\n" + "=" * 60)
    print("🚀 快速開始步驟:")
    print("=" * 60)
    
    print("\n📝 **OANDA模擬賬戶註冊:**")
    print("   1. 訪問 https://www.oanda.com/demo-account/")
    print("   2. 填寫註冊信息")
    print("   3. 在後台獲取:")
    print("      - Account ID")
    print("      - API Key")
    
    print("\n💻 **代碼準備:**")
    print("   已為你創建了:")
    print("   - mt5_gold_trader.py (MT5版本)")
    print("   - oanda_gold_trader.py (OANDA API版本)")
    print("   - requirements_mt5.txt (依賴包)")
    
    print("\n🔧 **環境設置:**")
    print("   # 安裝Python包")
    print("   pip install pandas numpy matplotlib requests")
    
    print("\n" + "=" * 60)
    print("📊 黃金交易基礎知識:")
    print("=" * 60)
    
    print("\n💰 **黃金(XAU/USD)特性:**")
    print("   - 交易對: XAUUSD 或 XAU_USD")
    print("   - 交易時間: 24小時 (週一至週五)")
    print("   - 點差: 通常0.3-0.5點")
    print("   - 合約大小: 100盎司/標準手")
    print("   - 每點價值: ~$0.10 (0.1手)")
    
    print("\n⚠️ **風險管理規則:**")
    print("   1. 單筆風險 ≤ 1-2% 總資金")
    print("   2. 總風險 ≤ 5% 總資金")
    print("   3. 使用止損單")
    print("   4. 避免過度槓桿")
    
    print("\n📈 **常用技術指標:**")
    print("   1. 移動平均線 (SMA20, SMA50)")
    print("   2. RSI (14期)")
    print("   3. 布林帶 (20期, 2標準差)")
    print("   4. MACD")
    
    print("\n" + "=" * 60)
    print("🎮 下一步行動:")
    print("=" * 60)
    
    print("\n選擇你的路徑:")
    print("   1. 註冊OANDA模擬賬戶 → 最簡單開始")
    print("   2. 設置Windows MT5 → 如果你有Windows")
    print("   3. 學習Python交易代碼 → 技術準備")
    
    print("\n需要幫助任何一步，隨時告訴我！")


if __name__ == "__main__":
    main()
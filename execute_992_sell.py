#!/usr/bin/env python3

# 聯想集團(00992)賣出執行腳本
# 生成時間: 2026-02-19 20:07:42
# 執行條件: 開市後價格低於$8.81或達到目標價

import time

def check_price_and_sell():
    """檢查價格並執行賣出"""
    print("📊 監控聯想集團(00992)價格...")
    
    # 這裡可以連接富途API獲取實時價格
    # 暫時使用模擬
    
    current_price = 8.99  # 模擬當前價格
    
    print(f"當前價格: ${current_price:.2f}")
    print(f"關鍵支撐位: $8.81")
    print(f"買入價: $8.99")
    print(f"當前盈虧: +{(current_price/8.99-1)*100:.2f}%")
    
    # 賣出條件
    if current_price < 8.81:
        print("🔴 觸發止損條件: 跌破黃金分割位")
        print("🚀 執行賣出操作...")
        # 這裡可以調用富途API賣出
        print("✅ 賣出訂單已提交")
        
    elif current_price >= 9.00:
        print("🟢 達到獲利目標")
        print("🚀 執行賣出操作...")
        # 這裡可以調用富途API賣出
        print("✅ 賣出訂單已提交")
        
    else:
        print("🟡 價格在區間內，繼續觀察")
        print("💡 建議: 設置價格提醒")

if __name__ == "__main__":
    check_price_and_sell()

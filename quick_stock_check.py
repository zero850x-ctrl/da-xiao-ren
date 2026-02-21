#!/usr/bin/env python3
"""
快速股票檢查 - 簡單版本
"""

import sys
import os
from datetime import datetime

print("=" * 70)
print("📈 快速股票檢查")
print("=" * 70)

# 股票信息
stocks = [
    {"code": "00005", "name": "匯豐控股", "buy_price": 59.4},
    {"code": "01398", "name": "工商銀行", "buy_price": 4.46},
    {"code": "02638", "name": "港燈-SS", "buy_price": 4.85}
]

def check_futu_connection():
    """檢查富途連接"""
    try:
        import futu as ft
        
        print("🔗 嘗試連接富途API...")
        
        # 嘗試連接
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 測試連接
        ret, data = quote_ctx.get_market_snapshot(['HK.00700'])
        
        if ret == ft.RET_OK:
            print("✅ 富途API連接成功")
            return quote_ctx, ft
        else:
            print(f"❌ 富途API連接測試失敗")
            return None, None
            
    except ImportError:
        print("❌ 未安裝futu-api模塊")
        print("💡 安裝命令: pip install futu-api")
        return None, None
    except Exception as e:
        print(f"❌ 連接失敗: {e}")
        print("💡 請確保:")
        print("   1. 富途牛牛已安裝並運行")
        print("   2. 已開啟OpenD API服務")
        print("   3. 工具 → OpenD API設置 → 啟用API")
        return None, None

def get_real_time_price(quote_ctx, ft, stock_code):
    """獲取實時價格"""
    try:
        full_code = f"{stock_code}.HK"
        
        # 獲取快照數據
        ret, data = quote_ctx.get_market_snapshot([full_code])
        
        if ret == ft.RET_OK and len(data) > 0:
            snapshot = data.iloc[0]
            
            return {
                'last_price': snapshot.get('last_price', 0),
                'change_rate': snapshot.get('change_rate', 0),
                'volume': snapshot.get('volume', 0),
                'turnover': snapshot.get('turnover', 0),
                'pe_ratio': snapshot.get('pe_ratio', 0),
                'pb_ratio': snapshot.get('pb_ratio', 0),
                'market_cap': snapshot.get('market_cap', 0)
            }
        else:
            print(f"   ⚠️  無法獲取 {full_code} 數據")
            return None
            
    except Exception as e:
        print(f"   ❌ 獲取 {stock_code} 數據時出錯: {e}")
        return None

def main():
    """主函數"""
    print(f"\n📊 分析以下股票:")
    for stock in stocks:
        print(f"  • {stock['code']}.HK {stock['name']} (買入價: ${stock['buy_price']})")
    
    # 嘗試連接富途
    quote_ctx, ft = check_futu_connection()
    
    if quote_ctx and ft:
        print(f"\n📡 正在獲取實時數據...")
        use_real_data = True
    else:
        print(f"\n🧪 使用模擬數據進行分析...")
        use_real_data = False
    
    print(f"\n{'='*60}")
    print("📋 股票分析結果")
    print(f"{'='*60}")
    
    total_pl = 0
    total_pl_percent = 0
    
    for stock in stocks:
        code = stock['code']
        name = stock['name']
        buy_price = stock['buy_price']
        
        if use_real_data and quote_ctx:
            # 獲取實時數據
            data = get_real_time_price(quote_ctx, ft, code)
            
            if data:
                current_price = data['last_price']
                change_rate = data['change_rate']
                data_source = "實時數據"
            else:
                # 如果獲取失敗，使用模擬數據
                import numpy as np
                current_price = buy_price * (1 + np.random.uniform(-0.05, 0.05))
                change_rate = ((current_price - buy_price) / buy_price) * 100
                data_source = "模擬數據"
        else:
            # 使用模擬數據
            import numpy as np
            current_price = buy_price * (1 + np.random.uniform(-0.05, 0.05))
            change_rate = ((current_price - buy_price) / buy_price) * 100
            data_source = "模擬數據"
        
        # 計算盈虧
        pl = current_price - buy_price
        pl_percent = (pl / buy_price) * 100
        
        total_pl += pl
        total_pl_percent += pl_percent
        
        # 顯示結果
        pl_symbol = "🟢" if pl > 0 else "🔴" if pl < 0 else "⚪"
        
        print(f"\n{code}.HK {name}")
        print(f"  買入價: ${buy_price:.3f}")
        print(f"  當前價: ${current_price:.3f} ({data_source})")
        print(f"  盈虧: {pl_symbol} ${pl:+.3f} ({pl_percent:+.2f}%)")
        
        # 簡單建議
        if pl_percent > 10:
            suggestion = "考慮獲利了結 🎯"
        elif pl_percent > 5:
            suggestion = "持有觀察 👀"
        elif pl_percent < -10:
            suggestion = "考慮止損 ⚠️"
        elif pl_percent < -5:
            suggestion = "謹慎持有 🧐"
        else:
            suggestion = "持有 📈"
        
        print(f"  建議: {suggestion}")
    
    # 計算平均表現
    avg_pl_percent = total_pl_percent / len(stocks)
    
    print(f"\n{'='*60}")
    print("📊 投資組合表現")
    print(f"{'='*60}")
    print(f"平均回報: {avg_pl_percent:+.2f}%")
    
    if avg_pl_percent > 5:
        print(f"整體建議: 🟢 表現良好，可考慮部分獲利")
    elif avg_pl_percent < -5:
        print(f"整體建議: 🔴 表現不佳，檢視風險控制")
    else:
        print(f"整體建議: 🟡 表現平穩，建議持有觀察")
    
    print(f"\n💡 提示:")
    if not use_real_data:
        print("   1. 這是模擬數據，僅供參考")
        print("   2. 獲取實時數據需要:")
        print("      • 安裝futu-api: pip install futu-api")
        print("      • 運行富途牛牛並開啟OpenD API")
        print("      • 工具 → OpenD API設置 → 啟用API")
    else:
        print("   1. 數據來源: 富途牛牛實時數據")
        print("   2. 更新時間: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    print(f"{'='*60}")
    
    # 關閉連接
    if quote_ctx:
        quote_ctx.close()

if __name__ == "__main__":
    main()
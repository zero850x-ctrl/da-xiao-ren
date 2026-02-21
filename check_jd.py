#!/usr/bin/env python3
"""
檢查京東集團(09618)數據
"""

import futu as ft
from datetime import datetime

print("=" * 70)
print("📉 京東集團 (09618) 分析")
print("=" * 70)

def main():
    try:
        # 連接富途API
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        
        print("🔍 獲取京東數據...")
        
        # 嘗試不同代碼格式
        codes_to_try = ['09618', 'HK.09618', '09618.HK', '9618', 'HK.9618']
        
        stock_data = None
        
        for code in codes_to_try:
            ret, data = quote_ctx.get_market_snapshot([code])
            if ret == ft.RET_OK and len(data) > 0:
                snapshot = data.iloc[0]
                last_price = snapshot.get('last_price', 0)
                
                if last_price > 0:  # 有效價格
                    stock_data = {
                        'code': code,
                        'name': snapshot.get('stock_name', '京東集團'),
                        'price': last_price,
                        'change_rate': snapshot.get('change_rate', 0),
                        'volume': snapshot.get('volume', 0),
                        'turnover': snapshot.get('turnover', 0),
                        'pe_ratio': snapshot.get('pe_ratio', 0),
                        'pb_ratio': snapshot.get('pb_ratio', 0),
                        'market_cap': snapshot.get('market_cap', 0)
                    }
                    break
        
        if stock_data:
            print(f"\n✅ 成功獲取數據")
            print(f"股票代碼: {stock_data['code']}")
            print(f"股票名稱: {stock_data['name']}")
            print(f"當前價格: ${stock_data['price']:.2f}")
            print(f"今日變動: {stock_data['change_rate']:+.2f}%")
            print(f"成交量: {stock_data['volume']:,}")
            
            if stock_data['turnover'] > 0:
                turnover_m = stock_data['turnover'] / 1_000_000
                print(f"成交額: ${turnover_m:.2f}M")
            
            print(f"市盈率: {stock_data['pe_ratio']:.2f}")
            print(f"市淨率: {stock_data['pb_ratio']:.2f}")
            
            if stock_data['market_cap'] > 0:
                market_cap_b = stock_data['market_cap'] / 1_000_000_000
                print(f"市值: ${market_cap_b:.2f}B")
            
            # 分析買入價$120的情況
            buy_price = 120.0
            current_price = stock_data['price']
            
            print(f"\n📊 持倉分析:")
            print(f"買入價格: ${buy_price:.2f}")
            print(f"當前價格: ${current_price:.2f}")
            
            profit_loss = current_price - buy_price
            profit_loss_percent = (profit_loss / buy_price) * 100
            
            pl_symbol = "🟢" if profit_loss > 0 else "🔴" if profit_loss < 0 else "⚪"
            print(f"盈虧: {pl_symbol} ${profit_loss:+.2f} ({profit_loss_percent:+.2f}%)")
            
            # 虧損分析
            if profit_loss_percent < 0:
                print(f"\n📉 虧損分析:")
                print(f"虧損金額: ${-profit_loss:.2f}")
                print(f"虧損比例: {-profit_loss_percent:.2f}%")
                
                # 需要漲多少回本
                if current_price > 0:
                    recovery_percent = (buy_price / current_price - 1) * 100
                    print(f"需要上漲: {recovery_percent:+.2f}% 才能回本")
            
            # 投資建議
            print(f"\n🎯 投資建議:")
            
            if profit_loss_percent < -50:
                suggestion = "深度套牢，考慮換股或長期持有"
                confidence = "🔴 高"
                reason = "虧損超過50%，短期回本困難"
            elif profit_loss_percent < -30:
                suggestion = "嚴重虧損，檢視基本面"
                confidence = "🔴 高"
                reason = "虧損30-50%，需要重新評估"
            elif profit_loss_percent < -20:
                suggestion = "較大虧損，考慮止損"
                confidence = "🟡 中"
                reason = "虧損20-30%，控制風險"
            elif profit_loss_percent < -10:
                suggestion = "中度虧損，謹慎持有"
                confidence = "🟡 中"
                reason = "虧損10-20%，密切關注"
            elif profit_loss_percent < 0:
                suggestion = "小幅虧損，持有觀察"
                confidence = "⚪ 低"
                reason = "虧損小於10%，可能反彈"
            else:
                suggestion = "盈利中，繼續持有"
                confidence = "🟢 高"
                reason = "處於盈利狀態"
            
            print(f"  {suggestion}")
            print(f"  信心: {confidence}")
            print(f"  理由: {reason}")
            
        else:
            print("❌ 無法獲取京東集團數據")
            print("💡 可能原因:")
            print("   1. 股票代碼不正確")
            print("   2. API權限問題")
            print("   3. 市場數據不可用")
        
        quote_ctx.close()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    main()
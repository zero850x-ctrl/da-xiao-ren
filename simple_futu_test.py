#!/usr/bin/env python3
"""
簡單富途API測試 - 查看數據結構
"""

import futu as ft
import pandas as pd

def main():
    print("簡單富途API測試")
    print("=" * 50)
    
    try:
        # 連接OpenD
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        print("✅ 成功連接到OpenD")
        
        # 測試獲取京東健康數據
        stock_code = 'HK.09618'
        print(f"\n📊 獲取股票數據: {stock_code}")
        
        ret, data = quote_ctx.get_market_snapshot([stock_code])
        
        if ret == ft.RET_OK:
            print(f"✅ 數據獲取成功")
            print(f"數據類型: {type(data)}")
            print(f"數據形狀: {data.shape if hasattr(data, 'shape') else 'N/A'}")
            
            if isinstance(data, pd.DataFrame):
                print(f"\n📋 數據列名:")
                for col in data.columns:
                    print(f"  - {col}")
                
                print(f"\n📄 第一行數據:")
                print(data.iloc[0])
                
                # 顯示重要字段
                print(f"\n🎯 重要信息:")
                for col in ['code', 'last_price', 'change_rate', 'volume', 'turnover', 'update_time']:
                    if col in data.columns:
                        value = data.iloc[0][col]
                        print(f"  {col}: {value}")
            
            # 保存數據到CSV以便查看
            if isinstance(data, pd.DataFrame):
                csv_file = f"/tmp/futu_stock_{stock_code.replace('.', '_')}.csv"
                data.to_csv(csv_file, index=False)
                print(f"\n💾 數據已保存到: {csv_file}")
                
        else:
            print(f"❌ 數據獲取失敗: {data}")
            
        # 測試另一個股票
        print(f"\n📊 獲取騰訊數據: HK.00700")
        ret, tencent_data = quote_ctx.get_market_snapshot(['HK.00700'])
        
        if ret == ft.RET_OK and isinstance(tencent_data, pd.DataFrame):
            print(f"✅ 騰訊數據獲取成功")
            if len(tencent_data) > 0:
                print(f"股票名稱: {tencent_data.iloc[0].get('stock_name', 'N/A')}")
                print(f"最新價格: {tencent_data.iloc[0].get('last_price', 'N/A')}")
        
        # 測試獲取多隻股票
        print(f"\n📊 獲取多隻股票數據")
        stock_codes = ['HK.00700', 'HK.09988', 'HK.03690']
        ret, multi_data = quote_ctx.get_market_snapshot(stock_codes)
        
        if ret == ft.RET_OK and isinstance(multi_data, pd.DataFrame):
            print(f"✅ 成功獲取 {len(multi_data)} 隻股票數據")
            print(f"\n簡要信息:")
            for idx, row in multi_data.iterrows():
                code = row.get('code', 'N/A')
                name = row.get('stock_name', 'N/A')
                price = row.get('last_price', 'N/A')
                change = row.get('change_rate', 'N/A')
                
                if pd.notnull(change):
                    change_str = f"{change:.2%}"
                else:
                    change_str = "N/A"
                    
                print(f"  {name} ({code}): {price} ({change_str})")
        
        quote_ctx.close()
        print("\n🔒 連接已關閉")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
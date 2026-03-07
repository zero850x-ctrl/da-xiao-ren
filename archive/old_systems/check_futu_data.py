#!/usr/bin/env python3
"""
检查富途API返回的数据结构
"""

import futu as ft
from datetime import datetime, timedelta

def check_data_structure():
    print("🔍 检查富途API数据结构...")
    
    try:
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 获取历史K线数据
        end_time = datetime.now()
        start_time = end_time - timedelta(days=5)
        
        ret, kline_data, page_req_key = quote_ctx.request_history_kline(
            code="HK.02800",
            start=start_time.strftime('%Y-%m-%d'),
            end=end_time.strftime('%Y-%m-%d'),
            ktype=ft.KLType.K_DAY,
            max_count=100
        )
        
        if ret == ft.RET_OK:
            print(f"✅ 成功获取历史K线: {len(kline_data)} 条记录")
            print(f"\n📊 数据结构:")
            print(f"  列名: {list(kline_data.columns)}")
            print(f"  数据类型:")
            print(kline_data.dtypes)
            
            if len(kline_data) > 0:
                print(f"\n📋 第一条记录:")
                print(kline_data.iloc[0])
                
                print(f"\n📋 最后一条记录:")
                print(kline_data.iloc[-1])
        else:
            print(f"❌ 获取历史K线失败: {kline_data}")
        
        quote_ctx.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_data_structure()
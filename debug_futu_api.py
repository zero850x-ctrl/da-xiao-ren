#!/usr/bin/env python3
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# 測試獲取歷史數據
result = quote_ctx.request_history_kline(
    "HK.800000", 
    start="2026-01-01", 
    end="2026-02-08",
    ktype=KLType.K_DAY
)

print(f"返回類型: {type(result)}")
print(f"返回長度: {len(result)}")

if isinstance(result, tuple):
    print(f"是元組，長度: {len(result)}")
    for i, item in enumerate(result):
        print(f"  元素{i}: 類型={type(item)}, 值={item if isinstance(item, (int, str, float)) else '...'}")
else:
    print(f"返回值: {result}")

quote_ctx.close()
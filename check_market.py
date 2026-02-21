#!/usr/bin/env python3
"""
检查当前市场状况
"""

import sys
from datetime import datetime
from futu import *

def check_market():
    """检查市场状况"""
    print(f"📊 市场检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 连接API
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 监控列表
    watchlist = [
        "HK.02800",  # 盈富基金
        "HK.00700",  # 腾讯
        "HK.09988",  # 阿里巴巴
        "HK.01299",  # 友邦保险
        "HK.02318",  # 中国平安
    ]
    
    print("📈 监控股票当前状态:")
    for code in watchlist:
        ret, snapshot = quote_ctx.get_market_snapshot([code])
        if ret == RET_OK and len(snapshot) > 0:
            name = snapshot['name'].iloc[0]
            price = snapshot['last_price'].iloc[0]
            prev_close = snapshot['prev_close_price'].iloc[0]
            volume = snapshot['volume'].iloc[0]
            
            # 计算涨跌幅
            if prev_close > 0:
                change_pct = ((price - prev_close) / prev_close) * 100
                change_emoji = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
            else:
                change_pct = 0
                change_emoji = "⚪"
            
            print(f"{change_emoji} {code} ({name}):")
            print(f"   现价: {price:.2f} | 昨收: {prev_close:.2f} | 涨跌: {change_pct:+.2f}%")
            print(f"   成交量: {volume:,} 股")
    
    # 检查HSI指数
    print("\n📊 恒生指数:")
    hsi_codes = ["HK.HSI", "HK.HSCEI"]
    for code in hsi_codes:
        ret, snapshot = quote_ctx.get_market_snapshot([code])
        if ret == RET_OK and len(snapshot) > 0:
            name = snapshot['name'].iloc[0]
            price = snapshot['last_price'].iloc[0]
            prev_close = snapshot['prev_close_price'].iloc[0]
            change_pct = ((price - prev_close) / prev_close) * 100
            change_emoji = "🟢" if change_pct > 0 else "🔴" if change_pct < 0 else "⚪"
            
            print(f"{change_emoji} {code} ({name}): {price:.2f} ({change_pct:+.2f}%)")
    
    # 检查交易时间
    now = datetime.now()
    trading_start = now.replace(hour=9, minute=30, second=0, microsecond=0)
    trading_end = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    print(f"\n⏰ 交易时间检查:")
    print(f"   当前时间: {now.strftime('%H:%M:%S')}")
    print(f"   交易时段: 09:30 - 16:00")
    
    if trading_start <= now <= trading_end:
        print("   ✅ 在交易时间内")
    else:
        print("   ⏸️  非交易时间")
    
    quote_ctx.close()
    print("\n✅ 市场检查完成")

if __name__ == "__main__":
    check_market()
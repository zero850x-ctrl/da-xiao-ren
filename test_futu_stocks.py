#!/usr/bin/env python3
"""
富途API股票數據測試腳本
測試獲取實時股票數據
"""

import futu as ft
import pandas as pd
from datetime import datetime

def test_connection():
    """測試OpenD連接"""
    print("🔗 測試OpenD連接...")
    
    try:
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 獲取全局狀態
        ret, data = quote_ctx.get_global_state()
        
        if ret == ft.RET_OK:
            print("✅ 成功連接到OpenD!")
            print(f"服務器版本: {data.get('server_ver', '未知')}")
            print(f"行情登錄: {data.get('qot_logined', False)}")
            print(f"交易登錄: {data.get('trd_logined', False)}")
            print(f"程序狀態: {data.get('program_status_desc', '未知')}")
            
            # 顯示市場狀態
            print("\n🌍 市場狀態:")
            markets = {
                'market_hk': '港股',
                'market_us': '美股', 
                'market_sh': '滬市',
                'market_sz': '深市'
            }
            
            for market_key, market_name in markets.items():
                status = data.get(market_key, '未知')
                print(f"  {market_name}: {status}")
                
            return quote_ctx, True
            
        else:
            print(f"❌ 獲取全局狀態失敗: {data}")
            return None, False
            
    except Exception as e:
        print(f"❌ 連接失敗: {e}")
        return None, False

def get_stock_data(quote_ctx, stock_codes):
    """獲取股票數據"""
    print(f"\n📊 獲取股票數據: {stock_codes}")
    
    try:
        ret, data = quote_ctx.get_market_snapshot(stock_codes)
        
        if ret == ft.RET_OK:
            print(f"✅ 成功獲取 {len(data)} 隻股票數據")
            
            # 創建簡化的數據框
            result_df = data[[
                'code', 'stock_name', 'last_price', 
                'change_rate', 'volume', 'turnover', 
                'update_time'
            ]].copy()
            
            # 格式化數據
            result_df['change_rate'] = result_df['change_rate'].apply(
                lambda x: f"{x:.2%}" if pd.notnull(x) else "N/A"
            )
            result_df['last_price'] = result_df['last_price'].apply(
                lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A"
            )
            
            print("\n📈 股票數據:")
            print(result_df.to_string(index=False))
            
            return result_df
        else:
            print(f"❌ 獲取股票數據失敗: {data}")
            return None
            
    except Exception as e:
        print(f"❌ 獲取數據時出錯: {e}")
        return None

def get_popular_hk_stocks(quote_ctx):
    """獲取熱門港股數據"""
    print("\n🏆 熱門港股數據:")
    
    # 熱門港股列表
    popular_stocks = [
        'HK.00700',  # 騰訊控股
        'HK.09988',  # 阿里巴巴
        'HK.03690',  # 美團
        'HK.09888',  # 百度
        'HK.09618',  # 京東健康
        'HK.01810',  # 小米集團
        'HK.02020',  # 安踏體育
        'HK.00941',  # 中國移動
        'HK.01299',  # 友邦保險
        'HK.00005',  # 匯豐控股
    ]
    
    return get_stock_data(quote_ctx, popular_stocks)

def get_specific_stock(quote_ctx, stock_code):
    """獲取特定股票詳細數據"""
    print(f"\n🔍 詳細分析: {stock_code}")
    
    try:
        ret, data = quote_ctx.get_market_snapshot([stock_code])
        
        if ret == ft.RET_OK and len(data) > 0:
            stock = data.iloc[0]
            
            print(f"股票名稱: {stock['stock_name']}")
            print(f"股票代碼: {stock['code']}")
            print(f"最新價格: {stock['last_price']}")
            print(f"漲跌幅: {stock['change_rate']:.2%}")
            print(f"開盤價: {stock['open_price']}")
            print(f"最高價: {stock['high_price']}")
            print(f"最低價: {stock['low_price']}")
            print(f"昨收價: {stock['prev_close_price']}")
            print(f"成交量: {stock['volume']}")
            print(f"成交額: {stock['turnover']}")
            print(f"更新時間: {stock['update_time']}")
            print(f"市盈率: {stock['pe_ratio']}")
            print(f"市淨率: {stock['pb_ratio']}")
            
            return stock
        else:
            print(f"❌ 獲取股票數據失敗: {data}")
            return None
            
    except Exception as e:
        print(f"❌ 獲取詳細數據時出錯: {e}")
        return None

def test_basic_functions(quote_ctx):
    """測試基本功能"""
    print("\n🧪 測試基本API功能...")
    
    try:
        # 測試獲取交易日
        ret, trading_days = quote_ctx.get_trading_days(
            market=ft.Market.HK, 
            start='2026-01-01', 
            end='2026-01-31'
        )
        
        if ret == ft.RET_OK:
            print(f"✅ 獲取交易日成功 (共{len(trading_days)}天)")
            print(f"最近5個交易日: {trading_days[:5]}")
        else:
            print(f"❌ 獲取交易日失敗: {trading_days}")
            
        # 測試獲取股票基本信息
        ret, stock_info = quote_ctx.get_stock_basicinfo(
            market=ft.Market.HK,
            stock_type=ft.SecurityType.STOCK
        )
        
        if ret == ft.RET_OK:
            print(f"✅ 獲取股票基本信息成功 (共{len(stock_info)}隻股票)")
            print(f"示例: {stock_info.iloc[0]['code']} - {stock_info.iloc[0]['name']}")
        else:
            print(f"❌ 獲取股票基本信息失敗: {stock_info}")
            
    except Exception as e:
        print(f"❌ 測試基本功能時出錯: {e}")

def main():
    """主函數"""
    print("=" * 60)
    print("富途Open API股票數據測試")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 測試連接
    quote_ctx, connected = test_connection()
    
    if not connected or not quote_ctx:
        print("\n❌ 無法連接到OpenD，請檢查:")
        print("1. OpenD是否正在運行")
        print("2. 是否已登錄富途賬號")
        print("3. 網絡連接是否正常")
        return
    
    try:
        # 測試熱門港股
        popular_data = get_popular_hk_stocks(quote_ctx)
        
        # 測試特定股票（京東健康）
        jd_health = get_specific_stock(quote_ctx, 'HK.09618')
        
        # 測試基本功能
        test_basic_functions(quote_ctx)
        
        print("\n" + "=" * 60)
        print("✅ 測試完成!")
        print("=" * 60)
        
        print("\n🎯 下一步建議:")
        print("1. 開發股票價格監控工具")
        print("2. 設置價格提醒功能")
        print("3. 創建技術分析工具")
        print("4. 集成到OpenClaw技能系統")
        
        # 提供示例代碼
        print("\n💻 快速使用示例:")
        print("""
import futu as ft

# 連接行情服務器
quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)

# 獲取單隻股票數據
ret, data = quote_ctx.get_market_snapshot(['HK.09618'])

if ret == ft.RET_OK:
    stock = data.iloc[0]
    print(f"{stock['stock_name']} ({stock['code']}):")
    print(f"  價格: HKD {stock['last_price']}")
    print(f"  漲跌: {stock['change_rate']:.2%}")
    
quote_ctx.close()
        """)
        
    finally:
        # 確保關閉連接
        if quote_ctx:
            quote_ctx.close()
            print("\n🔒 已關閉連接")

if __name__ == "__main__":
    main()
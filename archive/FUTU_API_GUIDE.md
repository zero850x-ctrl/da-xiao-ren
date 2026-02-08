# 📈 富途（FUTU）Open API 研究與使用指南

## 概述

富途Open API是一個為量化交易和程序化交易設計的接口，提供豐富的行情和交易功能。它由兩部分組成：
1. **OpenD** - 本地網關程序，負責與富途服務器通信
2. **Futu API** - 多語言SDK（支持Python、Java、C#、C++、JavaScript）

## 系統要求

### 1. 賬戶要求
- 富途牛牛賬戶（平台賬號）
- 綜合交易賬戶（用於實際交易）
- API訪問權限

### 2. 軟件要求
- OpenD網關程序（Windows/MacOS/Linux）
- Python 3.6+（或其他支持語言）
- 富途API SDK

## 安裝步驟

### 步驟1：安裝OpenD網關
1. 從富途官網下載OpenD
2. 安裝並啟動OpenD
3. 使用富途賬號登錄
4. OpenD默認運行在：`127.0.0.1:11111`

### 步驟2：安裝Python SDK
```bash
# 安裝富途API
pip install futu-api

# 或使用pip3
pip3 install futu-api

# 升級到最新版本
pip install futu-api --upgrade
```

### 步驟3：驗證安裝
```python
import futu as ft

try:
    quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
    print("✅ 富途API安裝成功並已連接服務器")
    quote_ctx.close()
except Exception as e:
    print(f"❌ 安裝失敗: {e}")
```

## 核心功能

### 1. 行情功能
- 實時報價
- K線數據
- 市場快照
- 逐筆交易
- 擺盤數據
- 經紀隊列

### 2. 交易功能
- 下單交易
- 查詢訂單
- 查詢持倉
- 賬戶信息
- 模擬交易

### 3. 支持市場
- 香港市場（港股）
- 美國市場（美股）
- A股市場（滬深股通）
- 新加坡市場
- 日本市場

## 代碼示例

### 示例1：獲取股票實時價格（9618.HK - JD Health）
```python
import futu as ft

def get_stock_price(stock_code):
    """
    獲取股票實時價格
    
    參數:
    - stock_code: 股票代碼，格式如 'HK.9618'
    """
    try:
        # 創建行情上下文
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 獲取市場快照
        ret, data = quote_ctx.get_market_snapshot([stock_code])
        
        if ret == ft.RET_OK:
            # 提取關鍵信息
            stock_name = data.iloc[0]['stock_name']
            last_price = data.iloc[0]['last_price']
            change_rate = data.iloc[0]['change_rate']
            update_time = data.iloc[0]['update_time']
            
            print(f"股票: {stock_name} ({stock_code})")
            print(f"最新價格: {last_price}")
            print(f"漲跌幅: {change_rate:.2%}")
            print(f"更新時間: {update_time}")
            
            return {
                'code': stock_code,
                'name': stock_name,
                'price': last_price,
                'change_rate': change_rate,
                'update_time': update_time
            }
        else:
            print(f"獲取數據失敗: {data}")
            return None
            
    except Exception as e:
        print(f"錯誤: {e}")
        return None
    finally:
        quote_ctx.close()

# 使用示例
if __name__ == "__main__":
    # 獲取京東健康(9618.HK)價格
    jd_health_data = get_stock_price('HK.9618')
    
    if jd_health_data:
        print(f"\n📊 京東健康實時行情:")
        print(f"  價格: HKD {jd_health_data['price']}")
        print(f"  漲跌: {jd_health_data['change_rate']:.2%}")
```

### 示例2：批量獲取多隻股票價格
```python
import futu as ft
import pandas as pd

def get_multiple_stocks(stock_codes):
    """
    批量獲取多隻股票價格
    
    參數:
    - stock_codes: 股票代碼列表，如 ['HK.9618', 'HK.00700', 'HK.09988']
    """
    try:
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        
        ret, data = quote_ctx.get_market_snapshot(stock_codes)
        
        if ret == ft.RET_OK:
            # 創建簡化的數據框
            result_df = data[['code', 'stock_name', 'last_price', 'change_rate', 'update_time']].copy()
            result_df['change_rate'] = result_df['change_rate'].apply(lambda x: f"{x:.2%}")
            
            print("📈 多隻股票實時行情:")
            print(result_df.to_string(index=False))
            
            return result_df
        else:
            print(f"獲取數據失敗: {data}")
            return None
            
    except Exception as e:
        print(f"錯誤: {e}")
        return None
    finally:
        quote_ctx.close()

# 使用示例
if __name__ == "__main__":
    stocks = ['HK.9618', 'HK.00700', 'HK.09988', 'HK.01810']
    stock_data = get_multiple_stocks(stocks)
```

### 示例3：獲取歷史K線數據
```python
import futu as ft
from datetime import datetime, timedelta

def get_historical_data(stock_code, days=30):
    """
    獲取歷史K線數據
    
    參數:
    - stock_code: 股票代碼
    - days: 獲取多少天的數據
    """
    try:
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 計算開始日期
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 獲取日K線數據
        ret, data, page_req_key = quote_ctx.request_history_kline(
            stock_code,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            ktype=ft.KLType.K_DAY,
            autype=ft.AuType.QFQ,  # 前復權
            fields=[ft.KL_FIELD.ALL],
            max_count=1000
        )
        
        if ret == ft.RET_OK:
            print(f"📅 {stock_code} 最近{days}天歷史數據:")
            print(f"數據條數: {len(data)}")
            
            # 顯示最新幾條數據
            print("\n最新5條記錄:")
            print(data[['time_key', 'open', 'close', 'high', 'low', 'volume']].tail().to_string(index=False))
            
            return data
        else:
            print(f"獲取歷史數據失敗: {data}")
            return None
            
    except Exception as e:
        print(f"錯誤: {e}")
        return None
    finally:
        quote_ctx.close()

# 使用示例
if __name__ == "__main__":
    history_data = get_historical_data('HK.9618', days=60)
```

### 示例4：簡單的交易下單（模擬交易）
```python
import futu as ft

def place_simulated_order(stock_code, price, quantity):
    """
    模擬交易下單
    
    參數:
    - stock_code: 股票代碼
    - price: 價格
    - quantity: 數量
    """
    try:
        # 創建交易上下文（模擬環境）
        trd_ctx = ft.OpenHKTradeContext(host='127.0.0.1', port=11111)
        
        # 下單（模擬交易）
        ret, data = trd_ctx.place_order(
            price=price,
            qty=quantity,
            code=stock_code,
            trd_side=ft.TrdSide.BUY,
            order_type=ft.OrderType.NORMAL,
            trd_env=ft.TrdEnv.SIMULATE
        )
        
        if ret == ft.RET_OK:
            print(f"✅ 模擬下單成功!")
            print(f"訂單ID: {data.iloc[0]['order_id']}")
            print(f"狀態: {data.iloc[0]['order_status']}")
            return data
        else:
            print(f"❌ 下單失敗: {data}")
            return None
            
    except Exception as e:
        print(f"錯誤: {e}")
        return None
    finally:
        trd_ctx.close()

# 使用示例
if __name__ == "__main__":
    # 模擬買入100股京東健康，價格30港元
    order_result = place_simulated_order('HK.9618', 30.0, 100)
```

## 股票代碼格式

富途API使用特定的股票代碼格式：

| 市場 | 格式 | 示例 |
|------|------|------|
| 港股 | HK.股票代碼 | HK.9618, HK.00700 |
| 美股 | US.股票代碼 | US.AAPL, US.TSLA |
| A股 | SH.股票代碼 或 SZ.股票代碼 | SH.000001, SZ.399001 |

## 常見問題解決

### 問題1：連接失敗
```python
# 檢查OpenD是否運行
# 默認地址：127.0.0.1:11111

# 解決方案：
# 1. 確保OpenD已啟動
# 2. 檢查防火牆設置
# 3. 確認端口未被佔用
```

### 問題2：API Key無效
```python
# 需要富途賬戶和API權限
# 解決方案：
# 1. 登錄富途牛牛APP
# 2. 在設置中啟用API訪問
# 3. 獲取API Key
```

### 問題3：數據獲取失敗
```python
# 可能原因：
# 1. 股票代碼格式錯誤
# 2. 市場未開市
# 3. 賬戶權限不足

# 解決方案：
# 1. 檢查代碼格式
# 2. 確認交易時間
# 3. 檢查賬戶權限
```

## 進階功能

### 1. 實時數據訂閱
```python
# 訂閱實時數據
quote_ctx.subscribe(
    ['HK.9618'], 
    [ft.SubType.QUOTE, ft.SubType.TICKER, ft.SubType.K_DAY]
)

# 設置回調處理實時數據
class StockHandler(ft.TickerHandlerBase):
    def on_recv_rsp(self, rsp_str):
        # 處理實時數據
        pass
```

### 2. 技術指標計算
```python
# 可以使用pandas和ta-lib計算技術指標
import pandas as pd
import talib

# 計算移動平均線
data['MA5'] = talib.SMA(data['close'], timeperiod=5)
data['MA20'] = talib.SMA(data['close'], timeperiod=20)
```

### 3. 策略回測
```python
# 富途提供回測框架
backtest_ctx = ft.BacktestContext()
ret, result = backtest_ctx.run_backtest(
    strategy='your_strategy',
    start_time='2024-01-01',
    end_time='2024-12-31'
)
```

## 安全注意事項

1. **API Key保護**：不要將API Key硬編碼在代碼中
2. **環境變量**：使用環境變量存儲敏感信息
3. **模擬測試**：先在模擬環境測試，再進行實盤交易
4. **錯誤處理**：完善的錯誤處理機制
5. **日誌記錄**：記錄所有交易操作

## 資源鏈接

1. **官方文檔**：https://openapi.futunn.com/futu-api-doc/
2. **GitHub倉庫**：https://github.com/FutunnOpen/py-futu-api
3. **OpenD下載**：https://www.futunn.com/OpenAPI
4. **社區討論**：知乎、CSDN相關專欄

## 下一步建議

1. **安裝OpenD**：下載並安裝OpenD網關
2. **獲取API權限**：在富途牛牛APP中啟用API訪問
3. **測試連接**：運行簡單的測試程序驗證連接
4. **開發策略**：基於API開發量化交易策略
5. **實盤測試**：在模擬環境充分測試後進行實盤交易

## 總結

富途Open API提供了一個強大且免費的量化交易平台，特別適合：
- 個人投資者進行程序化交易
- 量化策略研究與開發
- 實時市場數據分析
- 自動化交易系統

通過Python SDK，你可以輕鬆地獲取實時行情、執行交易指令，並構建自己的量化交易系統。

---

**最後更新**: 2026-02-07  
**狀態**: 研究完成，待實際測試  
**下一步**: 安裝OpenD並獲取API權限進行實際測試
# 📈 富途Open API 安裝與使用指南

## ✅ 已完成步驟

### 1. Python SDK 安裝完成
```bash
# 已成功安裝
pip3 install futu-api

# 安裝版本
富途API版本: 9.06.5608
```

### 2. 依賴包已安裝
- ✅ pandas (數據處理)
- ✅ protobuf (協議緩衝區)
- ✅ PyCryptodome (加密)
- ✅ simplejson (JSON處理)
- ✅ numpy (數值計算)

## 🔧 下一步：安裝 OpenD 網關

### 什麼是 OpenD？
OpenD 是富途API的本地網關程序，負責：
- 連接富途服務器
- 處理API請求
- 管理數據傳輸
- 運行在 `127.0.0.1:11111`

### 安裝步驟：

#### 步驟1：下載 OpenD
1. 訪問富途官網：https://www.futunn.com/OpenAPI
2. 下載適合 macOS 的 OpenD 版本
3. 通常提供以下版本：
   - Windows (.exe)
   - macOS (.dmg 或 .pkg)
   - Linux (.deb 或 .rpm)

#### 步驟2：安裝 OpenD
```bash
# macOS 通常使用 .dmg 文件
# 1. 雙擊下載的 .dmg 文件
# 2. 將 OpenD 拖到 Applications 文件夾
# 3. 在 Applications 中打開 OpenD
```

#### 步驟3：配置 OpenD
1. 首次運行需要登錄富途賬號
2. 使用富途牛牛APP掃碼登錄
3. 確認 OpenD 運行在 `127.0.0.1:11111`

## 🧪 測試連接

### 測試腳本已準備好：
```bash
# 運行測試腳本
cd /Users/gordonlui/.openclaw/workspace
python3 test_futu_api.py
```

### 預期結果：
1. ✅ 檢查API安裝 - 應該成功
2. ⚠️ 測試OpenD連接 - 需要OpenD運行
3. 📊 獲取股票數據 - 需要OpenD運行

## 💻 快速使用示例

### 示例1：簡單連接測試
```python
import futu as ft

try:
    # 創建行情上下文
    quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
    
    # 獲取全局狀態
    ret, data = quote_ctx.get_global_state()
    
    if ret == ft.RET_OK:
        print("✅ 連接成功！")
        print(f"市場狀態: {data}")
    else:
        print(f"❌ 連接失敗: {data}")
        
    quote_ctx.close()
    
except Exception as e:
    print(f"❌ 錯誤: {e}")
```

### 示例2：獲取股票價格
```python
import futu as ft

def get_stock_price(code):
    """獲取股票價格"""
    try:
        quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
        
        # 獲取市場快照
        ret, data = quote_ctx.get_market_snapshot([code])
        
        if ret == ft.RET_OK:
            stock = data.iloc[0]
            print(f"{stock['stock_name']} ({code}):")
            print(f"  最新價: {stock['last_price']}")
            print(f"  漲跌幅: {stock['change_rate']:.2%}")
            print(f"  成交量: {stock['volume']}")
        else:
            print(f"獲取數據失敗: {data}")
            
        quote_ctx.close()
        
    except Exception as e:
        print(f"錯誤: {e}")

# 使用示例
get_stock_price('HK.9618')  # 京東健康
get_stock_price('HK.00700') # 騰訊
get_stock_price('HK.09988') # 阿里巴巴
```

## 📋 股票代碼格式

| 市場 | 格式 | 示例 |
|------|------|------|
| 港股 | HK.股票代碼 | HK.9618, HK.00700 |
| 美股 | US.股票代碼 | US.AAPL, US.TSLA |
| A股 | SH.股票代碼 或 SZ.股票代碼 | SH.000001, SZ.399001 |

## 🚀 進階功能

### 1. 實時數據訂閱
```python
# 訂閱實時行情
quote_ctx.subscribe(['HK.9618'], [ft.SubType.QUOTE])

# 設置回調處理實時數據
class StockHandler(ft.TickerHandlerBase):
    def on_recv_rsp(self, rsp_str):
        # 處理實時數據
        pass
```

### 2. 歷史數據查詢
```python
# 獲取歷史K線
ret, data = quote_ctx.request_history_kline(
    'HK.9618',
    start='2024-01-01',
    end='2024-12-31',
    ktype=ft.KLType.K_DAY
)
```

### 3. 技術指標計算
```python
import pandas as pd
import talib

# 使用TA-Lib計算技術指標
data['MA5'] = talib.SMA(data['close'], timeperiod=5)
data['MA20'] = talib.SMA(data['close'], timeperiod=20)
data['RSI'] = talib.RSI(data['close'], timeperiod=14)
```

## 🔍 故障排除

### 問題1：連接被拒絕
```
錯誤: ECONNREFUSED
```
**解決方案：**
1. 確保 OpenD 已啟動
2. 檢查 OpenD 是否運行在 `127.0.0.1:11111`
3. 確認防火牆沒有阻止連接

### 問題2：認證失敗
```
錯誤: 認證失敗
```
**解決方案：**
1. 在 OpenD 中使用富途賬號登錄
2. 確認賬號有API訪問權限
3. 檢查網絡連接

### 問題3：數據獲取失敗
```
錯誤: 獲取數據失敗
```
**解決方案：**
1. 確認股票代碼格式正確
2. 檢查市場是否開市
3. 確認賬號有行情權限

## 📁 可用文件

### 已創建的文件：
1. **FUTU_API_GUIDE.md** - 完整API使用指南
2. **test_futu_api.py** - 測試腳本
3. **FUTU_INSTALL_GUIDE.md** - 本安裝指南
4. **send_futu_report.py** - 報告發送腳本

### 文件位置：
```
/Users/gordonlui/.openclaw/workspace/
├── FUTU_API_GUIDE.md      # 完整指南
├── test_futu_api.py       # 測試腳本
├── FUTU_INSTALL_GUIDE.md  # 安裝指南
└── send_futu_report.py    # 報告腳本
```

## 🎯 下一步行動

### 短期目標：
1. **下載並安裝 OpenD**
2. **登錄富途賬號**
3. **測試基本連接**
4. **獲取股票數據**

### 中期目標：
1. **開發股票監控工具**
2. **設置價格提醒**
3. **創建技術分析工具**
4. **集成到OpenClaw技能**

### 長期目標：
1. **量化交易策略**
2. **自動化交易系統**
3. **投資組合管理**
4. **風險控制系統**

## 📞 支持資源

1. **官方文檔**：https://openapi.futunn.com/futu-api-doc/
2. **GitHub倉庫**：https://github.com/FutunnOpen/py-futu-api
3. **OpenD下載**：https://www.futunn.com/OpenAPI
4. **社區支持**：知乎、CSDN相關專欄

## 💡 提示與建議

### 開發建議：
1. **先模擬後實盤** - 先在模擬環境測試
2. **錯誤處理** - 完善的錯誤處理機制
3. **日誌記錄** - 記錄所有操作和錯誤
4. **定期備份** - 備份配置和數據

### 安全建議：
1. **保護賬號** - 不要分享登錄信息
2. **API權限** - 僅授予必要權限
3. **網絡安全** - 使用安全網絡連接
4. **數據備份** - 定期備份重要數據

---

**最後更新**: 2026-02-07  
**狀態**: Python SDK 安裝完成，待安裝 OpenD  
**下一步**: 下載並安裝 OpenD 網關程序
# 🚀 幣安Testnet模擬交易設置指南

## 📋 第一步：獲取API密鑰

### 1. 訪問幣安Testnet網站
```
https://testnet.binance.vision/
```

### 2. 創建測試賬戶
- 點擊右上角 "Create Testnet Account"
- 使用GitHub或Google賬戶登錄
- 系統會自動創建測試賬戶

### 3. 獲取API密鑰
登錄後，在Dashboard中：
1. 點擊 "API Management"
2. 點擊 "Create API"
3. 輸入API名稱（例如："OpenClaw_Trading_Bot"）
4. 點擊 "Create"
5. **重要**：立即複製並保存：
   - **API Key**
   - **Secret Key**

### 4. 設置API權限
確保API有以下權限：
- ✅ Enable Reading
- ✅ Enable Spot & Margin Trading
- ✅ Enable Futures (可選)

## 🔧 第二步：設置環境變量

### 方法1：直接在代碼中設置（不推薦用於生產）
```python
API_KEY = "你的API Key"
API_SECRET = "你的Secret Key"
```

### 方法2：使用環境變量（推薦）
```bash
# 在終端中設置
export BINANCE_API_KEY_TEST="你的API Key"
export BINANCE_API_SECRET_TEST="你的Secret Key"
```

### 方法3：使用配置文件
創建 `config.py`：
```python
BINANCE_CONFIG = {
    'testnet': {
        'api_key': '你的API Key',
        'api_secret': '你的Secret Key'
    }
}
```

## 🧪 第三步：測試連接

運行測試腳本：
```bash
python3 binance_test_connection.py
```

## 💰 第四步：獲取測試資金

幣安Testnet提供免費的測試資金：
1. 在Dashboard中點擊 "Faucet"
2. 選擇要獲取的幣種（BTC, ETH, USDT等）
3. 輸入數量（例如：10 BTC, 10000 USDT）
4. 點擊 "Get Test Tokens"

**建議獲取：**
- 10 BTC (約 $400,000)
- 50,000 USDT (穩定幣)
- 100 ETH (約 $30,000)

## 📊 第五步：了解Testnet限制

### 與主網的區別：
1. **資金是虛擬的** - 不是真實貨幣
2. **市場數據是真實的** - 使用真實市場價格
3. **交易是模擬的** - 不會影響真實市場
4. **有速率限制** - 每分鐘1200次請求

### 可用功能：
- ✅ 現貨交易
- ✅ 限價單/市價單
- ✅ 訂單查詢
- ✅ 賬戶餘額查詢
- ✅ K線數據獲取

### 不可用功能：
- ❌ 提現到外部錢包
- ❌ 真實資金交易
- ❌ 某些高級訂單類型

## 🛡️ 第六步：安全注意事項

### 即使Testnet也要注意：
1. **不要分享Secret Key** - 即使是測試環境
2. **使用環境變量** - 不要硬編碼在代碼中
3. **定期輪換密鑰** - 每30天更新一次
4. **限制IP訪問** - 在API設置中限制IP

### 備份你的密鑰：
```bash
# 安全保存密鑰
echo "API Key: xxx" > ~/.binance_testnet_keys.txt
chmod 600 ~/.binance_testnet_keys.txt
```

## 🔄 第七步：故障排除

### 常見問題：

#### Q1: API連接失敗
```
解決方案：檢查網絡連接，確認API Key/Secret正確
```

#### Q2: 權限不足
```
解決方案：在API Management中啟用所需權限
```

#### Q3: 速率限制
```
解決方案：添加延遲，使用WebSocket實時數據
```

#### Q4: 測試資金不足
```
解決方案：從Faucet獲取更多測試資金
```

## 🚀 第八步：開始交易

### 簡單測試交易：
```python
# 購買0.001 BTC
order = client.order_market_buy(
    symbol='BTCUSDT',
    quantity=0.001
)

# 出售0.001 BTC  
order = client.order_market_sell(
    symbol='BTCUSDT',
    quantity=0.001
)
```

### 設置止損：
```python
# 限價止損單
order = client.create_order(
    symbol='BTCUSDT',
    side='SELL',
    type='STOP_LOSS_LIMIT',
    quantity=0.001,
    price=45000,  # 觸發價格
    stopPrice=44000  # 止損價格
)
```

## 📈 第九步：監控和報告

### 每日報告內容：
1. **賬戶概況** - 總資產、盈虧
2. **交易統計** - 交易次數、勝率
3. **持倉分析** - 當前持倉、浮動盈虧
4. **風險指標** - 最大回撤、夏普比率

### 報告頻率：
- **實時監控**：每小時檢查一次
- **每日總結**：香港時間00:00
- **每周回顧**：每周日23:59

## 🎯 學習目標

### 技術學習：
1. ✅ API集成和錯誤處理
2. ✅ 訂單管理和狀態追蹤
3. ✅ 市場數據分析和處理
4. ✅ 風險管理和止損執行

### 交易學習：
1. ✅ 加密貨幣市場特性
2. ✅ 24小時交易節奏
3. ✅ 波動率管理
4. ✅ 多幣種資產配置

---

## 📞 支持資源

### 官方文檔：
- [幣安API文檔](https://binance-docs.github.io/apidocs/spot/en/)
- [Testnet指南](https://testnet.binance.vision/)
- [Python庫文檔](https://python-binance.readthedocs.io/)

### 社區支持：
- [幣安開發者Discord](https://discord.gg/binance)
- [GitHub Issues](https://github.com/binance/binance-connector-python/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/binance)

### 學習資源：
- [幣安學院](https://academy.binance.com/)
- [交易策略教程](https://www.binance.com/en/blog)
- [API最佳實踐](https://dev.binance.vision/)

---

**🎉 現在你已經準備好開始加密貨幣模擬交易了！**

**下一步**：運行 `setup_binance_testnet.py` 來自動化設置過程。
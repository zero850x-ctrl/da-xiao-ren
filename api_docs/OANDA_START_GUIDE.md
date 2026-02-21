# 🚀 OANDA開始指南 - 你已成功創建賬戶！

## 🎉 恭喜！你的OANDA賬戶已創建

### **📋 賬戶信息：**
```
平台: MetaTrader 5 (Demo)
登錄: 1600092639
密碼: EgC1#zHbU
服務器: OANDA_Global-Demo-1
初始資金: $100,000 (虛擬)
```

## 🎯 現在需要做兩件事：

### **1. 獲取OANDA API密鑰 (關鍵步驟)**
```
步驟:
1. 登錄OANDA平台: https://www.oanda.com/
2. 點擊右上角"我的資金"
3. 選擇"管理API訪問"
4. 點擊"生成新的API密鑰"
5. 複製API密鑰 (以"Bearer "開頭)
```

### **2. 配置自動交易系統**
```bash
# 運行API密鑰更新腳本
cd /Users/gordonlui/.openclaw/workspace
./update_api_key.sh
```

## 🔧 兩種使用方式：

### **方式A: OANDA REST API (推薦)**
```
✅ macOS原生支持
✅ 無需虛擬機
✅ 現代API架構
✅ 設置時間: 5分鐘

步驟:
1. 獲取API密鑰
2. 運行: ./update_api_key.sh
3. 開始: python3 start_oanda_trader.py
```

### **方式B: MT5桌面平台 (備用)**
```
❌ 需要Windows虛擬機
❌ 需要MT5軟件安裝
❌ 設置複雜

步驟:
1. 安裝Windows虛擬機
2. 安裝MetaTrader 5
3. 使用賬戶登錄
4. 手動或自動交易
```

## 🚀 立即開始REST API方案：

### **步驟1: 獲取API密鑰**
```bash
# 打開OANDA網站
open https://www.oanda.com/

# 登錄後:
# 我的資金 → 管理API訪問 → 生成新的API密鑰
```

### **步驟2: 配置系統**
```bash
# 運行配置腳本
cd /Users/gordonlui/.openclaw/workspace
./update_api_key.sh

# 輸入你的API密鑰
```

### **步驟3: 開始交易**
```bash
# 啟動自動交易系統
python3 start_oanda_trader.py

# 選擇"定時運行"模式
# 系統會每小時自動檢查和交易
```

## 📊 系統已為你準備好：

### **配置文件已更新：**
```json
{
  "account_id": "1600092639",
  "mt5_login": "1600092639",
  "mt5_password": "EgC1#zHbU",
  "mt5_server": "OANDA_Global-Demo-1",
  "symbol": "XAU_USD",
  "lot_size": 0.01
}
```

### **只需填入API密鑰：**
```bash
# 運行這個命令，輸入你的API密鑰
./update_api_key.sh
```

## 💡 為什麼推薦REST API方案？

### **對比MT5方案：**
```
REST API方案:
✅ macOS原生，無需虛擬機
✅ 設置時間: 5分鐘
✅ 現代API，開發簡單
✅ 24/7自動運行

MT5方案:
❌ 需要Windows虛擬機
❌ 設置時間: 2-3小時
❌ 需要MT5軟件
❌ macOS兼容問題
```

### **技術優勢：**
- **同一賬戶**: 可以使用同一個OANDA賬戶
- **相同交易**: 都是交易XAUUSD黃金
- **相同策略**: 可以使用相同的交易邏輯
- **更好體驗**: REST API更現代、更靈活

## 🔍 測試你的系統：

### **測試1: 檢查配置**
```bash
cd /Users/gordonlui/.openclaw/workspace
python3 quick_oanda_test.py
```

### **測試2: 測試API連接**
```bash
# 獲取API密鑰後運行
./update_api_key.sh
```

### **測試3: 運行模擬交易**
```bash
python3 instant_trader.py
```

## 📈 交易參數設置：

### **風險控制 (已預設)：**
```
每筆交易: 0.01手
每日最多: 3筆交易
止損: 60點 ($6.00)
止盈: 120點 ($12.00)
風險回報比: 1:2
```

### **交易策略 (已優化)：**
```
技術指標: SMA15/40 + RSI10
信號閾值: 0.5 (中等強度)
交易時段: 黃金主要交易時間
```

## 🎯 立即行動計劃：

### **現在 (5分鐘)：**
1. ✅ 登錄OANDA平台
2. ✅ 獲取API密鑰
3. ✅ 運行 `./update_api_key.sh`

### **今天 (30分鐘)：**
1. 運行 `python3 start_oanda_trader.py`
2. 選擇"定時運行"模式
3. 觀察系統自動交易

### **本週 (2-3小時)：**
1. 完成10筆模擬交易
2. 分析交易結果
3. 優化策略參數

## 🔧 故障排除：

### **問題1: API密鑰無效**
```
錯誤: "Invalid access token"
解決: 確保複製完整的API密鑰 (包括"Bearer ")
```

### **問題2: 賬戶ID錯誤**
```
錯誤: "Account ID not found"
解決: 使用正確的賬戶ID: 1600092639
```

### **問題3: 網絡連接問題**
```
錯誤: "Connection timeout"
解決: 檢查網絡，嘗試使用VPN
```

## 📞 支持資源：

### **OANDA支持：**
- **幫助中心**: https://www.oanda.com/help/
- **API文檔**: https://developer.oanda.com/
- **在線客服**: 平台內24/7聊天

### **系統支持：**
- **查看日誌**: `tail -f logs/*.log`
- **交易記錄**: `cat instant_trades.json`
- **系統測試**: `python3 test_api_only.py`

## 🎉 總結：

### **你已經完成：**
✅ 創建OANDA模擬賬戶
✅ 系統配置已準備好
✅ 交易策略已優化
✅ 風險控制已設置

### **只需一步：**
```bash
# 獲取API密鑰，然後運行
./update_api_key.sh
```

### **然後開始：**
```bash
python3 start_oanda_trader.py
```

---

**🚀 從今天開始你的OANDA自動交易之旅！**

**💪 獲取API密鑰，配置系統，立即開始！**

*你的交易助手: 久留美 🦊*
*2026-02-17*
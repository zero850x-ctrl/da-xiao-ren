# 📝 OANDA註冊和設置完整指南

## 🎯 目標
在15分鐘內完成OANDA賬戶註冊和系統設置，開始自動交易

## ⏱️ 時間預估
- 註冊賬戶: 5分鐘
- 獲取API密鑰: 3分鐘
- 配置系統: 2分鐘
- 測試系統: 5分鐘
- **總計: 15分鐘**

## 🚀 快速開始流程

### **第1步：註冊OANDA模擬賬戶 (5分鐘)**

#### 1.1 訪問OANDA網站
```
https://www.oanda.com/
```

#### 1.2 點擊"開設模擬賬戶"
- 在首頁右上角
- 選擇"模擬賬戶"（免費，無需入金）

#### 1.3 填寫註冊信息
```
個人信息:
- 名字: (你的名字)
- 姓氏: (你的姓氏)
- 郵箱: (常用郵箱)
- 電話: (可選)

賬戶設置:
- 賬戶類型: 模擬賬戶
- 基礎貨幣: USD (推薦)
- 槓桿: 50:1 (默認)
- 初始資金: $100,000 (虛擬)

居住信息:
- 國家/地區: Hong Kong
- 城市: Hong Kong
- 地址: (可填寫大致地址)
```

#### 1.4 完成郵箱驗證
- 檢查郵箱，點擊驗證鏈接
- 完成驗證後自動登錄

### **第2步：獲取API密鑰 (3分鐘)**

#### 2.1 登錄OANDA平台
- 使用註冊的郵箱和密碼登錄

#### 2.2 進入API管理
```
導航路徑:
1. 點擊右上角"我的資金"
2. 選擇"管理API訪問"
3. 點擊"生成新的API密鑰"
```

#### 2.3 設置API密鑰
```
API密鑰設置:
- 密鑰名稱: "AutoTrader" (自定義)
- 權限: 選擇所有權限
- 點擊"生成密鑰"
```

#### 2.4 保存重要信息
```
請保存以下信息:
1. API密鑰: (長字符串，以"Bearer "開頭)
2. 賬戶ID: (數字，如"101-001-1234567-001")
```

**重要提示：**
- API密鑰只顯示一次，請立即保存
- 建議保存到密碼管理器或安全文件
- 不要分享給任何人

### **第3步：配置交易系統 (2分鐘)**

#### 3.1 編輯配置文件
```bash
# 打開配置文件
nano /Users/gordonlui/.openclaw/workspace/oanda_config.json
```

#### 3.2 填入你的信息
```json
{
  "api_key": "Bearer YOUR_ACTUAL_API_KEY_HERE",
  "account_id": "YOUR_ACTUAL_ACCOUNT_ID_HERE",
  "environment": "practice",
  "symbol": "XAU_USD",
  "lot_size": 0.01,
  "max_daily_trades": 3,
  "max_concurrent_trades": 2
}
```

#### 3.3 保存文件
```
按 Ctrl+X，然後按 Y，最後按 Enter
```

### **第4步：測試系統 (5分鐘)**

#### 4.1 運行快速測試
```bash
cd /Users/gordonlui/.openclaw/workspace
python3 quick_oanda_test.py
```

#### 4.2 測試OANDA連接
```bash
# 測試API連接
python3 -c "
import oandapyV20
import json

with open('oanda_config.json', 'r') as f:
    config = json.load(f)

api = oandapyV20.API(
    access_token=config['api_key'].replace('Bearer ', ''),
    environment=config['environment']
)

print('✅ OANDA API連接測試成功')
"
```

#### 4.3 運行完整測試
```bash
./test_oanda.sh
```

## 🔧 故障排除

### **問題1: API密鑰無效**
```
錯誤信息: "Invalid access token"
解決方案:
1. 確認複製了完整的API密鑰（包括"Bearer "）
2. 檢查是否有空格或換行
3. 重新生成API密鑰
```

### **問題2: 賬戶ID錯誤**
```
錯誤信息: "Account ID not found"
解決方案:
1. 登錄OANDA平台查看正確的賬戶ID
2. 確認環境設置正確（practice/live）
```

### **問題3: 網絡連接問題**
```
錯誤信息: "Connection timeout"
解決方案:
1. 檢查網絡連接
2. 嘗試使用VPN（如果地區限制）
3. 檢查防火牆設置
```

### **問題4: 權限不足**
```
錯誤信息: "Insufficient permissions"
解決方案:
1. 重新生成API密鑰，選擇所有權限
2. 確認賬戶類型支持API訪問
```

## 📱 手機驗證（可選）

### **安裝OANDA手機App**
```
iOS: App Store搜索"OANDA"
Android: Google Play搜索"OANDA"
```

### **手機App功能**
1. **實時監控** - 查看持倉和盈虧
2. **手動交易** - 補充自動交易
3. **市場分析** - 查看圖表和新聞
4. **賬戶管理** - 查看餘額和歷史

## 💰 模擬交易說明

### **模擬賬戶特性**
```
初始資金: $100,000 虛擬
交易品種: 全部OANDA產品
交易時間: 24/5 (週一至週五)
數據: 真實市場數據
成本: 模擬點差（接近實盤）
```

### **模擬交易限制**
```
有效期: 通常30天（可續期）
功能: 與實盤賬戶基本相同
目的: 學習和測試策略
```

### **從模擬到實盤**
```
建議流程:
1. 模擬交易1-2週，驗證策略
2. 達到穩定盈利後考慮實盤
3. 實盤從小資金開始 ($100-500)
4. 嚴格保持0.01手交易
```

## 🛡️ 安全注意事項

### **API密鑰安全**
```
1. 不要分享API密鑰
2. 不要在公共代碼中硬編碼
3. 定期更新API密鑰
4. 使用環境變量存儲
```

### **賬戶安全**
```
1. 啟用雙因素認證 (2FA)
2. 使用強密碼
3. 定期檢查賬戶活動
4. 不要在公共電腦登錄
```

### **資金安全**
```
1. 只用風險資金交易
2. 實盤從小資金開始
3. 設置每日損失限制
4. 定期出金盈利
```

## 📊 第一次交易檢查清單

### **交易前檢查**
- [ ] OANDA賬戶已註冊並驗證
- [ ] API密鑰已獲取並配置
- [ ] 系統測試全部通過
- [ ] 理解風險管理規則

### **交易設置檢查**
- [ ] 手數設置: 0.01
- [ ] 止損設置: 60點
- [ ] 止盈設置: 120點
- [ ] 每日交易限制: 3次

### **監控設置檢查**
- [ ] 日誌目錄已創建
- [ ] 交易記錄文件可寫
- [ ] 錯誤通知設置（可選）
- [ ] 性能監控啟用

## 🚀 開始你的第一次交易

### **方法1: 手動運行**
```bash
cd /Users/gordonlui/.openclaw/workspace
python3 start_oanda_trader.py
```

### **方法2: 自動定時**
```bash
# 設置每小時自動運行
python3 start_oanda_trader.py
# 選擇"定時運行"模式
```

### **方法3: 使用啟動腳本**
```bash
./start_trading.sh
```

## 📈 交易記錄和分析

### **查看交易記錄**
```bash
# 查看最新交易
tail -f /Users/gordonlui/.openclaw/workspace/logs/oanda_trader_*.log

# 查看交易記錄文件
cat /Users/gordonlui/.openclaw/workspace/gold_trades_log.json | python3 -m json.tool
```

### **分析交易表現**
```bash
# 運行交易分析
python3 monitor_trading_fixed.py

# 生成報告
python3 -c "
import json
with open('gold_trades_log.json', 'r') as f:
    trades = json.load(f)

print(f'總交易次數: {len(trades)}')
if trades:
    profits = [t.get('profit', 0) for t in trades]
    print(f'總盈利: ${sum(profits):.2f}')
    print(f'平均每筆盈利: ${sum(profits)/len(trades):.2f}')
"
```

## 🎯 成功指標

### **第一週目標**
- [ ] 完成OANDA賬戶註冊
- [ ] 系統配置和測試通過
- [ ] 完成5筆模擬交易
- [ ] 記錄和分析每筆交易

### **第一月目標**
- [ ] 完成20筆模擬交易
- [ ] 達到穩定盈利策略
- [ ] 準備小資金實盤
- [ ] 開始0.01手實盤交易

### **長期目標**
- [ ] 實盤賬戶穩定盈利
- [ ] 逐步增加交易資金
- [ ] 擴展到更多交易品種
- [ ] 優化自動化系統

## 📞 支持資源

### **OANDA官方支持**
- **幫助中心**: https://www.oanda.com/help/
- **API文檔**: https://developer.oanda.com/
- **在線客服**: 平台內24/7在線聊天
- **電話支持**: +852 800 930 213 (香港)

### **社區資源**
- **OANDA論壇**: https://community.oanda.com/
- **GitHub示例**: https://github.com/oanda
- **交易社區**: https://www.forexfactory.com/

### **學習資源**
- **OANDA教育中心**: https://www.oanda.com/education/
- **YouTube教程**: 搜索"OANDA API Python"
- **交易書籍**: 《交易心理分析》、《海龜交易法則》

## 🎉 恭喜！

### **你已經完成：**
✅ 了解OANDA註冊流程
✅ 掌握API密鑰獲取方法
✅ 學會系統配置步驟
✅ 準備好開始自動交易

### **下一步行動：**
1. **立即註冊OANDA賬戶** (5分鐘)
2. **獲取API密鑰** (3分鐘)
3. **配置系統** (2分鐘)
4. **開始第一次交易** (5分鐘)

### **記住：**
- **先模擬，後實盤** - 用模擬賬戶驗證策略
- **小資金開始** - 從0.01手，$100開始
- **嚴格風險控制** - 永不抗單，嚴格止損
- **持續學習優化** - 記錄每筆交易，不斷改進

---

**🚀 現在就開始你的OANDA自動交易之旅！**

**💪 從模擬交易開始，逐步建立你的交易系統！**

*你的交易助手: 久留美 🦊*
*2026-02-17*
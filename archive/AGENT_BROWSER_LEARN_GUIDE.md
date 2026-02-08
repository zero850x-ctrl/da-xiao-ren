# 🕸️ Agent Browser Skill 學習指南

## 📋 基本信息

### Skill名稱:
- **正式名稱**: agent-browser-clawdbot
- **版本**: 0.1.0
- **作者**: MaTriXy
- **更新時間**: 2026-02-08
- **類型**: 瀏覽器自動化CLI

### 功能概述:
專為AI代理優化的無頭瀏覽器自動化CLI，具有：
- 可訪問性樹快照
- 基於引用的確定性元素選擇
- 會話隔離和狀態持久化
- 強大的自動化命令

## 🎯 主要功能

### 1. 瀏覽器自動化
- 網頁導航和控制
- 元素交互（點擊、輸入、選擇）
- 表單填寫和提交
- 頁面截圖和PDF生成

### 2. 數據提取
- 網頁內容抓取
- 結構化數據提取
- 動態內容處理
- API請求攔截和分析

### 3. 會話管理
- 會話隔離和持久化
- Cookie和本地存儲管理
- 用戶代理模擬
- 代理設置

### 4. 網絡控制
- 請求攔截和修改
- 資源加載控制
- 網絡條件模擬
- 性能監控

### 5. 可訪問性支持
- 可訪問性樹快照
- 屏幕閱讀器兼容
- 鍵盤導航支持
- ARIA屬性訪問

## 🚀 安裝方法

### 方法1: 使用clawhub安裝
```bash
npx clawhub install agent-browser-clawdbot --dir /Users/gordonlui/.openclaw/skills
```

### 方法2: 使用安裝腳本
```bash
cd /Users/gordonlui/.openclaw/workspace
./install_skills.sh
# 選擇選項2: 安裝agent-browser
```

### 方法3: 手動安裝
```bash
# 創建目錄
mkdir -p /Users/gordonlui/.openclaw/skills/agent-browser-clawdbot

# 從clawhub下載
npx clawhub inspect agent-browser-clawdbot --download /Users/gordonlui/.openclaw/skills
```

## 🔧 配置要求

### 系統要求:
- Node.js 18+
- npm 或 yarn
- 現代瀏覽器（Chrome/Firefox）
- 足夠的內存和CPU

### 依賴項:
- Puppeteer 或 Playwright
- 瀏覽器驅動程序
- 必要的系統庫

### 權限:
- 網絡訪問權限
- 文件系統寫入權限
- 瀏覽器執行權限

## 💡 使用示例

### 基本使用:
```bash
# 啟動瀏覽器會話
agent-browser start --url https://example.com

# 執行JavaScript
agent-browser eval --script "document.title"

# 截取屏幕截圖
agent-browser screenshot --output page.png

# 提取頁面內容
agent-browser extract --selector "h1" --output title.txt
```

### 高級使用:
```bash
# 自動化表單填寫
agent-browser automate --script "
  await page.goto('https://example.com/login');
  await page.type('#username', 'user123');
  await page.type('#password', 'pass123');
  await page.click('#submit');
"

# 數據抓取工作流
agent-browser scrape --config scrape-config.json

# 性能測試
agent-browser benchmark --url https://example.com --iterations 10
```

## 🎯 在加密貨幣學習系統中的應用

### 應用場景1: 市場數據收集
```bash
# 自動收集加密貨幣價格
agent-browser automate --script "
  await page.goto('https://www.binance.com/en/markets');
  const prices = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.price')).map(el => el.textContent);
  });
  return prices;
"
```

### 應用場景2: 新聞和資訊抓取
```bash
# 收集加密貨幣新聞
agent-browser scrape --url https://cointelegraph.com --selectors "
  articles: .post-card__title
  dates: .post-card__date
  links: .post-card__title-link
"
```

### 應用場景3: 社交媒體監控
```bash
# 監控Twitter/X上的加密貨幣討論
agent-browser monitor --url https://twitter.com --keywords "
  bitcoin
  ethereum
  crypto
  blockchain
" --interval 300
```

### 應用場景4: 技術分析數據
```bash
# 從交易平台獲取技術指標
agent-browser extract --url https://tradingview.com --indicators "
  RSI
  MACD
  Bollinger Bands
  Moving Averages
"
```

## 🔄 整合到現有系統

### 整合步驟:
1. **安裝skill** - 完成安裝和配置
2. **測試功能** - 驗證基本操作
3. **創建腳本** - 編寫特定任務腳本
4. **集成到Python** - 通過子進程調用
5. **自動化調度** - 設置定時任務

### Python集成示例:
```python
import subprocess
import json

def collect_crypto_data():
    """使用agent-browser收集加密貨幣數據"""
    script = """
    await page.goto('https://www.binance.com/en/markets');
    const data = await page.evaluate(() => {
        const rows = document.querySelectorAll('.css-1qkp2ad');
        return Array.from(rows).map(row => ({
            symbol: row.querySelector('.css-1x8dg53').textContent,
            price: row.querySelector('.css-ydcgk2').textContent,
            change: row.querySelector('.css-1vgpzss').textContent
        }));
    });
    return data;
    """
    
    cmd = [
        'agent-browser', 'automate',
        '--script', script,
        '--output', 'json'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout) if result.returncode == 0 else None
```

### 自動化工作流:
```python
# 每日數據收集工作流
def daily_data_collection():
    tasks = [
        ("幣安市場數據", "https://www.binance.com/en/markets"),
        ("CoinMarketCap排名", "https://coinmarketcap.com"),
        ("加密貨幣新聞", "https://cointelegraph.com"),
        ("Reddit討論", "https://www.reddit.com/r/CryptoCurrency")
    ]
    
    for task_name, url in tasks:
        print(f"收集: {task_name}")
        data = collect_data_from_url(url)
        save_to_database(task_name, data)
        time.sleep(60)  # 避免請求過快
```

## 🛠️ 故障排除

### 常見問題1: 瀏覽器啟動失敗
```
錯誤: Could not launch browser
解決:
1. 檢查瀏覽器安裝
2. 更新瀏覽器驅動
3. 檢查系統權限
4. 增加內存限制
```

### 常見問題2: 頁面加載超時
```
錯誤: Page load timeout
解決:
1. 增加超時時間
2. 檢查網絡連接
3. 使用代理服務器
4. 重試機制
```

### 常見問題3: 元素找不到
```
錯誤: Element not found
解決:
1. 等待元素加載
2. 使用不同的選擇器
3. 檢查iframe
4. 啟用JavaScript
```

### 常見問題4: 內存不足
```
錯誤: Out of memory
解決:
1. 減少並發任務
2. 增加系統內存
3. 使用無頭模式
4. 定期重啟會話
```

## 📊 性能優化

### 最佳實踐:
1. **使用無頭模式** - 減少資源消耗
2. **會話重用** - 避免頻繁啟動
3. **請求攔截** - 阻止不必要的資源
4. **緩存利用** - 重用已下載內容
5. **並行控制** - 合理控制並發數

### 配置優化:
```json
{
  "headless": true,
  "timeout": 30000,
  "viewport": {"width": 1280, "height": 800},
  "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
  "ignoreHTTPSErrors": true,
  "args": ["--no-sandbox", "--disable-setuid-sandbox"]
}
```

## 🎯 學習路線

### 初級階段 (第1周):
- [ ] 安裝和基本配置
- [ ] 學習基本命令
- [ ] 完成簡單自動化
- [ ] 數據提取練習

### 中級階段 (第2周):
- [ ] 複雜頁面處理
- [ ] 會話管理
- [ ] 錯誤處理
- [ ] 性能優化

### 高級階段 (第3周):
- [ ] 分佈式爬蟲
- [ ] 反爬蟲對策
- [ ] 自定義擴展
- [ ] 生產部署

### 專家階段 (第4周):
- [ ] 源碼分析
- [ ] 插件開發
- [ ] 性能調優
- [ ] 團隊協作

## 💪 實踐項目

### 項目1: 加密貨幣價格監控
- 目標: 每小時收集主流加密貨幣價格
- 技術: 定時任務 + 數據存儲
- 輸出: CSV文件 + 數據庫

### 項目2: 市場情緒分析
- 目標: 分析社交媒體情緒
- 技術: 文本抓取 + NLP分析
- 輸出: 情緒指數報告

### 項目3: 技術指標收集
- 目標: 收集技術分析數據
- 技術: 圖表數據提取
- 輸出: 技術指標數據庫

### 項目4: 新聞聚合系統
- 目標: 聚合加密貨幣新聞
- 技術: 多源抓取 + 去重
- 輸出: 每日新聞摘要

## 📞 支持資源

### 官方資源:
- ClawHub頁面: agent-browser-clawdbot
- 作者: MaTriXy
- 更新日誌: 查看版本歷史

### 社區資源:
- OpenClaw Discord
- GitHub倉庫
- 技術博客

### 學習資源:
- Puppeteer文檔
- Playwright文檔
- 瀏覽器自動化教程

## 🚀 開始行動

### 立即開始:
1. **安裝skill** - 使用安裝腳本
2. **測試示例** - 運行簡單命令
3. **閱讀文檔** - 查看SKILL.md
4. **實踐項目** - 開始第一個項目

### 成功標準:
- ✅ Skill安裝成功
- ✅ 基本命令可用
- ✅ 完成簡單自動化
- ✅ 整合到現有系統

### 預期成果:
- 自動化加密貨幣數據收集
- 減少手動工作
- 提高數據質量
- 增強學習系統能力

**現在就開始安裝和使用agent-browser，提升你的加密貨幣學習系統！** 🚀🕸️📈
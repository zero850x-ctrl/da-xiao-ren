# 🕸️ agent-browser 深度學習筆記

## 📋 學習概覽
- **學習時間**: 2026-02-08 10:05開始
- **學習目標**: 掌握加密貨幣數據收集自動化
- **學習方法**: 文檔學習 + 實踐練習 + 項目應用
- **學習狀態**: 進行中

## 📚 文檔學習

### 1. 核心概念理解

#### 什麼是agent-browser?
- 專為AI代理優化的瀏覽器自動化CLI
- 基於可訪問性樹快照和引用選擇
- 支持會話隔離和狀態持久化
- 高性能網頁操作和數據提取

#### 與內置瀏覽器工具的區別
**使用agent-browser當:**
- 自動化多步驟工作流
- 需要確定性元素選擇
- 性能要求高
- 處理複雜SPA應用
- 需要會話隔離

**使用內置瀏覽器工具當:**
- 需要截圖/PDF分析
- 需要視覺檢查
- 需要瀏覽器擴展集成

### 2. 核心工作流

```bash
# 1. 導航和快照
agent-browser open https://example.com
agent-browser snapshot -i --json

# 2. 解析引用，然後交互
agent-browser click @e2
agent-browser fill @e3 "text"

# 3. 頁面變化後重新快照
agent-browser snapshot -i --json
```

### 3. 關鍵命令分類

#### 導航命令
```bash
agent-browser open <url>
agent-browser back | forward | reload | close
```

#### 快照命令 (始終使用 -i --json)
```bash
agent-browser snapshot -i --json          # 可交互元素，JSON輸出
agent-browser snapshot -i -c -d 5 --json  # 緊湊格式，深度限制
agent-browser snapshot -s "#main" -i      # 限定選擇器範圍
```

#### 交互命令 (基於引用)
```bash
agent-browser click @e2
agent-browser fill @e3 "text"
agent-browser type @e3 "text"
agent-browser hover @e4
agent-browser check @e5 | uncheck @e5
agent-browser select @e6 "value"
agent-browser press "Enter"
agent-browser scroll down 500
agent-browser drag @e7 @e8
```

#### 信息獲取命令
```bash
agent-browser get text @e1 --json
agent-browser get html @e2 --json
agent-browser get value @e3 --json
agent-browser get attr @e4 "href" --json
agent-browser get title --json
agent-browser get url --json
agent-browser get count ".item" --json
```

#### 狀態檢查命令
```bash
agent-browser is visible @e2 --json
agent-browser is enabled @e3 --json
agent-browser is checked @e4 --json
```

#### 等待命令
```bash
agent-browser wait @e2                    # 等待元素
agent-browser wait 1000                   # 等待毫秒
agent-browser wait --text "Welcome"       # 等待文本
agent-browser wait --url "**/dashboard"   # 等待URL
agent-browser wait --load networkidle     # 等待網絡
agent-browser wait --fn "window.ready === true"
```

#### 會話管理 (隔離瀏覽器)
```bash
agent-browser --session admin open site.com
agent-browser --session user open site.com
agent-browser session list
# 或通過環境變量: AGENT_BROWSER_SESSION=admin agent-browser ...
```

#### 狀態持久化
```bash
agent-browser state save auth.json        # 保存cookies/存儲
agent-browser state load auth.json        # 加載 (跳過登錄)
```

#### 截圖和PDF
```bash
agent-browser screenshot page.png
agent-browser screenshot --full page.png
agent-browser pdf page.pdf
```

#### 網絡控制
```bash
agent-browser network route "**/ads/*" --abort           # 阻止
agent-browser network route "**/api/*" --body '{"x":1}'  # 模擬
agent-browser network requests --filter api              # 查看
```

#### Cookies和存儲
```bash
agent-browser cookies                     # 獲取所有
agent-browser cookies set name value
agent-browser storage local key           # 獲取localStorage
agent-browser storage local set key val
```

#### 標籤頁和框架
```bash
agent-browser tab new https://example.com
agent-browser tab 2                       # 切換到標籤頁
agent-browser frame @e5                   # 切換到iframe
agent-browser frame main                  # 返回主框架
```

### 4. 快照輸出格式

```json
{
  "success": true,
  "data": {
    "snapshot": "...",
    "refs": {
      "e1": {"role": "heading", "name": "Example Domain"},
      "e2": {"role": "button", "name": "Submit"},
      "e3": {"role": "textbox", "name": "Email"}
    }
  }
}
```

### 5. 最佳實踐

1. **始終使用 `-i` 標誌** - 專注於可交互元素
2. **始終使用 `--json`** - 更容易解析
3. **等待穩定性** - `agent-browser wait --load networkidle`
4. **保存認證狀態** - 使用 `state save/load` 跳過登錄流程
5. **使用會話** - 隔離不同的瀏覽器上下文
6. **使用 `--headed` 調試** - 查看實際情況

## 🧪 實踐練習

### 練習1: 基本導航和快照

```bash
# 1. 打開測試頁面
agent-browser open https://httpbin.org/html

# 2. 獲取快照
agent-browser snapshot -i --json > snapshot1.json

# 3. 分析快照
cat snapshot1.json | jq '.data.refs'  # 需要安裝jq

# 4. 獲取頁面信息
agent-browser get title --json
agent-browser get url --json
```

### 練習2: 元素交互

```bash
# 1. 打開表單頁面
agent-browser open https://httpbin.org/forms/post

# 2. 獲取快照找到元素
agent-browser snapshot -i --json > form_snapshot.json

# 3. 分析並交互 (需要根據實際引用)
# agent-browser fill @e1 "John Doe"
# agent-browser click @e2
```

### 練習3: 會話管理

```bash
# 創建兩個獨立會話
agent-browser --session user1 open https://example.com
agent-browser --session user2 open https://example.com

# 分別操作
agent-browser --session user1 snapshot -i --json
agent-browser --session user2 snapshot -i --json

# 查看會話列表
agent-browser session list
```

## 🎯 加密貨幣應用實踐

### 應用1: 市場數據收集

```bash
#!/bin/bash
# 加密貨幣市場數據收集

# 設置環境
export PATH="/Users/gordonlui/.npm-global/bin:$PATH"

# 數據目錄
DATA_DIR="/Users/gordonlui/.openclaw/workspace/crypto_data"
mkdir -p "$DATA_DIR"

# 收集函數
collect_crypto_data() {
    local site=$1
    local url=$2
    
    echo "📊 收集 $site 數據..."
    
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    
    # 打開網站
    agent-browser open "$url"
    sleep 8  # 等待頁面加載
    
    # 獲取快照
    agent-browser snapshot -i --json > "$DATA_DIR/${site}_snapshot_$TIMESTAMP.json"
    
    # 獲取頁面標題
    agent-browser get title --json > "$DATA_DIR/${site}_title_$TIMESTAMP.json"
    
    echo "✅ $site 數據收集完成"
}

# 收集多個網站
collect_crypto_data "coingecko" "https://www.coingecko.com"
collect_crypto_data "coinmarketcap" "https://coinmarketcap.com"
collect_crypto_data "binance" "https://www.binance.com/en/markets"

echo "🎉 數據收集完成！"
```

### 應用2: 價格監控腳本

```python
#!/usr/bin/env python3
"""
加密貨幣價格監控腳本
"""

import subprocess
import json
import time
from datetime import datetime

def monitor_crypto_price(crypto_symbol, site_url):
    """監控特定加密貨幣價格"""
    
    # 打開網站
    subprocess.run(["agent-browser", "open", site_url], check=True)
    time.sleep(10)  # 等待頁面加載
    
    # 獲取快照
    result = subprocess.run(
        ["agent-browser", "snapshot", "-i", "--json"],
        capture_output=True,
        text=True,
        check=True
    )
    
    snapshot = json.loads(result.stdout)
    
    # 分析快照，提取價格信息
    # 這裡需要根據具體網站結構編寫分析邏輯
    
    price_data = {
        "symbol": crypto_symbol,
        "timestamp": datetime.now().isoformat(),
        "site": site_url,
        "snapshot": snapshot.get("data", {}).get("refs", {})
    }
    
    return price_data

# 監控主要加密貨幣
cryptos_to_monitor = [
    ("BTC", "https://www.coingecko.com/en/coins/bitcoin"),
    ("ETH", "https://www.coingecko.com/en/coins/ethereum"),
    ("BNB", "https://www.coingecko.com/en/coins/bnb")
]

for symbol, url in cryptos_to_monitor:
    data = monitor_crypto_price(symbol, url)
    print(f"{symbol} 數據收集完成")
    
    # 保存數據
    with open(f"{symbol}_price_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(data, f, indent=2)
```

### 應用3: 新聞和資訊收集

```bash
#!/bin/bash
# 加密貨幣新聞收集

echo "📰 收集加密貨幣新聞..."

# 打開新聞網站
agent-browser open https://cryptopanic.com
sleep 10

# 獲取新聞列表快照
agent-browser snapshot -i --json > news_snapshot.json

# 提取新聞標題和鏈接
# 需要分析JSON結構，找到新聞元素

echo "✅ 新聞數據收集完成"
```

## 🔧 錯誤處理和優化

### 常見錯誤處理

1. **超時處理**
```python
import subprocess
import time

def run_with_timeout(cmd, timeout=30):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result
    except subprocess.TimeoutExpired:
        print(f"命令超時: {' '.join(cmd)}")
        return None
```

2. **重試機制**
```python
def run_with_retry(cmd, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result
        except subprocess.CalledProcessError as e:
            print(f"嘗試 {attempt + 1} 失敗: {e}")
            time.sleep(2 ** attempt)  # 指數退避
    return None
```

3. **狀態檢查**
```bash
# 檢查元素是否存在
agent-browser is visible @e1 --json

# 檢查頁面是否加載完成
agent-browser wait --load networkidle
```

### 性能優化

1. **使用會話重用**
```bash
# 創建會話並重用
agent-browser --session crypto open https://www.coingecko.com
agent-browser --session crypto snapshot -i --json
# 會話保持，無需重新加載瀏覽器
```

2. **狀態保存和加載**
```bash
# 登錄後保存狀態
agent-browser state save auth_state.json

# 下次直接加載狀態
agent-browser state load auth_state.json
agent-browser open https://logged-in-site.com
```

3. **並行收集**
```python
import concurrent.futures

def collect_multiple_sites(sites):
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(collect_site_data, site): site for site in sites}
        results = {}
        for future in concurrent.futures.as_completed(futures):
            site = futures[future]
            try:
                results[site] = future.result()
            except Exception as e:
                print(f"{site} 收集失敗: {e}")
        return results
```

## 📊 學習進度跟踪

### 已完成
- [x] 安裝agent-browser skill和CLI工具
- [x] 完成基本功能測試
- [x] 創建加密貨幣數據收集框架
- [x] 學習核心命令分類
- [x] 理解最佳實踐

### 進行中
- [ ] 深度練習所有命令
- [ ] 創建完整的數據收集系統
- [ ] 實現錯誤處理和優化
- [ ] 開發實際應用項目

### 待完成
- [ ] 多網站數據收集整合
- [ ] 定時自動化任務設置
- [ ] 數據分析和可視化
- [ ] 生產環境部署

## 🚀 下一步學習計劃

### 短期 (今天)
1. **完成所有命令練習**
2. **創建3個實際應用腳本**
3. **測試錯誤處理機制**
4. **優化收集性能**

### 中期 (周末)
1. **實現多網站數據收集**
2. **設置定時自動化任務**
3. **開發數據分析工具**
4. **創建可視化報告**

### 長期 (下周)
1. **整合到加密貨幣學習系統**
2. **實現智能數據分析**
3. **開發交易信號生成**
4. **構建完整分析平台**

## 📝 學習心得

### 關鍵收穫
1. **agent-browser的強大功能**: 不僅是簡單的瀏覽器自動化，而是完整的網頁交互框架
2. **引用系統的優勢**: 確定性元素選擇，避免傳統選擇器的脆弱性
3. **會話管理的價值**: 隔離不同任務，提高穩定性和性能
4. **狀態持久化的便利**: 跳過重複登錄，提高效率

### 學習建議
1. **從簡單開始**: 先掌握基本命令，再逐步深入
2. **實踐驅動**: 通過實際項目學習效果最好
3. **文檔為本**: 官方文檔是最準確的學習資源
4. **社區支持**: 遇到問題時尋求社區幫助

### 應用展望
1. **加密貨幣領域**: 自動化數據收集、市場監控、新聞分析
2. **其他領域**: 電商價格監控、社交媒體分析、競爭情報收集
3. **商業應用**: 自動化測試、數據爬蟲、工作流自動化

---

**學習記錄更新時間**: 2026-02-08 10:06  
**學習狀態**: 深度學習進行中  
**下一步**: 開始實踐練習所有命令
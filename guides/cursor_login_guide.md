# Cursor CLI 登錄與設置指南

## ✅ 安裝狀態
- **安裝路徑**: `/Users/gordonlui/.local/bin/agent`
- **版本**: 2026.02.13-41ac335
- **狀態**: 已安裝，需要登錄

## 🔐 登錄步驟

### 方法1: 交互式登錄（推薦）
```bash
# 啟動登錄流程
agent login

# 系統會自動打開瀏覽器
# 按照提示完成OAuth授權
```

### 方法2: 使用API密鑰
```bash
# 設置環境變量
export CURSOR_API_KEY="your-api-key-here"

# 驗證登錄
agent status
```

## 📋 獲取API密鑰

### 步驟：
1. **訪問Cursor網站**: https://cursor.com
2. **登錄您的賬號**
3. **進入設置頁面** → **API密鑰**
4. **生成新密鑰** 或 使用現有密鑰
5. **複製API密鑰**

### 永久設置API密鑰：
```bash
# 添加到 ~/.zshrc
echo 'export CURSOR_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

## 🚀 基本使用示例

### 1. 檢查狀態
```bash
agent status
agent about
```

### 2. 查看可用模型
```bash
agent models
```

### 3. 基本對話
```bash
# 交互模式
agent chat "幫我寫一個Python股票分析腳本"

# 非交互模式（輸出到終端）
agent --print "分析這個函數: $(cat /tmp/test_cursor.py)"
```

### 4. 計劃模式
```bash
agent --plan "設計一個自動化交易系統"
```

### 5. 代碼生成
```bash
agent --print "寫一個Python函數，計算移動平均線"
```

## 🔧 高級功能

### 1. Shell集成
```bash
# 安裝shell集成
agent install-shell-integration

# 安裝後可以在終端直接使用
# 例如: 在當前目錄分析代碼
```

### 2. MCP服務器管理
```bash
# 管理MCP服務器
agent mcp list
agent mcp add <server-url>
```

### 3. 規則生成
```bash
# 生成Cursor規則
agent generate-rule
```

### 4. 會話管理
```bash
# 創建新會話
agent create-chat

# 恢復會話
agent resume <chat-id>
agent ls  # 列出會話
```

## 💡 使用場景

### 場景1: 代碼審查
```bash
agent --print "審查這個Python文件的安全性: /path/to/file.py"
```

### 場景2: 自動化測試
```bash
agent --print "為這個函數寫單元測試: $(cat /path/to/function.py)"
```

### 場景3: 文檔生成
```bash
agent --print "為這個項目生成README文檔"
```

### 場景4: 錯誤修復
```bash
agent chat "幫我修復這個錯誤: $(cat error.log)"
```

## ⚠️ 注意事項

### 安全設置
1. **沙盒模式**: 默認啟用，限制文件訪問
2. **權限控制**: 需要批准才能執行命令
3. **工作空間信任**: 可以設置信任的工作空間

### 訂閱要求
- **免費層**: 有限功能
- **專業版**: 完整功能，需要訂閱
- **團隊版**: 協作功能

### 環境變量
```bash
# 禁用瀏覽器自動打開
export NO_OPEN_BROWSER=1

# 設置代理
export HTTPS_PROXY="http://proxy.example.com:8080"

# 設置超時
export CURSOR_TIMEOUT=300
```

## 🔍 故障排除

### 常見問題：
1. **登錄失敗**: 檢查網絡連接，嘗試`NO_OPEN_BROWSER=1 agent login`
2. **API密鑰無效**: 重新生成密鑰，確保沒有空格
3. **權限不足**: 檢查訂閱狀態
4. **命令執行失敗**: 檢查沙盒設置

### 獲取幫助：
```bash
agent --help
agent help <command>
```

## 📞 支持資源
- **官方文檔**: https://cursor.com/docs/cli
- **社區支持**: https://community.cursor.com
- **問題反饋**: https://github.com/anysphere/cursor/issues

---

*最後更新: 2026-02-16*
*下一步: 登錄後測試完整功能*
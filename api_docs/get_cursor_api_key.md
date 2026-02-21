# 從Cursor Desktop獲取API密鑰

## 🎯 最簡單的方法

### **方法1: 從Cursor應用程序界面獲取** (推薦)
1. **打開Cursor應用程序**
   ```bash
   open -a "Cursor"
   ```

2. **點擊左下角設置圖標** ⚙️
   - 或使用快捷鍵: `Cmd + ,`

3. **導航到Account或API設置**
   - 在設置中搜索 "API" 或 "API Key"
   - 或查看左側菜單的 "Account" 部分

4. **複製API密鑰**
   - 點擊 "Copy" 或 "Show" 按鈕
   - 複製完整的API密鑰

### **方法2: 使用Cursor CLI獲取**
如果您安裝了Cursor CLI：
```bash
# 登錄Cursor CLI
agent login

# 檢查狀態
agent status

# API密鑰可能顯示在輸出中
# 或查看環境變量
echo $CURSOR_API_KEY
```

### **方法3: 檢查環境變量**
```bash
# 檢查當前環境變量
env | grep -i cursor

# 檢查shell配置
grep -r "CURSOR_API_KEY" ~/.zshrc ~/.bashrc ~/.profile 2>/dev/null
```

## 🔍 自動化檢查腳本

讓我創建一個檢查腳本：

```bash
cat > /tmp/check_cursor_api.sh << 'EOF'
#!/bin/bash

echo "🔍 Cursor API密鑰檢查"
echo "===================="

echo ""
echo "1. 檢查環境變量:"
env | grep -i cursor || echo "   未找到CURSOR_API_KEY環境變量"

echo ""
echo "2. 檢查配置文件:"
find ~ -name "*cursor*" -type f 2>/dev/null | xargs grep -l "api_key\|apiKey\|API_KEY" 2>/dev/null | head -5 || echo "   未找到包含API密鑰的文件"

echo ""
echo "3. 檢查Keychain:"
security find-generic-password -s "Cursor" 2>/dev/null && echo "   ✅ 找到Cursor Keychain條目" || echo "   ❌ 未找到Cursor Keychain條目"

echo ""
echo "4. 建議手動獲取:"
echo "   請打開Cursor應用程序，在設置中查找API密鑰"
echo "   或訪問: https://cursor.com/account/api-keys"
EOF

chmod +x /tmp/check_cursor_api.sh
/tmp/check_cursor_api.sh
```

## 📋 手動獲取步驟詳解

### **步驟1: 打開Cursor設置**
1. 啟動Cursor應用程序
2. 點擊左下角 **⚙️ 設置圖標**
3. 或按 `Cmd + ,`

### **步驟2: 找到API設置**
在設置中：
1. 搜索 "API"
2. 或查看左側的 "Account" 或 "Preferences"
3. 或查看 "Extensions" → "Cursor"

### **步驟3: 獲取API密鑰**
1. 找到 "API Key" 或 "Access Token"
2. 點擊 "Show" 或 "Copy"
3. 複製完整的密鑰

### **步驟4: 設置環境變量**
```bash
# 設置臨時環境變量
export CURSOR_API_KEY="your-api-key-here"

# 設置永久環境變量
echo 'export CURSOR_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

## 🚀 快速測試

獲取API密鑰後，測試Cursor CLI：

```bash
# 設置API密鑰
export CURSOR_API_KEY="your-actual-api-key"

# 測試Cursor CLI
agent status
agent about
agent models

# 測試基本功能
agent --print "Hello, Cursor!"
```

## 🔧 如果找不到API密鑰

### **選項A: 生成新API密鑰**
1. 訪問: https://cursor.com/account/api-keys
2. 登錄您的Cursor賬號
3. 點擊 "Generate New API Key"
4. 複製生成的密鑰

### **選項B: 使用Cursor網站**
1. 在瀏覽器中登錄: https://cursor.com
2. 點擊右上角頭像
3. 選擇 "API Keys" 或 "Account Settings"
4. 創建或查看API密鑰

### **選項C: 聯繫支持**
如果以上方法都失敗：
1. 訪問: https://cursor.com/contact
2. 或發送郵件: support@cursor.com

## 📝 注意事項

### **安全性**:
- 🔒 API密鑰就像密碼，請妥善保管
- 🔒 不要分享或提交到代碼庫
- 🔒 定期輪換密鑰

### **使用限制**:
- 📊 API密鑰可能有使用限制
- ⏱️ 可能有速率限制
- 💰 可能需要訂閱計劃

### **驗證**:
```bash
# 驗證API密鑰有效性
curl -H "Authorization: Bearer $CURSOR_API_KEY" \
  https://api.cursor.com/v1/models 2>/dev/null | head -5
```

## 🎯 下一步

獲取API密鑰後，您可以：

### **1. 設置Cursor CLI**
```bash
export CURSOR_API_KEY="your-key"
agent status
```

### **2. 集成到OpenClaw**
```bash
# 在OpenClaw配置中添加
echo 'CURSOR_API_KEY="your-key"' >> ~/.openclaw/env
```

### **3. 自動化任務**
```bash
# 使用Cursor CLI自動化
agent --print "分析這個代碼: $(cat /path/to/file.py)"
```

## 📞 需要幫助？

### **常見問題**:
1. **"Invalid API Key"**: 確保密鑰正確，沒有多餘空格
2. **"Authentication required"**: 運行 `agent login` 或設置環境變量
3. **"Rate limit exceeded"**: 等待一段時間或升級訂閱

### **獲取支持**:
- Cursor文檔: https://docs.cursor.com
- 社區論壇: https://community.cursor.com
- 官方支持: support@cursor.com

**請先從Cursor應用程序獲取API密鑰，然後告訴我密鑰，我幫您設置。**
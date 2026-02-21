# 真正的全自動操作指南

## 🎯 當前狀況分析

經過測試，我發現：

### **✅ 已確認的能力：**
1. **peekaboo已安裝** - 版本 3.0.0-beta3
2. **Chrome已安裝** - 可以打開
3. **gog已安裝** - 可以配置

### **❌ 遇到的限制：**
1. **權限未授予** - 需要屏幕錄製和輔助功能權限
2. **peekaboo命令複雜** - 需要特定JSON格式
3. **全自動受阻** - 無法完全控制UI

## 🚀 **新的全自動方案**

### **方案1: 權限授予 + 真正全自動** (推薦)
**步驟**:
1. **您手動授予權限** (2分鐘)
2. **我進行真正全自動操作** (5分鐘)

### **方案2: 混合自動化**
**步驟**:
1. **我自動打開Chrome和系統設置**
2. **您授予權限**
3. **我繼續全自動操作**

### **方案3: 智能指導 + 部分自動化**
**步驟**:
1. **我提供實時指導**
2. **您手動操作關鍵步驟**
3. **我自動化重複任務**

## 🔧 **立即行動方案**

### **第一步: 快速權限檢查**
```bash
# 運行這個快速檢查腳本
cat > /tmp/quick_check.sh << 'EOF'
#!/bin/bash
echo "=== 系統檢查 ==="
echo "1. peekaboo: $(which peekaboo 2>/dev/null || echo '未安裝')"
echo "2. Chrome: $(ls /Applications/Google\ Chrome.app 2>/dev/null && echo '已安裝' || echo '未安裝')"
echo "3. gog: $(which gog 2>/dev/null || echo '未安裝')"
echo ""
echo "=== 權限狀態 ==="
peekaboo permissions 2>&1 | grep -E "(Screen Recording|Accessibility)"
EOF
chmod +x /tmp/quick_check.sh
/tmp/quick_check.sh
```

### **第二步: 授予權限** (關鍵步驟)

**請完成以下操作**:
1. **打開系統設置** 
   ```bash
   open "x-apple.systempreferences:com.apple.preference.security"
   ```
   或手動: 蘋果菜單 🍎 → 系統設置

2. **授予兩個權限**:
   - **屏幕錄製** → 添加 **Peekaboo** 或 **終端**
   - **輔助功能** → 添加 **Peekaboo** 或 **終端**

3. **驗證權限**:
   ```bash
   peekaboo permissions
   ```
   應該顯示: `Granted` 而不是 `Not Granted`

### **第三步: 真正的全自動操作**

權限授予後，我可以:
```bash
# 1. 自動打開Chrome
# 2. 自動導航到Google Cloud Console  
# 3. 自動點擊創建項目
# 4. 自動輸入項目名稱
# 5. 自動啟用API
# 6. 自動創建OAuth憑證
# 7. 自動下載憑證文件
# 8. 自動配置gog
```

## 📋 **權限授予詳細步驟**

### **屏幕錄製權限**:
1. 系統設置 → 隱私與安全性 → 屏幕錄製
2. 點擊右側的 **+** 按鈕
3. 在應用程序中找到:
   - **Peekaboo** (如果可見)
   - 或 **終端** (Terminal)
   - 或 **iTerm** (如果使用)
4. 點擊 **打開**
5. 確保旁邊有 **✓** 標記

### **輔助功能權限**:
1. 系統設置 → 隱私與安全性 → 輔助功能
2. 點擊右側的 **+** 按鈕
3. 在應用程序中找到:
   - **Peekaboo** (如果可見)
   - 或 **終端** (Terminal)
   - 或 **iTerm** (如果使用)
4. 點擊 **打開**
5. 確保旁邊有 **✓** 標記

## ⚡ **快速開始命令**

### **命令1: 打開系統設置**
```bash
# 方法1: 使用open命令
open "x-apple.systempreferences:com.apple.preference.security"

# 方法2: 使用peekaboo (如果已有權限)
peekaboo app launch "系統設定"
```

### **命令2: 檢查當前狀態**
```bash
# 綜合狀態檢查
echo "=== Google API設置狀態 ==="
echo "1. 憑證文件: $(ls ~/.gog/client_secret.json 2>/dev/null && echo '已存在' || echo '未找到')"
echo "2. gog配置: $(gog auth list 2>/dev/null && echo '已配置' || echo '未配置')"
echo "3. 權限狀態:"
peekaboo permissions 2>&1 | grep -E "(Screen Recording|Accessibility)"
```

### **命令3: 一鍵準備**
```bash
# 創建準備腳本
cat > /tmp/prepare_automation.sh << 'EOF'
#!/bin/bash
echo "準備全自動操作..."
echo ""
echo "A. 檢查必要軟件:"
which peekaboo && echo "✅ peekaboo已安裝" || echo "❌ 請安裝: brew install steipete/tap/peekaboo"
which gog && echo "✅ gog已安裝" || echo "❌ 請安裝: brew install steipete/tap/gogcli"
ls /Applications/Google\ Chrome.app && echo "✅ Chrome已安裝" || echo "❌ 請安裝Chrome"
echo ""
echo "B. 當前權限狀態:"
peekaboo permissions 2>&1 | grep -E "(Screen Recording|Accessibility)"
echo ""
echo "C. 下一步:"
echo "   如果權限未授予，請打開系統設置授予權限。"
echo "   然後運行全自動腳本。"
EOF
chmod +x /tmp/prepare_automation.sh
/tmp/prepare_automation.sh
```

## 🎯 **最終建議**

### **最快速路徑**:
1. **立即授予權限** (2分鐘)
2. **我執行全自動** (5分鐘)
3. **驗證結果** (1分鐘)

### **具體行動**:
```bash
# 1. 打開系統設置授予權限
open "x-apple.systempreferences:com.apple.preference.security"

# 2. 授予後通知我
# 3. 我將立即開始全自動操作
```

## 📞 **需要幫助？**

### **如果遇到問題**:
1. **權限不生效**: 重啟終端，重新授予
2. **找不到Peekaboo**: 選擇"終端"應用
3. **其他問題**: 截圖並告訴我

### **隨時可以**:
1. 詢問具體步驟
2. 要求更詳細指導
3. 選擇其他方案

**請先授予權限，然後告訴我繼續！** 🚀
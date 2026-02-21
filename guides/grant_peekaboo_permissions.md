# Peekaboo 權限授予指南

## 🚨 重要：需要手動授予權限

為了進行全自動操作，您需要授予以下兩個權限：

### **1. 屏幕錄製權限 (Screen Recording)**
**用途**: 允許peekaboo查看屏幕內容、識別UI元素

### **2. 輔助功能權限 (Accessibility)**
**用途**: 允許peekaboo控制鍵盤、鼠標、與UI交互

## 📋 授予權限步驟

### **步驟1: 打開隱私與安全性設置**
1. 點擊屏幕左上角 **蘋果菜單** 🍎
2. 選擇 **系統設置** (System Settings)
3. 選擇 **隱私與安全性** (Privacy & Security)

### **步驟2: 授予屏幕錄製權限**
1. 在左側選擇 **屏幕錄製** (Screen Recording)
2. 點擊右側的 **+** 按鈕
3. 找到並選擇 **Peekaboo** 或 **終端** (Terminal)
4. 點擊 **打開** (Open)
5. 確保旁邊有 **✓** 標記

### **步驟3: 授予輔助功能權限**
1. 在左側選擇 **輔助功能** (Accessibility)
2. 點擊右側的 **+** 按鈕
3. 找到並選擇 **Peekaboo** 或 **終端** (Terminal)
4. 點擊 **打開** (Open)
5. 確保旁邊有 **✓** 標記

## 🔧 快速檢查命令

授予權限後，運行以下命令檢查：

```bash
# 檢查權限狀態
peekaboo permissions

# 預期輸出：
# Screen Recording (Required): Granted
# Accessibility (Required): Granted
```

## ⚡ 一鍵檢查腳本

創建檢查腳本：

```bash
cat > /tmp/check_peekaboo_perms.sh << 'EOF'
#!/bin/bash
echo "🔍 檢查Peekaboo權限狀態..."
echo ""

PERMS=$(peekaboo permissions 2>&1)

if echo "$PERMS" | grep -q "Screen Recording.*Granted" && \
   echo "$PERMS" | grep -q "Accessibility.*Granted"; then
    echo "✅ 所有權限已授予！"
    echo "   可以開始全自動操作。"
else
    echo "❌ 權限未完全授予："
    echo "$PERMS"
    echo ""
    echo "📋 請按照權限授予指南操作。"
fi
EOF

chmod +x /tmp/check_peekaboo_perms.sh
/tmp/check_peekaboo_perms.sh
```

## 🎯 權限授予後的測試

權限授予後，測試基本功能：

```bash
# 測試1: 截屏
peekaboo image --output /tmp/test_permission.png

# 測試2: 列出應用
peekaboo list apps | head -5

# 測試3: 檢查窗口
peekaboo list windows | head -5
```

## 🔄 如果遇到問題

### **問題1: 權限不生效**
**解決方案**:
1. 重啟Peekaboo服務
2. 重啟終端應用
3. 重新授予權限

### **問題2: 找不到Peekaboo應用**
**解決方案**:
1. 在權限設置中選擇 **終端** (Terminal)
2. 或者選擇 **iTerm** (如果使用iTerm)
3. 或者選擇 **Visual Studio Code** (如果從VSCode運行)

### **問題3: 權限被重置**
**解決方案**:
1. 檢查系統更新
2. 重新運行權限授予步驟
3. 確保在 **系統設置** 中保存更改

## 📝 注意事項

1. **安全性**: 這些權限允許應用訪問和控制您的電腦
2. **信任**: 只授予您信任的應用
3. **撤銷**: 隨時可以在系統設置中移除權限
4. **範圍**: 權限應用於整個系統，不僅是當前會話

## 🚀 下一步

權限授予後，我可以：
1. ✅ 自動打開Chrome瀏覽器
2. ✅ 自動導航到Google Cloud Console
3. ✅ 自動點擊按鈕和填寫表單
4. ✅ 自動下載憑證文件
5. ✅ 自動配置gog CLI

**請先授予權限，然後通知我繼續全自動操作。**
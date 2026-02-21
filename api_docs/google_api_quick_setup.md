# Google API 快速設置指南

## 🎯 前提條件
- ✅ 已在Chrome登錄Google賬號
- ✅ 已安裝gog CLI (`brew install steipete/tap/gogcli`)
- ✅ 網絡連接正常

## 📋 快速設置步驟

### 步驟1: 訪問Google Cloud Console
1. **打開Chrome瀏覽器**
2. **訪問**: https://console.cloud.google.com/
3. **確保已登錄**您的Google賬號

### 步驟2: 創建新項目
1. 點擊左上角項目選擇器
2. 點擊"新建項目"
3. 輸入項目名稱: **`OpenClaw-Gog`**
4. 點擊"創建" (約需30秒)

### 步驟3: 啟用所需API
在左側菜單依次啟用：
1. **API和服務** → **庫**
2. 搜索並啟用：
   - 🔍 `Gmail API` → 啟用
   - 🔍 `Google Calendar API` → 啟用  
   - 🔍 `Google Drive API` → 啟用
   - 🔍 `Google Sheets API` → 啟用
   - 🔍 `Google Docs API` → 啟用
   - 🔍 `People API` → 啟用

### 步驟4: 創建OAuth憑證
1. **API和服務** → **憑證**
2. 點擊"創建憑證" → **OAuth 2.0客戶端ID**
3. 配置：
   - 應用程式類型: **桌面應用程式**
   - 名稱: `OpenClaw Gog CLI`
4. 點擊"創建"

### 步驟5: 下載憑證文件
1. 點擊剛創建的憑證右側的"下載"按鈕
2. 文件將保存為: `client_secret_XXXXX.json`
3. **重命名並移動**:
   ```bash
   mkdir -p ~/.gog
   mv ~/Downloads/client_secret_*.json ~/.gog/client_secret.json
   ```

### 步驟6: 配置gog
```bash
# 1. 設置憑證
gog auth credentials ~/.gog/client_secret.json

# 2. 添加您的Google賬號
#    將 zero850x@gmail.com 替換為您的實際郵箱
gog auth add zero850x@gmail.com --services gmail,calendar,drive,contacts,docs,sheets

# 3. 授權訪問
#    系統會打開瀏覽器，點擊"允許"授權
```

### 步驟7: 測試配置
```bash
# 檢查認證狀態
gog auth list

# 測試Gmail搜索
gog gmail search 'newer_than:1d' --max 3

# 測試日曆
gog calendar colors
```

## ⚡ 一鍵設置腳本

如果您已經下載了`client_secret.json`，運行：

```bash
# 給予執行權限
chmod +x /Users/gordonlui/.openclaw/workspace/setup_google_api.sh

# 運行設置腳本
/Users/gordonlui/.openclaw/workspace/setup_google_api.sh
```

## 🔧 故障排除

### 問題1: "重定向URI不匹配"
**解決方案**:
1. 在Google Cloud Console中編輯OAuth 2.0客戶端ID
2. 添加授權重定向URI: `http://localhost:8080`
3. 保存並重試

### 問題2: "API未啟用"
**解決方案**:
1. 確保所有6個API都已啟用
2. 可能需要等待幾分鐘生效

### 問題3: "憑證文件無效"
**解決方案**:
1. 檢查文件路徑: `ls -la ~/.gog/client_secret.json`
2. 確保文件是有效的JSON格式
3. 重新下載憑證文件

### 問題4: "權限不足"
**解決方案**:
1. 確保使用的Google賬號有足夠權限
2. 檢查API配額限制

## 🚀 快速測試命令

### 測試1: 基本功能
```bash
# 查看可用服務
gog --help

# 檢查賬號狀態
gog auth list
```

### 測試2: Gmail操作
```bash
# 搜索最近郵件
gog gmail search 'in:inbox newer_than:7d' --max 5

# 發送測試郵件給自己
gog gmail send --to "zero850x@gmail.com" --subject "gog測試" --body "這是gog CLI測試郵件"
```

### 測試3: 日曆操作
```bash
# 查看日曆顏色
gog calendar colors

# 創建測試事件
gog calendar create primary --summary "gog測試會議" \
  --from "$(date -v+1H +%Y-%m-%dT%H:%M:%S)" \
  --to "$(date -v+2H +%Y-%m-%dT%H:%M:%S)" \
  --event-color 7
```

## 📊 與OpenClaw集成

### 自動化示例
```bash
#!/bin/bash
# openclaw_google_integration.sh

# 1. 每日郵件摘要
DAILY_SUMMARY=$(gog gmail search 'newer_than:1d label:important' --max 10 --json)
echo "📧 重要郵件摘要:"
echo "$DAILY_SUMMARY" | jq -r '.[] | "• \(.from): \(.subject)"'

# 2. 日曆提醒
TOMORROW_EVENTS=$(gog calendar events primary --from "$(date -v+1d +%Y-%m-%d)" --json)
echo "📅 明日日程:"
echo "$TOMORROW_EVENTS" | jq -r '.[] | "• \(.start.dateTime): \(.summary)"'
```

### Cron任務示例
```bash
# 每日早上8點發送日程摘要
0 8 * * * /Users/gordonlui/.openclaw/workspace/daily_calendar_summary.sh

# 每小時檢查重要郵件
0 * * * * /Users/gordonlui/.openclaw/workspace/check_important_emails.sh
```

## 🔒 安全建議

1. **保護憑證文件**:
   ```bash
   chmod 600 ~/.gog/client_secret.json
   chmod 700 ~/.gog
   ```

2. **定期檢查API使用**:
   - 訪問: https://console.cloud.google.com/apis/dashboard
   - 監控API請求和配額使用

3. **備份配置**:
   ```bash
   # 備份gog配置
   cp -r ~/.gog ~/.gog_backup_$(date +%Y%m%d)
   ```

## 📞 獲取幫助

### 官方資源
- **gog文檔**: https://gogcli.sh
- **Google API文檔**: https://developers.google.com/workspace
- **問題反饋**: https://github.com/steipete/gogcli/issues

### 本地幫助
```bash
# 查看gog幫助
gog --help
gog gmail --help
gog calendar --help

# 查看設置日誌
cat ~/.openclaw/google_api/gog_auth.log
```

---

**下一步**: 完成Google Cloud Console設置後，運行設置腳本或手動執行步驟6-7。

**預計時間**: 10-15分鐘（大部分時間在Google Cloud Console操作）
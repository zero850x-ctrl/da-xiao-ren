#!/bin/bash

# Google API 設置腳本
# 作者: OpenClaw Assistant
# 日期: 2026-02-16

echo "🔧 Google API 設置開始"
echo "======================"
echo ""

# 創建配置目錄
echo "1. 創建配置目錄..."
mkdir -p ~/.gog
mkdir -p ~/.openclaw/google_api
echo "✅ 目錄創建完成: ~/.gog, ~/.openclaw/google_api"
echo ""

# 檢查是否已有憑證
echo "2. 檢查現有憑證..."
if [ -f ~/.gog/client_secret.json ]; then
    echo "✅ 找到現有憑證: ~/.gog/client_secret.json"
    echo "   創建時間: $(stat -f "%Sm" ~/.gog/client_secret.json)"
else
    echo "⚠️  未找到憑證文件"
    echo ""
    echo "📋 請完成以下步驟："
    echo ""
    echo "A. 創建Google Cloud項目"
    echo "   1. 訪問: https://console.cloud.google.com/"
    echo "   2. 點擊'創建項目'"
    echo "   3. 項目名稱: OpenClaw-Gog"
    echo "   4. 點擊'創建'"
    echo ""
    echo "B. 啟用所需API"
    echo "   1. 在左側菜單選擇'API和服務' → '庫'"
    echo "   2. 搜索並啟用以下API："
    echo "      - Gmail API"
    echo "      - Google Calendar API"
    echo "      - Google Drive API"
    echo "      - Google Sheets API"
    echo "      - Google Docs API"
    echo "      - People API (用於Contacts)"
    echo ""
    echo "C. 創建OAuth 2.0憑證"
    echo "   1. 在左側菜單選擇'API和服務' → '憑證'"
    echo "   2. 點擊'創建憑證' → 'OAuth 2.0客戶端ID'"
    echo "   3. 應用程式類型: 桌面應用程式"
    echo "   4. 名稱: OpenClaw Gog CLI"
    echo "   5. 點擊'創建'"
    echo ""
    echo "D. 下載憑證文件"
    echo "   1. 創建後點擊下載按鈕 (JSON格式)"
    echo "   2. 保存為: ~/Downloads/client_secret.json"
    echo "   3. 運行: mv ~/Downloads/client_secret.json ~/.gog/"
    echo ""
    read -p "完成以上步驟後按Enter繼續..."
fi
echo ""

# 檢查憑證文件
if [ -f ~/.gog/client_secret.json ]; then
    echo "3. 驗證憑證文件..."
    CLIENT_ID=$(grep -o '"client_id":"[^"]*"' ~/.gog/client_secret.json | head -1 | cut -d'"' -f4)
    PROJECT_ID=$(grep -o '"project_id":"[^"]*"' ~/.gog/client_secret.json | head -1 | cut -d'"' -f4)
    
    if [ -n "$CLIENT_ID" ]; then
        echo "✅ 憑證文件有效"
        echo "   項目ID: $PROJECT_ID"
        echo "   客戶端ID: ${CLIENT_ID:0:20}..."
        
        # 配置gog
        echo ""
        echo "4. 配置gog認證..."
        echo "   正在設置gog憑證..."
        gog auth credentials ~/.gog/client_secret.json 2>&1 | tee ~/.openclaw/google_api/gog_auth.log
        
        if [ $? -eq 0 ]; then
            echo "✅ gog憑證設置成功"
            
            # 添加Google賬號
            echo ""
            echo "5. 添加Google賬號..."
            echo "   請輸入您的Google郵箱地址:"
            read -p "   Email: " GOOGLE_EMAIL
            
            if [ -n "$GOOGLE_EMAIL" ]; then
                echo "   正在添加賬號: $GOOGLE_EMAIL"
                gog auth add "$GOOGLE_EMAIL" --services gmail,calendar,drive,contacts,docs,sheets 2>&1 | tee -a ~/.openclaw/google_api/gog_auth.log
                
                if [ $? -eq 0 ]; then
                    echo "✅ Google賬號添加成功"
                    
                    # 測試功能
                    echo ""
                    echo "6. 測試gog功能..."
                    echo "   A. 檢查認證狀態:"
                    gog auth list 2>&1 | tee ~/.openclaw/google_api/gog_test.log
                    
                    echo ""
                    echo "   B. 測試Gmail搜索 (最近1天):"
                    gog gmail search 'newer_than:1d' --max 3 2>&1 | tee -a ~/.openclaw/google_api/gog_test.log
                    
                    echo ""
                    echo "   C. 測試日曆功能:"
                    gog calendar colors 2>&1 | tee -a ~/.openclaw/google_api/gog_test.log
                    
                    echo ""
                    echo "✅ Google API設置完成！"
                    echo ""
                    echo "📋 設置摘要:"
                    echo "   憑證文件: ~/.gog/client_secret.json"
                    echo "   日誌文件: ~/.openclaw/google_api/"
                    echo "   gog配置: ~/.gog/config.json"
                    echo "   測試日誌: ~/.openclaw/google_api/gog_test.log"
                    
                    # 創建使用示例
                    echo ""
                    echo "🚀 使用示例:"
                    cat > ~/.openclaw/google_api/examples.md << 'EOF'
# gog 使用示例

## 基本命令

### 1. 檢查狀態
```bash
gog auth list
```

### 2. Gmail 操作
```bash
# 搜索郵件
gog gmail search 'in:inbox newer_than:7d' --max 10

# 發送郵件
gog gmail send --to "recipient@example.com" --subject "測試" --body "這是測試郵件"

# 創建草稿
gog gmail drafts create --to "recipient@example.com" --subject "會議記錄" --body-file ./meeting_notes.txt
```

### 3. 日曆操作
```bash
# 查看日曆顏色
gog calendar colors

# 創建事件
gog calendar create primary --summary "團隊會議" \
  --from "2026-02-16T14:00:00" \
  --to "2026-02-16T15:00:00" \
  --event-color 9

# 查看事件
gog calendar events primary --from "2026-02-16" --to "2026-02-17"
```

### 4. Google Drive
```bash
# 搜索文件
gog drive search "季度報告" --max 5

# 查看文件信息
gog drive get <file-id>
```

### 5. Google Sheets
```bash
# 讀取數據
gog sheets get <sheet-id> "Sheet1!A1:D10" --json

# 更新數據
gog sheets update <sheet-id> "Sheet1!A1:B2" \
  --values-json '[["姓名","部門"],["張三","技術部"]]'
```

### 6. Google Docs
```bash
# 導出文檔
gog docs export <doc-id> --format txt --out ./document.txt

# 查看內容
gog docs cat <doc-id>
```

## 自動化示例

### 1. 每日郵件摘要
```bash
#!/bin/bash
# daily_email_summary.sh

TODAY=$(date +%Y-%m-%d)
SUMMARY=$(gog gmail search "newer_than:1d" --max 20 --json)

echo "📧 每日郵件摘要 ($TODAY)"
echo "$SUMMARY" | jq -r '.[] | "• \(.subject) (\(.from))"'
```

### 2. 會議提醒
```bash
#!/bin/bash
# meeting_reminder.sh

TOMORROW=$(date -v+1d +%Y-%m-%d)
MEETINGS=$(gog calendar events primary --from "$TOMORROW" --to "$TOMORROW" --json)

echo "📅 明日會議提醒"
echo "$MEETINGS" | jq -r '.[] | "• \(.summary) (\(.start.dateTime))"'
```

### 3. 數據同步
```bash
#!/bin/bash
# sync_to_sheets.sh

# 從本地CSV同步到Google Sheets
CSV_DATA=$(cat data.csv | jq -R 'split(",")')
gog sheets update <sheet-id> "Data!A1" --values-json "$CSV_DATA"
```

## 環境變量

```bash
# 設置默認賬號
export GOG_ACCOUNT="your-email@gmail.com"

# 設置輸出格式
export GOG_OUTPUT_FORMAT="json"

# 禁用交互提示
export GOG_NO_INPUT="true"
```

## 故障排除

### 常見問題：
1. **認證過期**: 運行 `gog auth refresh`
2. **權限不足**: 檢查API啟用狀態
3. **網絡問題**: 檢查代理設置
4. **配額限制**: 查看Google Cloud配額頁面

### 獲取幫助：
```bash
gog --help
gog <command> --help
```

## 安全建議

1. **保護憑證文件**: 設置適當的文件權限
2. **定期輪換密鑰**: 每90天更新一次OAuth憑證
3. **限制API範圍**: 只啟用必要的API
4. **監控使用情況**: 定期檢查Google Cloud日誌
EOF
                    
                    echo "   示例文檔: ~/.openclaw/google_api/examples.md"
                    echo ""
                    echo "🎉 設置完成！現在可以使用gog管理Google Workspace了。"
                    
                else
                    echo "❌ 添加Google賬號失敗，請檢查錯誤日誌"
                fi
            else
                echo "❌ 未輸入郵箱地址"
            fi
        else
            echo "❌ gog憑證設置失敗，請檢查錯誤日誌"
        fi
    else
        echo "❌ 憑證文件格式無效"
    fi
else
    echo "❌ 憑證文件不存在，請先下載client_secret.json"
    echo "   保存到: ~/.gog/client_secret.json"
fi

echo ""
echo "📝 日誌文件位置:"
echo "   ~/.openclaw/google_api/gog_auth.log"
echo "   ~/.openclaw/google_api/gog_test.log"
echo ""
echo "🔍 如需幫助，請查看日誌文件或重新運行此腳本。"
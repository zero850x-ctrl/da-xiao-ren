#!/bin/bash

echo "🔧 Google API 簡易設置"
echo "======================"
echo ""

# 檢查gog是否安裝
echo "1. 檢查gog安裝..."
if command -v gog &> /dev/null; then
    echo "✅ gog已安裝: $(which gog)"
    echo "   版本: $(gog --version 2>/dev/null || echo '未知')"
else
    echo "❌ gog未安裝"
    echo "   請先運行: brew install steipete/tap/gogcli"
    exit 1
fi
echo ""

# 檢查憑證文件
echo "2. 檢查憑證文件..."
if [ -f ~/.gog/client_secret.json ]; then
    echo "✅ 找到憑證文件: ~/.gog/client_secret.json"
    CLIENT_ID=$(grep -o '"client_id":"[^"]*"' ~/.gog/client_secret.json | head -1 | cut -d'"' -f4)
    echo "   客戶端ID: ${CLIENT_ID:0:20}..."
    
    # 配置gog
    echo ""
    echo "3. 配置gog認證..."
    gog auth credentials ~/.gog/client_secret.json 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ gog憑證設置成功"
        
        # 詢問郵箱
        echo ""
        echo "4. 添加Google賬號"
        echo "   請輸入您的Google郵箱地址 (例如: zero850x@gmail.com)"
        read -p "   📧 Email: " GOOGLE_EMAIL
        
        if [ -n "$GOOGLE_EMAIL" ]; then
            echo "   正在添加賬號: $GOOGLE_EMAIL"
            echo "   這將打開瀏覽器進行授權..."
            echo ""
            
            gog auth add "$GOOGLE_EMAIL" --services gmail,calendar,drive,contacts,docs,sheets
            
            if [ $? -eq 0 ]; then
                echo ""
                echo "✅ Google賬號添加成功！"
                echo ""
                
                # 測試
                echo "5. 運行快速測試..."
                echo ""
                echo "   A. 認證狀態:"
                gog auth list
                echo ""
                
                echo "   B. 測試Gmail搜索:"
                gog gmail search 'newer_than:1d' --max 2 2>&1 | grep -v "^$" || echo "   無最近郵件"
                echo ""
                
                echo "🎉 設置完成！"
                echo ""
                echo "📋 下一步操作:"
                echo "   1. 測試更多功能: gog --help"
                echo "   2. 查看日曆: gog calendar colors"
                echo "   3. 搜索文件: gog drive search '報告' --max 5"
                echo ""
                echo "💡 提示: 使用 'gog <command> --help' 查看具體幫助"
                
            else
                echo "❌ 添加賬號失敗"
                echo "   請檢查瀏覽器授權是否成功"
            fi
        else
            echo "❌ 未輸入郵箱地址"
        fi
    else
        echo "❌ gog憑證設置失敗"
        echo "   請檢查憑證文件是否有效"
    fi
else
    echo "❌ 未找到憑證文件"
    echo ""
    echo "📋 請先完成以下步驟:"
    echo ""
    echo "A. 訪問 Google Cloud Console"
    echo "   https://console.cloud.google.com/"
    echo ""
    echo "B. 創建項目並啟用API"
    echo "   1. 創建項目: OpenClaw-Gog"
    echo "   2. 啟用API: Gmail, Calendar, Drive, Sheets, Docs, People API"
    echo ""
    echo "C. 創建OAuth憑證"
    echo "   1. 憑證 → 創建憑證 → OAuth 2.0客戶端ID"
    echo "   2. 應用類型: 桌面應用程式"
    echo "   3. 名稱: OpenClaw Gog CLI"
    echo ""
    echo "D. 下載憑證文件"
    echo "   1. 點擊下載按鈕"
    echo "   2. 保存為: ~/.gog/client_secret.json"
    echo "   3. 創建目錄: mkdir -p ~/.gog"
    echo ""
    echo "完成後重新運行此腳本。"
    echo ""
    echo "💡 提示: 詳細步驟請查看:"
    echo "   cat /Users/gordonlui/.openclaw/workspace/google_api_quick_setup.md"
fi

echo ""
echo "🔍 日誌文件: ~/.openclaw/google_api/ (如果存在)"
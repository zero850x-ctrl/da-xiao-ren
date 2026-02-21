#!/bin/bash

echo "🤖 智能Google API設置助手"
echo "=========================="
echo ""

# 檢查peekaboo
echo "1. 檢查自動化工具..."
if command -v peekaboo &> /dev/null; then
    echo "✅ peekaboo已安裝: $(which peekaboo)"
    PEEKABOO_VERSION=$(peekaboo --version 2>/dev/null | head -1)
    echo "   版本: $PEEKABOO_VERSION"
else
    echo "❌ peekaboo未安裝"
    echo "   安裝命令: brew install steipete/tap/peekaboo"
    exit 1
fi
echo ""

# 檢查權限
echo "2. 檢查系統權限..."
peekaboo permissions 2>&1 | grep -E "(Screen Recording|Accessibility)" || echo "   需要手動檢查權限"
echo ""

# 提供選擇
echo "3. 選擇設置模式:"
echo "   [1] 全自動模式 (我來操作，您確認)"
echo "   [2] 半自動模式 (我指導，您操作)" 
echo "   [3] 手動模式 (提供詳細指南)"
echo ""
read -p "   請選擇 (1-3): " MODE_CHOICE
echo ""

case $MODE_CHOICE in
    1)
        echo "🎯 選擇: 全自動模式"
        echo "   我將嘗試自動化整個流程。"
        echo "   需要您授予屏幕錄製和輔助功能權限。"
        echo ""
        
        # 檢查Chrome
        if [ -d "/Applications/Google Chrome.app" ]; then
            echo "✅ Chrome瀏覽器已安裝"
        else
            echo "❌ Chrome瀏覽器未安裝"
            echo "   請先安裝Chrome瀏覽器"
            exit 1
        fi
        
        echo ""
        echo "⚠️  重要: 請確保已登錄Google賬號"
        echo "   按Enter開始自動化..."
        read
        
        # 嘗試自動化
        echo "🚀 開始自動化..."
        echo ""
        
        # 1. 打開Chrome
        echo "📂 步驟1: 打開Chrome瀏覽器..."
        peekaboo app launch "Google Chrome" 2>&1 | grep -v "^$" || true
        sleep 3
        
        # 2. 打開新標籤頁
        echo "📂 步驟2: 打開新標籤頁..."
        peekaboo keyboard shortcut "command" "t" 2>&1 | grep -v "^$" || true
        sleep 1
        
        # 3. 輸入網址
        echo "📂 步驟3: 導航到Google Cloud Console..."
        peekaboo keyboard type "https://console.cloud.google.com/" 2>&1 | grep -v "^$" || true
        sleep 1
        peekaboo keyboard press "Enter" 2>&1 | grep -v "^$" || true
        sleep 5
        
        echo ""
        echo "✅ 自動化步驟完成"
        echo ""
        echo "📋 請在瀏覽器中繼續:"
        echo "   1. 創建新項目: OpenClaw-Gog"
        echo "   2. 啟用6個API"
        echo "   3. 創建OAuth憑證"
        echo "   4. 下載client_secret.json"
        echo ""
        echo "完成後按Enter繼續gog配置..."
        read
        ;;
        
    2)
        echo "🎯 選擇: 半自動模式"
        echo "   我將逐步指導您操作。"
        echo ""
        
        # 逐步指導
        echo "📋 準備工作:"
        echo "   1. 確保Chrome瀏覽器已打開"
        echo "   2. 確保已登錄Google賬號"
        echo "   3. 準備好下載文件的位置"
        echo ""
        read -p "   準備好後按Enter開始..."
        echo ""
        
        # 指導步驟
        echo "🚀 開始設置..."
        echo ""
        
        echo "📂 步驟1: 打開Google Cloud Console"
        echo "   請在Chrome中訪問: https://console.cloud.google.com/"
        echo ""
        read -p "   完成後按Enter繼續..."
        echo ""
        
        echo "📂 步驟2: 創建新項目"
        echo "   1. 點擊左上角項目選擇器"
        echo "   2. 點擊'新建項目'"
        echo "   3. 項目名稱: OpenClaw-Gog"
        echo "   4. 點擊'創建'"
        echo ""
        read -p "   完成後按Enter繼續..."
        echo ""
        
        echo "📂 步驟3: 啟用API"
        echo "   在左側菜單選擇'API和服務' → '庫'"
        echo "   搜索並啟用以下6個API:"
        echo "   - Gmail API"
        echo "   - Google Calendar API"
        echo "   - Google Drive API"
        echo "   - Google Sheets API"
        echo "   - Google Docs API"
        echo "   - People API"
        echo ""
        read -p "   完成後按Enter繼續..."
        echo ""
        
        echo "📂 步驟4: 創建OAuth憑證"
        echo "   1. 'API和服務' → '憑證'"
        echo "   2. 點擊'創建憑證' → 'OAuth 2.0客戶端ID'"
        echo "   3. 應用程式類型: 桌面應用程式"
        echo "   4. 名稱: OpenClaw Gog CLI"
        echo "   5. 點擊'創建'"
        echo ""
        read -p "   完成後按Enter繼續..."
        echo ""
        
        echo "📂 步驟5: 下載憑證文件"
        echo "   1. 點擊剛創建的憑證右側的'下載'按鈕"
        echo "   2. 文件將保存到Downloads文件夾"
        echo "   3. 記住文件名: client_secret_XXXXX.json"
        echo ""
        read -p "   完成後按Enter繼續..."
        echo ""
        ;;
        
    3)
        echo "🎯 選擇: 手動模式"
        echo "   為您提供詳細文檔。"
        echo ""
        
        # 顯示指南
        echo "📚 詳細指南:"
        echo "   文件位置: /Users/gordonlui/.openclaw/workspace/google_api_quick_setup.md"
        echo ""
        echo "   查看命令:"
        echo "   cat /Users/gordonlui/.openclaw/workspace/google_api_quick_setup.md | less"
        echo ""
        echo "   或打開在編輯器:"
        echo "   open /Users/gordonlui/.openclaw/workspace/google_api_quick_setup.md"
        echo ""
        
        echo "📋 簡要步驟:"
        echo "   1. 訪問: https://console.cloud.google.com/"
        echo "   2. 創建項目: OpenClaw-Gog"
        echo "   3. 啟用6個API"
        echo "   4. 創建OAuth桌面應用憑證"
        echo "   5. 下載client_secret.json"
        echo "   6. 移動到 ~/.gog/client_secret.json"
        echo ""
        ;;
        
    *)
        echo "❌ 無效選擇"
        exit 1
        ;;
esac

# 共同的後續步驟
echo ""
echo "🔧 後續配置步驟:"
echo ""
echo "A. 移動憑證文件:"
echo "   mkdir -p ~/.gog"
echo "   mv ~/Downloads/client_secret*.json ~/.gog/client_secret.json"
echo ""
echo "B. 運行gog配置:"
echo "   /Users/gordonlui/.openclaw/workspace/simple_google_setup.sh"
echo ""
echo "C. 或手動配置:"
echo "   gog auth credentials ~/.gog/client_secret.json"
echo "   gog auth add 您的郵箱 --services gmail,calendar,drive,contacts,docs,sheets"
echo ""

# 檢查是否已有憑證
if [ -f ~/.gog/client_secret.json ]; then
    echo "✅ 檢測到現有憑證文件"
    echo "   可以直接運行配置腳本"
    echo ""
    read -p "   是否現在運行gog配置? (y/n): " RUN_CONFIG
    
    if [[ $RUN_CONFIG == "y" || $RUN_CONFIG == "Y" ]]; then
        /Users/gordonlui/.openclaw/workspace/simple_google_setup.sh
    fi
fi

echo ""
echo "🎉 設置助手完成！"
echo "📞 如有問題，請查看日誌文件或重新運行此腳本。"
#!/bin/bash

echo "🤖 智能Google API自動化"
echo "======================="
echo ""

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函數：檢查權限
check_permissions() {
    echo -e "${BLUE}🔍 檢查Peekaboo權限...${NC}"
    local perms_output=$(peekaboo permissions 2>&1)
    echo "$perms_output"
    
    local screen_granted=$(echo "$perms_output" | grep -c "Screen Recording.*Granted")
    local access_granted=$(echo "$perms_output" | grep -c "Accessibility.*Granted")
    
    if [ $screen_granted -eq 1 ] && [ $access_granted -eq 1 ]; then
        echo -e "${GREEN}✅ 所有權限已授予！${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  需要授予權限${NC}"
        return 1
    fi
}

# 函數：授予權限指導
guide_permissions() {
    echo -e "${BLUE}📋 權限授予指導${NC}"
    echo ""
    echo "請完成以下步驟："
    echo ""
    echo "1. ${YELLOW}系統設置應該已經打開${NC}"
    echo "   如果沒有，請手動打開：蘋果菜單 🍎 → 系統設置"
    echo ""
    echo "2. ${YELLOW}授予屏幕錄製權限${NC}"
    echo "   • 選擇'隱私與安全性'"
    echo "   • 選擇'屏幕錄製'"
    echo "   • 點擊'+'添加 ${YELLOW}Peekaboo${NC} 或 ${YELLOW}終端${NC}"
    echo ""
    echo "3. ${YELLOW}授予輔助功能權限${NC}"
    echo "   • 選擇'輔助功能'"
    echo "   • 點擊'+'添加 ${YELLOW}Peekaboo${NC} 或 ${YELLOW}終端${NC}"
    echo ""
    echo "完成後按Enter繼續..."
    read
    
    # 重新檢查
    check_permissions
}

# 函數：檢查Chrome
check_chrome() {
    echo -e "${BLUE}🔍 檢查Chrome瀏覽器...${NC}"
    if [ -d "/Applications/Google Chrome.app" ]; then
        echo -e "${GREEN}✅ Chrome已安裝${NC}"
        return 0
    else
        echo -e "${RED}❌ Chrome未安裝${NC}"
        return 1
    fi
}

# 函數：打開Chrome
open_chrome() {
    echo -e "${BLUE}🚀 打開Chrome瀏覽器...${NC}"
    
    # 嘗試多種方法
    if command -v peekaboo &> /dev/null && check_permissions; then
        echo "使用peekaboo打開Chrome..."
        peekaboo app launch "Google Chrome" 2>&1 | grep -v "^$" || true
    else
        echo "使用open命令打開Chrome..."
        open -a "Google Chrome" 2>&1 || true
    fi
    
    sleep 3
    echo -e "${GREEN}✅ Chrome應該已打開${NC}"
}

# 函數：導航到Google Cloud
navigate_to_google_cloud() {
    echo -e "${BLUE}🌐 導航到Google Cloud Console...${NC}"
    
    # 嘗試自動輸入網址
    if check_permissions; then
        echo "嘗試自動輸入網址..."
        peekaboo keyboard type "https://console.cloud.google.com/" 2>&1 | grep -v "^$" || true
        sleep 1
        peekaboo keyboard press "Enter" 2>&1 | grep -v "^$" || true
    else
        echo -e "${YELLOW}⚠️  請手動輸入網址:${NC}"
        echo "   https://console.cloud.google.com/"
        echo ""
        echo "完成後按Enter繼續..."
        read
    fi
    
    sleep 5
    echo -e "${GREEN}✅ 應該已加載Google Cloud Console${NC}"
}

# 函數：提供操作指導
provide_guidance() {
    echo -e "${BLUE}📝 操作指導${NC}"
    echo ""
    echo "現在請在Chrome瀏覽器中完成以下操作："
    echo ""
    echo "1. ${YELLOW}創建新項目${NC}"
    echo "   • 點擊左上角項目選擇器"
    echo "   • 點擊'新建項目'"
    echo "   • 項目名稱: ${GREEN}OpenClaw-Gog${NC}"
    echo "   • 點擊'創建' (等待完成)"
    echo ""
    echo "2. ${YELLOW}啟用API${NC}"
    echo "   • 左側菜單: 'API和服務' → '庫'"
    echo "   • 搜索並啟用以下6個API:"
    echo "     1. ${GREEN}Gmail API${NC}"
    echo "     2. ${GREEN}Google Calendar API${NC}"
    echo "     3. ${GREEN}Google Drive API${NC}"
    echo "     4. ${GREEN}Google Sheets API${NC}"
    echo "     5. ${GREEN}Google Docs API${NC}"
    echo "     6. ${GREEN}People API${NC}"
    echo ""
    echo "3. ${YELLOW}創建OAuth憑證${NC}"
    echo "   • 左側菜單: 'API和服務' → '憑證'"
    echo "   • 點擊'創建憑證' → 'OAuth 2.0客戶端ID'"
    echo "   • 應用程式類型: ${GREEN}桌面應用程式${NC}"
    echo "   • 名稱: ${GREEN}OpenClaw Gog CLI${NC}"
    echo "   • 點擊'創建'"
    echo ""
    echo "4. ${YELLOW}下載憑證文件${NC}"
    echo "   • 點擊剛創建的憑證右側的'下載'按鈕"
    echo "   • 文件將保存到Downloads文件夾"
    echo "   • 文件名類似: ${GREEN}client_secret_XXXXX.json${NC}"
    echo ""
    echo "完成所有步驟後按Enter繼續..."
    read
}

# 函數：配置gog
configure_gog() {
    echo -e "${BLUE}🔧 配置gog CLI...${NC}"
    
    # 檢查憑證文件
    local cert_file=$(ls ~/Downloads/client_secret_*.json 2>/dev/null | head -1)
    
    if [ -n "$cert_file" ]; then
        echo -e "${GREEN}✅ 找到憑證文件: $cert_file${NC}"
        
        # 創建目錄
        mkdir -p ~/.gog
        
        # 移動文件
        echo "移動憑證文件到 ~/.gog/"
        mv "$cert_file" ~/.gog/client_secret.json
        
        # 配置gog
        echo "配置gog認證..."
        gog auth credentials ~/.gog/client_secret.json 2>&1 | tee /tmp/gog_auth.log
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ gog憑證配置成功${NC}"
            
            # 詢問郵箱
            echo ""
            echo -e "${YELLOW}請輸入您的Google郵箱地址:${NC}"
            read -p "📧 Email: " google_email
            
            if [ -n "$google_email" ]; then
                echo "添加Google賬號: $google_email"
                gog auth add "$google_email" --services gmail,calendar,drive,contacts,docs,sheets 2>&1 | tee -a /tmp/gog_auth.log
                
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}✅ Google賬號添加成功！${NC}"
                    
                    # 測試
                    echo ""
                    echo -e "${BLUE}🧪 運行測試...${NC}"
                    gog auth list
                    echo ""
                    gog gmail search 'newer_than:1d' --max 2 2>&1 | grep -v "^$" || echo "無最近郵件"
                    
                    echo -e "${GREEN}🎉 Google API設置完成！${NC}"
                else
                    echo -e "${RED}❌ 添加賬號失敗${NC}"
                fi
            else
                echo -e "${RED}❌ 未輸入郵箱地址${NC}"
            fi
        else
            echo -e "${RED}❌ gog憑證配置失敗${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  未找到憑證文件${NC}"
        echo "請確保已下載client_secret.json到Downloads文件夾"
        echo "然後重新運行此腳本"
    fi
}

# 主程序
main() {
    echo -e "${BLUE}=== 開始智能自動化 ===${NC}"
    echo ""
    
    # 1. 檢查權限
    if ! check_permissions; then
        guide_permissions
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}⚠️  將使用有限自動化模式${NC}"
        fi
    fi
    
    # 2. 檢查Chrome
    if ! check_chrome; then
        echo -e "${RED}❌ 請先安裝Chrome瀏覽器${NC}"
        exit 1
    fi
    
    # 3. 打開Chrome
    open_chrome
    
    # 4. 導航到Google Cloud
    navigate_to_google_cloud
    
    # 5. 提供指導
    provide_guidance
    
    # 6. 配置gog
    configure_gog
    
    echo ""
    echo -e "${GREEN}=== 自動化完成 ===${NC}"
    echo "日誌文件: /tmp/gog_auth.log"
}

# 運行主程序
main
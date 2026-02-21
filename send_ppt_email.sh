#!/bin/bash
# 發送重慶美食PPT到指定郵箱

echo "📧 準備發送重慶美食PPT郵件..."
echo "=========================================="

# 檢查PPT文件
PPT_FILE="/Users/gordonlui/.openclaw/workspace/重慶美食之旅.pptx"
if [ ! -f "$PPT_FILE" ]; then
    echo "❌ 錯誤: PPT文件不存在: $PPT_FILE"
    exit 1
fi

echo "✅ PPT文件存在: $(basename "$PPT_FILE")"
echo "📊 文件大小: $(du -h "$PPT_FILE" | cut -f1)"

# 檢查himalaya
if ! command -v himalaya &> /dev/null; then
    echo "❌ 錯誤: himalaya未安裝"
    exit 1
fi

echo "✅ himalaya已安裝: $(himalaya --version)"

# 創建郵件內容
EMAIL_CONTENT=$(cat << 'EOF'
From: zero850x@gmail.com
To: gordonlct125@gmail.com
Subject: 重慶美食之旅PPT - 分享給您
Content-Type: multipart/mixed; boundary="BOUNDARY123"

--BOUNDARY123
Content-Type: text/plain; charset=utf-8

親愛的Gordon，

您好！

這是為您製作的重慶美食PPT簡報，共4頁，內容包括：

📋 內容概要：
1. 標題頁 - 重慶美食之旅
2. 重慶美食簡介
3. 三大經典美食（火鍋、小麵、酸辣粉）
4. 美食地圖與推薦

🎨 設計特色：
• 主題顏色：火鍋紅搭配暖色系
• 圖標使用：美食相關emoji圖標
• 佈局設計：簡潔專業，重點突出

希望這份PPT對您有幫助！如有需要修改或添加內容，請隨時告訴我。

祝好！

來自：OpenClaw助理
日期：2026年2月19日

--BOUNDARY123
Content-Type: application/vnd.openxmlformats-officedocument.presentationml.presentation
Content-Disposition: attachment; filename="重慶美食之旅.pptx"
Content-Transfer-Encoding: base64

EOF
)

# 添加PPT文件（base64編碼）
echo "⏳ 正在編碼PPT文件..."
PPT_BASE64=$(base64 "$PPT_FILE")
EMAIL_CONTENT+="\n$PPT_BASE64\n"
EMAIL_CONTENT+="\n--BOUNDARY123--"

# 保存郵件到臨時文件
TEMP_EMAIL_FILE="/tmp/chongqing_ppt_email.txt"
echo -e "$EMAIL_CONTENT" > "$TEMP_EMAIL_FILE"

echo "✅ 郵件內容已準備好"
echo "📤 正在發送郵件..."

# 使用himalaya發送郵件
if himalaya template send < "$TEMP_EMAIL_FILE"; then
    echo "✅ 郵件發送成功！"
    echo "📧 收件人: gordonlct125@gmail.com"
    echo "📎 附件: 重慶美食之旅.pptx"
    echo "📅 發送時間: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # 清理臨時文件
    rm -f "$TEMP_EMAIL_FILE"
else
    echo "❌ 郵件發送失敗"
    echo "💡 請檢查："
    echo "   1. himalaya配置是否正確"
    echo "   2. Gmail SMTP設置"
    echo "   3. 網絡連接"
    exit 1
fi

echo "=========================================="
echo "🎉 任務完成！PPT已發送到指定郵箱。"
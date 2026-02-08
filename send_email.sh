#!/bin/bash

# OpenClaw郵件發送工具
# 用法: ./send_email.sh "收件人郵箱" "郵件主題" "郵件內容"

# 檢查參數
if [ $# -lt 3 ]; then
    echo "用法: $0 \"收件人郵箱\" \"郵件主題\" \"郵件內容\""
    echo "示例: $0 \"recipient@example.com\" \"測試郵件\" \"這是一封測試郵件\""
    exit 1
fi

TO="$1"
SUBJECT="$2"
CONTENT="$3"
FROM="zero850x@gmail.com"
FROM_NAME="Gordon Lui (OpenClaw)"

# 創建臨時文件
TEMP_FILE=$(mktemp)

# 創建郵件內容
cat > "$TEMP_FILE" << EOF
From: $FROM_NAME <$FROM>
To: $TO
Subject: $SUBJECT
Content-Type: text/plain; charset=utf-8

$CONTENT

---
此郵件由OpenClaw助理通過Himalaya發送
發送時間: $(date)
EOF

echo "正在發送郵件到: $TO"
echo "主題: $SUBJECT"
echo ""

# 使用Python發送郵件
python3 << ENDPYTHON
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = 'zero850x@gmail.com'
PASSWORD = 'hebr wwxy syqo xwbq'  # 應用程式專用密碼

try:
    # 讀取郵件內容
    with open("$TEMP_FILE", 'r', encoding='utf-8') as f:
        email_content = f.read()
    
    # 解析郵件頭部和正文
    lines = email_content.split('\n')
    headers = {}
    body_lines = []
    in_body = False
    
    for line in lines:
        if not in_body and line.strip() == '':
            in_body = True
            continue
        if not in_body and ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
        elif in_body:
            body_lines.append(line)
    
    body = '\n'.join(body_lines)
    
    # 創建郵件
    msg = MIMEMultipart()
    msg['From'] = headers.get('From', '$FROM_NAME <$FROM>')
    msg['To'] = headers.get('To', '$TO')
    msg['Subject'] = headers.get('Subject', '$SUBJECT')
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # 連接並發送
    context = ssl.create_default_context()
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(USERNAME, PASSWORD)
        server.send_message(msg)
    
    print("✅ 郵件發送成功！")
    
except Exception as e:
    print(f"❌ 發送失敗: {e}")
    exit(1)
ENDPYTHON

# 清理臨時文件
rm "$TEMP_FILE"
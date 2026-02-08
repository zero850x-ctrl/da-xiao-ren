#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

# Gmail SMTP settings
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = 'zero850x@gmail.com'
PASSWORD = 'hebr wwxy syqo xwbq'  # 應用程式專用密碼

def send_test_email():
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = USERNAME
        msg['To'] = USERNAME
        msg['Subject'] = '測試郵件功能 - Python SMTP測試'
        
        # Email body
        body = """這是一封測試郵件，確認OpenClaw的郵件功能已成功設置。

發送時間: 使用Python smtplib直接發送
發送者: OpenClaw助理
帳號: zero850x@gmail.com
狀態: ✅ 郵件功能已啟用

你現在可以使用Himalaya CLI管理郵件：
- himalaya envelope list - 查看收件箱
- himalaya message read <ID> - 閱讀郵件
- himalaya folder list - 查看文件夾
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        print(f"連接至 {SMTP_SERVER}:{SMTP_PORT}...")
        
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect to SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            print("已連接!")
            
            # Start TLS encryption
            server.starttls(context=context)
            print("TLS已啟動!")
            
            # Login
            print(f"登入帳號: {USERNAME}")
            server.login(USERNAME, PASSWORD)
            print("登入成功!")
            
            # Send email
            print("發送郵件中...")
            server.send_message(msg)
            print("郵件發送成功!")
            
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP認證錯誤: {e}")
        return False
    except Exception as e:
        print(f"錯誤: {e}")
        return False

if __name__ == "__main__":
    print("開始測試SMTP發送功能...")
    if send_test_email():
        print("✅ 測試成功！請檢查你的收件箱。")
    else:
        print("❌ 測試失敗。")
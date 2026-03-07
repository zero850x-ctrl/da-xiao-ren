#!/usr/bin/env python3
"""
使用Python發送帶附件的郵件
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

def send_ppt_email():
    """發送PPT郵件"""
    
    print("📧 準備發送重慶美食PPT郵件...")
    print("=" * 50)
    
    # 檢查PPT文件
    ppt_file = "/Users/gordonlui/.openclaw/workspace/重慶美食之旅.pptx"
    if not os.path.exists(ppt_file):
        print(f"❌ 錯誤: PPT文件不存在: {ppt_file}")
        return False
    
    file_size = os.path.getsize(ppt_file) / 1024  # KB
    print(f"✅ PPT文件: {os.path.basename(ppt_file)}")
    print(f"📊 文件大小: {file_size:.1f} KB")
    
    # 郵件配置
    sender_email = "zero850x@gmail.com"
    receiver_email = "gordonlct125@gmail.com"
    password = "hebr wwxy syqo xwbq"  # 從配置中獲取
    
    # 創建郵件
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "重慶美食之旅PPT - 分享給您"
    
    # 郵件正文
    body = """親愛的Gordon，

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
"""
    
    message.attach(MIMEText(body, "plain", "utf-8"))
    
    # 添加附件
    try:
        with open(ppt_file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        
        # 添加頭部信息
        part.add_header(
            "Content-Disposition",
            f"attachment; filename=重慶美食之旅.pptx",
        )
        
        message.attach(part)
        print("✅ PPT附件已添加")
        
    except Exception as e:
        print(f"❌ 添加附件失敗: {e}")
        return False
    
    # 發送郵件
    try:
        print("📤 正在連接Gmail SMTP服務器...")
        
        # 創建安全連接
        context = ssl.create_default_context()
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            print("✅ TLS連接已建立")
            
            print("🔐 正在登錄...")
            server.login(sender_email, password)
            print("✅ 登錄成功")
            
            print("📨 正在發送郵件...")
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("✅ 郵件發送成功！")
            
            print(f"\n📧 郵件詳情:")
            print(f"   發件人: {sender_email}")
            print(f"   收件人: {receiver_email}")
            print(f"   主  題: {message['Subject']}")
            print(f"   附  件: 重慶美食之旅.pptx")
            print(f"   時  間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
            
    except smtplib.SMTPAuthenticationError:
        print("❌ 認證失敗: 請檢查Gmail密碼或應用專用密碼")
        print("💡 提示: 可能需要啟用Gmail的兩步驗證並生成應用專用密碼")
        return False
        
    except Exception as e:
        print(f"❌ 發送郵件失敗: {e}")
        print("💡 可能原因:")
        print("   1. 網絡連接問題")
        print("   2. Gmail SMTP設置問題")
        print("   3. 防火牆或安全軟件阻擋")
        return False

def main():
    """主函數"""
    print("🎯 發送重慶美食PPT到指定郵箱")
    print("=" * 50)
    
    success = send_ppt_email()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 任務完成！PPT已成功發送到 gordonlct125@gmail.com")
        print("\n📋 下一步:")
        print("   1. 檢查收件箱（包括垃圾郵件文件夾）")
        print("   2. 下載並查看PPT文件")
        print("   3. 如有問題請告知")
    else:
        print("❌ 郵件發送失敗，請檢查上述錯誤信息")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
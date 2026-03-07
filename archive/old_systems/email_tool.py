#!/usr/bin/env python3
"""
OpenClaw郵件工具
用於從OpenClaw發送和管理郵件
"""

import smtplib
import sys
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import argparse

# Gmail配置
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = 'zero850x@gmail.com'
PASSWORD = 'hebr wwxy syqo xwbq'  # 應用程式專用密碼

def send_email(to, subject, body, from_name="Gordon Lui (OpenClaw)"):
    """
    發送郵件
    
    參數:
    - to: 收件人郵箱
    - subject: 郵件主題
    - body: 郵件內容
    - from_name: 發件人名稱
    """
    try:
        # 創建郵件
        msg = MIMEMultipart()
        msg['From'] = f"{from_name} <{USERNAME}>"
        msg['To'] = to
        msg['Subject'] = subject
        
        # 添加正文
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 創建SSL上下文
        context = ssl.create_default_context()
        
        # 連接SMTP服務器
        print(f"連接至 {SMTP_SERVER}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            print("TLS加密已啟動")
            
            print(f"登入帳號: {USERNAME}")
            server.login(USERNAME, PASSWORD)
            print("登入成功")
            
            print(f"發送郵件到: {to}")
            server.send_message(msg)
            print("✅ 郵件發送成功！")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP認證錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 發送失敗: {e}")
        return False

def check_inbox():
    """檢查收件箱（使用Himalaya）"""
    print("檢查收件箱...")
    os.system("himalaya envelope list --page-size 5")

def read_email(email_id):
    """閱讀特定郵件"""
    print(f"閱讀郵件 ID: {email_id}")
    os.system(f"himalaya message read {email_id}")

def list_folders():
    """列出郵件文件夾"""
    print("郵件文件夾列表:")
    os.system("himalaya folder list")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='OpenClaw郵件工具')
    subparsers = parser.add_subparsers(dest='command', help='可用的命令')
    
    # 發送郵件命令
    send_parser = subparsers.add_parser('send', help='發送郵件')
    send_parser.add_argument('--to', required=True, help='收件人郵箱')
    send_parser.add_argument('--subject', required=True, help='郵件主題')
    send_parser.add_argument('--body', required=True, help='郵件內容')
    send_parser.add_argument('--from-name', default='Gordon Lui (OpenClaw)', help='發件人名稱')
    
    # 檢查收件箱命令
    subparsers.add_parser('inbox', help='檢查收件箱（最近5封）')
    
    # 閱讀郵件命令
    read_parser = subparsers.add_parser('read', help='閱讀特定郵件')
    read_parser.add_argument('id', help='郵件ID')
    
    # 列出文件夾命令
    subparsers.add_parser('folders', help='列出郵件文件夾')
    
    # 幫助命令
    subparsers.add_parser('help', help='顯示幫助信息')
    
    args = parser.parse_args()
    
    if args.command == 'send':
        success = send_email(args.to, args.subject, args.body, args.from_name)
        if not success:
            sys.exit(1)
            
    elif args.command == 'inbox':
        check_inbox()
        
    elif args.command == 'read':
        read_email(args.id)
        
    elif args.command == 'folders':
        list_folders()
        
    elif args.command == 'help' or not args.command:
        print("""
OpenClaw郵件工具 - 使用方法
        
命令:
  send     發送郵件
    --to        收件人郵箱
    --subject   郵件主題
    --body      郵件內容
    --from-name 發件人名稱（可選）
    
  inbox    檢查收件箱（顯示最近5封郵件）
  read     閱讀特定郵件
    <id>       郵件ID
  folders  列出郵件文件夾
  help     顯示此幫助信息

示例:
  python3 email_tool.py send --to "friend@example.com" --subject "你好" --body "這是一封測試郵件"
  python3 email_tool.py inbox
  python3 email_tool.py read 23
  python3 email_tool.py folders
        """)

if __name__ == "__main__":
    main()
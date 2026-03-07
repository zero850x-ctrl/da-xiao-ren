#!/usr/bin/env python3
"""
發送OpenClaw工作空間中的所有.md文件到指定郵箱
"""

import os
import smtplib
import zipfile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl
from pathlib import Path

# 配置
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = 'zero850x@gmail.com'
PASSWORD = 'hebr wwxy syqo xwbq'
TO_EMAIL = 'zero850x@gmail.com'
WORKSPACE_DIR = '/Users/gordonlui/.openclaw/workspace'

def find_md_files(directory):
    """查找所有.md文件"""
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                md_files.append(full_path)
    return md_files

def create_zip_file(md_files, zip_filename):
    """創建包含所有.md文件的ZIP壓縮包"""
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in md_files:
            # 計算相對路徑
            rel_path = os.path.relpath(file_path, WORKSPACE_DIR)
            zipf.write(file_path, rel_path)
            print(f"已添加: {rel_path}")
    return zip_filename

def create_summary_email(md_files):
    """創建包含所有文件內容的摘要郵件"""
    summary = "# OpenClaw工作空間.md文件匯總\n\n"
    summary += f"共找到 {len(md_files)} 個.md文件\n\n"
    
    for file_path in md_files:
        rel_path = os.path.relpath(file_path, WORKSPACE_DIR)
        summary += f"## {rel_path}\n\n"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 限制每個文件顯示前500字符
                if len(content) > 500:
                    content = content[:500] + "\n\n...（內容過長，已截斷）"
                summary += f"```markdown\n{content}\n```\n\n"
        except Exception as e:
            summary += f"讀取錯誤: {e}\n\n"
    
    return summary

def send_email_with_attachment(subject, body, attachment_path=None):
    """發送帶附件的郵件"""
    try:
        # 創建郵件
        msg = MIMEMultipart()
        msg['From'] = f"OpenClaw助理 <{USERNAME}>"
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject
        
        # 添加正文
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 添加附件（如果有）
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                
                # 設置附件頭部
                filename = os.path.basename(attachment_path)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{filename}"'
                )
                msg.attach(part)
                print(f"已添加附件: {filename}")
        
        # 發送郵件
        context = ssl.create_default_context()
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(USERNAME, PASSWORD)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"發送失敗: {e}")
        return False

def main():
    print("正在查找.md文件...")
    md_files = find_md_files(WORKSPACE_DIR)
    
    if not md_files:
        print("未找到任何.md文件")
        return
    
    print(f"找到 {len(md_files)} 個.md文件:")
    for file in md_files:
        print(f"  - {os.path.relpath(file, WORKSPACE_DIR)}")
    
    # 創建ZIP文件
    print("\n創建ZIP壓縮包...")
    zip_filename = os.path.join(WORKSPACE_DIR, 'openclaw_md_files.zip')
    create_zip_file(md_files, zip_filename)
    print(f"ZIP文件已創建: {zip_filename}")
    
    # 創建摘要
    print("\n創建文件摘要...")
    summary = create_summary_email(md_files)
    
    # 發送郵件
    print("\n發送郵件...")
    subject = f"OpenClaw工作空間.md文件匯總 ({len(md_files)}個文件)"
    body = f"""OpenClaw工作空間中的所有.md文件已打包完成。

共包含 {len(md_files)} 個文件：
{chr(10).join([f"- {os.path.relpath(f, WORKSPACE_DIR)}" for f in md_files])}

ZIP壓縮包已作為附件發送。
文件摘要請見下方。
"""
    
    # 發送帶附件的郵件
    if send_email_with_attachment(subject, body, zip_filename):
        print("✅ 郵件發送成功！")
        
        # 發送詳細內容郵件
        print("\n發送詳細內容郵件...")
        detail_subject = "OpenClaw工作空間.md文件詳細內容"
        if send_email_with_attachment(detail_subject, summary):
            print("✅ 詳細內容郵件發送成功！")
        else:
            print("❌ 詳細內容郵件發送失敗")
        
        # 清理臨時文件
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
            print(f"已清理臨時文件: {zip_filename}")
    else:
        print("❌ 郵件發送失敗")

if __name__ == "__main__":
    main()
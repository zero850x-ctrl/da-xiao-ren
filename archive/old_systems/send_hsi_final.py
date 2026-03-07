#!/usr/bin/env python3
"""
使用現有SMTP配置發送HSI技術分析報告
"""

import smtplib
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import sys

# Gmail SMTP配置（從test_smtp.py獲取）
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = 'zero850x@gmail.com'
PASSWORD = '990prot500'

def read_report():
    """讀取技術分析報告"""
    try:
        with open('hsi_technical_analysis_report.txt', 'r', encoding='utf-8') as f:
            report = f.read()
        
        with open('hsi_realtime.json', 'r') as f:
            realtime_data = json.load(f)
        
        return report, realtime_data
    except Exception as e:
        print(f"❌ 讀取報告失敗: {e}")
        return None, None

def create_email_content(report, realtime_data):
    """創建郵件內容"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 提取報告中的關鍵部分
    lines = report.split('\n')
    key_sections = []
    
    # 找到關鍵部分
    sections_to_extract = [
        "HSI 技術分析報告",
        "📊 當前市場狀態:",
        "📈 移動平均線分析",
        "📊 RSI指標",
        "📊 成交量分析",
        "📐 斐波那契回撤水平:",
        "🎯 趨勢判斷:",
        "🛡️  關鍵支撐阻力位:",
        "🔮 下周走勢預測:",
        "⚠️  風險提示:"
    ]
    
    for i, line in enumerate(lines):
        for section in sections_to_extract:
            if section in line:
                key_sections.append(line)
                # 添加接下來的幾行
                for j in range(1, 5):
                    if i + j < len(lines) and lines[i + j].strip():
                        key_sections.append(lines[i + j])
                key_sections.append("")  # 空行
    
    summary = "\n".join(key_sections)
    
    email_body = f"""📊 HSI 技術分析報告
📅 生成時間: {current_time}
🔗 數據來源: Futu OpenD

📈 市場概覽:
最新價格: {realtime_data['last_price']}
漲跌幅: {realtime_data['change_rate']:.2f}%
成交量: {realtime_data['volume']:,}
成交額: {realtime_data['turnover']:,.0f}
更新時間: {realtime_data['update_time']}

📋 技術分析摘要:
{summary}

📎 附件包含完整報告和圖表

⚠️ 免責聲明:
本報告基於技術分析，僅供參考。投資有風險，請謹慎決策。

--
OpenClaw Assistant
自動化技術分析系統
數據來源: Futu OpenD
"""
    return email_body

def send_email_with_attachments(email_body, attachments):
    """使用SMTP發送帶附件的郵件"""
    try:
        print(f"📧 準備發送郵件...")
        print(f"發件人: {USERNAME}")
        print(f"收件人: {USERNAME}")
        print(f"SMTP服務器: {SMTP_SERVER}:{SMTP_PORT}")
        
        # 創建郵件
        msg = MIMEMultipart()
        msg['From'] = f"OpenClaw Assistant <{USERNAME}>"
        msg['To'] = USERNAME
        msg['Subject'] = f"HSI技術分析報告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 添加正文
        msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
        
        # 添加附件
        attachment_count = 0
        for attachment in attachments:
            if os.path.exists(attachment):
                try:
                    with open(attachment, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    
                    encoders.encode_base64(part)
                    filename = os.path.basename(attachment)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{filename}"'
                    )
                    msg.attach(part)
                    attachment_count += 1
                    print(f"✅ 添加附件: {filename}")
                except Exception as e:
                    print(f"⚠️  添加附件失敗 {attachment}: {e}")
        
        # 連接SMTP服務器並發送
        print(f"\n🔗 連接SMTP服務器...")
        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        print("✅ 連接成功!")
        
        print("🔐 啟用TLS加密...")
        smtp.starttls()
        print("✅ TLS啟用成功!")
        
        print(f"🔑 登錄帳戶...")
        smtp.login(USERNAME, PASSWORD)
        print("✅ 登錄成功!")
        
        print("🚀 發送郵件...")
        smtp.send_message(msg)
        print("✅ 郵件發送成功!")
        
        # 關閉連接
        smtp.quit()
        print("✅ SMTP連接關閉")
        
        return True, attachment_count
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP認證失敗: {e}")
        print("請檢查用戶名和密碼是否正確")
        return False, 0
    except Exception as e:
        print(f"❌ 發送郵件失敗: {e}")
        import traceback
        traceback.print_exc()
        return False, 0

def check_attachments():
    """檢查附件文件是否存在"""
    attachments = [
        'hsi_technical_analysis_report.txt',
        'hsi_technical_chart.png',
        'hsi_history.csv',
        'hsi_realtime.json',
        'hsi_history.json'
    ]
    
    existing_attachments = []
    for attachment in attachments:
        if os.path.exists(attachment):
            existing_attachments.append(attachment)
            print(f"✅ 找到附件: {attachment}")
        else:
            print(f"⚠️  缺少附件: {attachment}")
    
    return existing_attachments

def main():
    print("=" * 60)
    print("📧 HSI技術分析報告郵件發送")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 檢查附件
    print("\n📎 檢查附件文件...")
    attachments = check_attachments()
    
    if len(attachments) < 2:
        print("❌ 附件文件不足，無法發送郵件")
        return False
    
    # 讀取報告
    print("\n📄 讀取技術分析報告...")
    report, realtime_data = read_report()
    
    if not report or not realtime_data:
        print("❌ 無法讀取報告或數據")
        return False
    
    print(f"✅ 報告讀取成功")
    print(f"   最新價格: {realtime_data['last_price']}")
    print(f"   漲跌幅: {realtime_data['change_rate']:.2f}%")
    
    # 創建郵件內容
    print("\n✍️  創建郵件內容...")
    email_body = create_email_content(report, realtime_data)
    
    # 顯示郵件摘要
    print("\n📋 郵件摘要:")
    lines = email_body.split('\n')
    for i in range(min(15, len(lines))):
        print(f"  {lines[i]}")
    print("  ...")
    
    # 發送郵件
    print("\n🚀 發送郵件到 zero850x@gmail.com...")
    success, attachment_count = send_email_with_attachments(email_body, attachments)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 郵件發送成功！")
        print(f"收件人: {USERNAME}")
        print(f"發送時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"附件數量: {attachment_count}")
        print("=" * 60)
        
        # 顯示關鍵預測
        print("\n🎯 關鍵技術分析預測:")
        lines = report.split('\n')
        for line in lines:
            if "下周走勢預測" in line or "偏多看法" in line or "偏空看法" in line or "震盪看法" in line:
                print(f"  {line}")
            if "支撐位:" in line or "阻力位:" in line or "目標位:" in line:
                print(f"  {line}")
        
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ 郵件發送失敗")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ 所有任務完成！")
        print("技術分析報告已成功發送到 zero850x@gmail.com")
        print("\n📁 生成的文件:")
        files = [
            'hsi_technical_analysis_report.txt',
            'hsi_technical_chart.png',
            'hsi_history.csv',
            'hsi_realtime.json',
            'hsi_history.json'
        ]
        for file in files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"  ✅ {file} ({size:,} bytes)")
    else:
        print("\n❌ 任務失敗")
        sys.exit(1)
#!/usr/bin/env python3
"""
直接使用SMTP發送HSI技術分析報告郵件
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
    
    email_body = f"""📊 HSI 技術分析報告
📅 生成時間: {current_time}
🔗 數據來源: Futu OpenD

📈 市場概覽:
最新價格: {realtime_data['last_price']}
漲跌幅: {realtime_data['change_rate']:.2f}%
成交量: {realtime_data['volume']:,}
成交額: {realtime_data['turnover']:,.0f}
更新時間: {realtime_data['update_time']}

{report}

📎 附件包含:
1. hsi_technical_analysis_report.txt - 完整技術分析報告
2. hsi_technical_chart.png - 技術分析圖表
3. hsi_history.csv - 歷史數據CSV
4. hsi_realtime.json - 實時數據JSON
5. hsi_history.json - 歷史數據JSON

⚠️ 免責聲明:
本報告基於技術分析，僅供參考。投資有風險，請謹慎決策。

--
OpenClaw Assistant
自動化技術分析系統
數據來源: Futu OpenD
"""
    return email_body

def send_email_direct(email_body, attachments):
    """直接使用SMTP發送郵件"""
    try:
        # 郵件配置（需要根據實際情況修改）
        # 這裡使用Gmail SMTP服務器
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # 發件人信息（需要實際的Gmail帳戶）
        sender_email = "your_email@gmail.com"  # 需要修改
        sender_password = "your_app_password"  # 需要修改（應用專用密碼）
        
        # 收件人
        receiver_email = "zero850x@gmail.com"
        
        print(f"📧 準備發送郵件...")
        print(f"發件人: {sender_email}")
        print(f"收件人: {receiver_email}")
        print(f"SMTP服務器: {smtp_server}:{smtp_port}")
        
        # 創建郵件
        msg = MIMEMultipart()
        msg['From'] = f"OpenClaw Assistant <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"HSI技術分析報告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 添加正文
        msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
        
        # 添加附件
        for attachment in attachments:
            if os.path.exists(attachment):
                try:
                    with open(attachment, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{os.path.basename(attachment)}"'
                    )
                    msg.attach(part)
                    print(f"✅ 添加附件: {attachment}")
                except Exception as e:
                    print(f"⚠️  添加附件失敗 {attachment}: {e}")
        
        # 連接SMTP服務器並發送
        print(f"\n🔗 連接SMTP服務器...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # 啟用TLS加密
        
        # 登錄（需要實際的帳戶信息）
        print(f"🔐 登錄SMTP服務器...")
        # 注意：這裡需要實際的Gmail帳戶和應用專用密碼
        # server.login(sender_email, sender_password)
        
        # 發送郵件
        print(f"🚀 發送郵件...")
        # text = msg.as_string()
        # server.sendmail(sender_email, receiver_email, text)
        
        # 關閉連接
        server.quit()
        
        print(f"✅ 郵件發送成功（模擬）")
        print(f"⚠️  注意：這是一個模擬發送")
        print(f"    需要配置實際的Gmail帳戶和應用專用密碼")
        
        return True
        
    except Exception as e:
        print(f"❌ 發送郵件失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

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

def create_summary_file(email_body, attachments):
    """創建摘要文件，包含所有內容"""
    try:
        summary_file = "hsi_analysis_summary.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("HSI技術分析報告 - 完整摘要\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(email_body)
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("附件列表:\n")
            for i, attachment in enumerate(attachments, 1):
                f.write(f"{i}. {attachment}\n")
            f.write("=" * 60 + "\n")
        
        print(f"✅ 創建摘要文件: {summary_file}")
        return summary_file
        
    except Exception as e:
        print(f"❌ 創建摘要文件失敗: {e}")
        return None

def main():
    print("=" * 60)
    print("📧 HSI技術分析報告郵件發送（直接SMTP）")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 檢查附件
    print("\n📎 檢查附件文件...")
    attachments = check_attachments()
    
    if len(attachments) < 2:
        print("❌ 附件文件不足")
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
    
    # 顯示摘要
    print("\n📋 報告摘要:")
    lines = email_body.split('\n')
    for i in range(min(20, len(lines))):
        print(f"  {lines[i]}")
    if len(lines) > 20:
        print("  ...")
    
    # 創建摘要文件
    print("\n💾 創建摘要文件...")
    summary_file = create_summary_file(email_body, attachments)
    if summary_file:
        attachments.append(summary_file)
    
    # 嘗試發送郵件
    print("\n🚀 嘗試發送郵件...")
    print("⚠️  注意：需要配置實際的Gmail帳戶才能發送")
    print("    目前只創建文件，不實際發送")
    
    # 模擬發送（實際需要配置Gmail帳戶）
    success = send_email_direct(email_body, attachments)
    
    if success:
        print("\n" + "=" * 60)
        print("📁 文件創建完成！")
        print("已創建以下文件:")
        for attachment in attachments:
            if os.path.exists(attachment):
                size = os.path.getsize(attachment)
                print(f"  ✅ {attachment} ({size:,} bytes)")
        
        print("\n📧 要實際發送郵件，需要:")
        print("1. 修改 send_email_direct.py 中的發件人信息")
        print("2. 使用Gmail應用專用密碼")
        print("3. 取消註釋發送代碼")
        print("=" * 60)
        
        # 顯示報告中的關鍵預測
        print("\n🎯 關鍵技術分析預測:")
        lines = report.split('\n')
        for line in lines:
            if "下周走勢預測" in line or "偏多看法" in line or "偏空看法" in line or "震盪看法" in line:
                print(f"  {line}")
            if "支撐位:" in line or "阻力位:" in line or "目標位:" in line:
                print(f"  {line}")
        
        return True
    else:
        print("\n❌ 郵件發送失敗")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ 技術分析完成！")
        print("所有文件已保存在工作區目錄")
        print("可以手動發送郵件給 zero850x@gmail.com")
    else:
        print("\n❌ 任務失敗")
        sys.exit(1)
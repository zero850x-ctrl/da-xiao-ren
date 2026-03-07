#!/usr/bin/env python3
"""
使用應用專用密碼發送HSI技術分析報告
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
import ssl

# Gmail SMTP配置（使用應用專用密碼）
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = 'zero850x@gmail.com'
PASSWORD = 'hebr wwxy syqo xwbq'  # 應用程式專用密碼

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
    
    # 提取關鍵摘要
    lines = report.split('\n')
    summary_lines = []
    
    # 提取重要部分
    important_sections = [
        "HSI 技術分析報告",
        "📊 當前市場狀態:",
        "📈 移動平均線分析",
        "📊 RSI指標",
        "📊 成交量分析",
        "🔮 下周走勢預測:",
        "⚠️  風險提示:"
    ]
    
    for i, line in enumerate(lines):
        for section in important_sections:
            if section in line:
                summary_lines.append(line)
                # 添加接下來的幾行
                for j in range(1, 4):
                    if i + j < len(lines) and lines[i + j].strip():
                        summary_lines.append(lines[i + j])
                summary_lines.append("")
                break
    
    summary = "\n".join(summary_lines[:30])  # 限制長度
    
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

📎 附件包含:
1. hsi_technical_analysis_report.txt - 完整技術分析報告
2. hsi_technical_chart.png - 技術分析圖表
3. hsi_history.csv - 歷史數據CSV

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
        
        # 添加附件（只添加最重要的3個）
        important_attachments = [
            'hsi_technical_analysis_report.txt',
            'hsi_technical_chart.png',
            'hsi_history.csv'
        ]
        
        attachment_count = 0
        for attachment in important_attachments:
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
        
        # 創建SSL上下文
        context = ssl.create_default_context()
        
        # 連接SMTP服務器並發送
        print(f"\n🔗 連接SMTP服務器...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            print("✅ 連接成功!")
            
            print("🔐 啟用TLS加密...")
            smtp.starttls(context=context)
            print("✅ TLS啟用成功!")
            
            print(f"🔑 登錄帳戶...")
            smtp.login(USERNAME, PASSWORD)
            print("✅ 登錄成功!")
            
            print("🚀 發送郵件...")
            smtp.send_message(msg)
            print("✅ 郵件發送成功!")
        
        return True, attachment_count
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP認證失敗: {e}")
        print("請檢查應用專用密碼是否正確")
        return False, 0
    except Exception as e:
        print(f"❌ 發送郵件失敗: {e}")
        import traceback
        traceback.print_exc()
        return False, 0

def main():
    print("=" * 60)
    print("📧 HSI技術分析報告郵件發送")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 檢查附件
    print("\n📎 檢查附件文件...")
    attachments = [
        'hsi_technical_analysis_report.txt',
        'hsi_technical_chart.png',
        'hsi_history.csv'
    ]
    
    existing_attachments = []
    for attachment in attachments:
        if os.path.exists(attachment):
            existing_attachments.append(attachment)
            print(f"✅ 找到附件: {attachment}")
        else:
            print(f"❌ 缺少附件: {attachment}")
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
    
    # 顯示關鍵信息
    print("\n🎯 關鍵分析結果:")
    print(f"  最新價格: {realtime_data['last_price']}")
    print(f"  漲跌幅: {realtime_data['change_rate']:.2f}%")
    
    # 從報告中提取預測
    lines = report.split('\n')
    for line in lines:
        if "下周走勢預測" in line:
            print(f"  {line}")
            # 打印接下來的幾行
            idx = lines.index(line)
            for i in range(1, 6):
                if idx + i < len(lines) and lines[idx + i].strip():
                    print(f"    {lines[idx + i]}")
    
    # 發送郵件
    print("\n🚀 發送郵件到 zero850x@gmail.com...")
    success, attachment_count = send_email_with_attachments(email_body, existing_attachments)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 郵件發送成功！")
        print(f"收件人: {USERNAME}")
        print(f"發送時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"附件數量: {attachment_count}")
        print("=" * 60)
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
        print("\n📊 分析完成:")
        print("1. ✅ Futu OpenD連接問題已解決")
        print("2. ✅ 技術分析工具已創建")
        print("3. ✅ 完整報告和圖表已生成")
        print("4. ✅ 郵件已發送")
    else:
        print("\n❌ 任務失敗")
        sys.exit(1)
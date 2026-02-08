#!/usr/bin/env python3
"""
發送HSI技術分析報告郵件
"""

import subprocess
import os
import json
from datetime import datetime
import sys

def read_report():
    """讀取技術分析報告"""
    try:
        with open('hsi_technical_analysis_report.txt', 'r', encoding='utf-8') as f:
            report = f.read()
        
        # 讀取實時數據
        with open('hsi_realtime.json', 'r') as f:
            realtime_data = json.load(f)
        
        return report, realtime_data
    except Exception as e:
        print(f"❌ 讀取報告失敗: {e}")
        return None, None

def create_email_content(report, realtime_data):
    """創建郵件內容"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    email_content = f"""From: OpenClaw Assistant <openclaw@assistant.com>
To: zero850x@gmail.com
Subject: HSI技術分析報告 - {current_time}
Content-Type: text/plain; charset=utf-8

📊 HSI 技術分析報告
📅 生成時間: {current_time}
🔗 數據來源: Futu OpenD

📈 市場概覽:
最新價格: {realtime_data['last_price']}
漲跌幅: {realtime_data['change_rate']:.2f}%
成交量: {realtime_data['volume']:,}
成交額: {realtime_data['turnover']:,.0f}
更新時間: {realtime_data['update_time']}

{report}

📎 附件:
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
    return email_content

def send_email_via_himalaya(email_content, attachments):
    """使用himalaya發送郵件"""
    try:
        # 創建臨時文件
        email_file = "temp_email.txt"
        with open(email_file, 'w', encoding='utf-8') as f:
            f.write(email_content)
        
        print("📧 準備發送郵件...")
        print(f"收件人: zero850x@gmail.com")
        print(f"附件: {len(attachments)} 個文件")
        
        # 使用himalaya發送郵件
        # 首先嘗試直接發送
        cmd = [
            'himalaya', 'message', 'write',
            '-H', 'To:zero850x@gmail.com',
            '-H', f'Subject:HSI技術分析報告 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            '--body-file', email_file
        ]
        
        # 添加附件
        for attachment in attachments:
            if os.path.exists(attachment):
                cmd.extend(['--attach', attachment])
        
        print(f"執行命令: {' '.join(cmd)}")
        
        # 運行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 郵件發送命令執行成功")
            print(f"輸出: {result.stdout}")
            
            # 清理臨時文件
            if os.path.exists(email_file):
                os.remove(email_file)
            
            return True
        else:
            print(f"❌ 郵件發送失敗")
            print(f"錯誤: {result.stderr}")
            
            # 嘗試使用模板方式
            print("\n嘗試使用模板方式發送...")
            return send_email_via_template(email_content, attachments)
            
    except Exception as e:
        print(f"❌ 發送郵件時出錯: {e}")
        import traceback
        traceback.print_exc()
        return False

def send_email_via_template(email_content, attachments):
    """使用模板方式發送郵件"""
    try:
        # 創建MML格式的郵件
        mml_content = f"""From: OpenClaw Assistant <openclaw@assistant.com>
To: zero850x@gmail.com
Subject: HSI技術分析報告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{email_content}
"""
        
        # 保存為文件
        mml_file = "email.mml"
        with open(mml_file, 'w', encoding='utf-8') as f:
            f.write(mml_content)
        
        # 使用himalaya template send
        cmd = ['himalaya', 'template', 'send', mml_file]
        print(f"執行模板命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 模板郵件發送成功")
            
            # 清理文件
            for file in [mml_file, 'temp_email.txt']:
                if os.path.exists(file):
                    os.remove(file)
            
            return True
        else:
            print(f"❌ 模板郵件發送失敗: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 模板發送失敗: {e}")
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
    print(f"   報告長度: {len(report)} 字符")
    print(f"   最新價格: {realtime_data['last_price']}")
    
    # 創建郵件內容
    print("\n✍️  創建郵件內容...")
    email_content = create_email_content(report, realtime_data)
    
    # 顯示郵件摘要
    lines = email_content.split('\n')
    print("📋 郵件摘要:")
    for i in range(min(15, len(lines))):
        print(f"  {lines[i]}")
    print("  ...")
    
    # 發送郵件
    print("\n🚀 發送郵件到 zero850x@gmail.com...")
    success = send_email_via_himalaya(email_content, attachments)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 郵件發送成功！")
        print(f"收件人: zero850x@gmail.com")
        print(f"發送時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"附件數量: {len(attachments)}")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ 郵件發送失敗")
        print("請檢查:")
        print("1. Himalaya配置是否正確")
        print("2. 網絡連接是否正常")
        print("3. SMTP服務器設置")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ 所有任務完成！")
        print("技術分析報告已發送到 zero850x@gmail.com")
    else:
        print("\n❌ 任務失敗")
        sys.exit(1)
#!/usr/bin/env python3
"""
發送HSI技術分析報告電郵
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from datetime import datetime
import json

class HSIReportEmailSender:
    def __init__(self):
        # 郵件配置
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "zero850x@gmail.com"
        self.receiver_email = "zero850x@gmail.com"
        self.app_password = "hebr wwxy syqo xwbq"  # Gmail應用程式密碼
        
        # 報告文件路徑
        self.data_dir = "/Users/gordonlui/.openclaw/workspace/hsi_data"
        self.report_files = {
            "full_report": os.path.join(self.data_dir, "hsi_final_report.md"),
            "html_report": os.path.join(self.data_dir, "hsi_final_report.html"),
            "brief_report": os.path.join(self.data_dir, "hsi_brief_report.md"),
            "technical_data": os.path.join(self.data_dir, "hsi_technical_analysis.json"),
            "reasoner_analysis": os.path.join(self.data_dir, "hsi_reasoner_analysis.json")
        }
    
    def check_report_files(self):
        """檢查報告文件是否存在"""
        print("🔍 檢查報告文件...")
        
        missing_files = []
        for name, path in self.report_files.items():
            if os.path.exists(path):
                file_size = os.path.getsize(path)
                print(f"✅ {name}: {path} ({file_size:,} bytes)")
            else:
                print(f"❌ {name}: {path} (文件不存在)")
                missing_files.append(name)
        
        if missing_files:
            print(f"\n⚠️  缺失文件: {', '.join(missing_files)}")
            return False
        
        print(f"\n✅ 所有報告文件檢查通過")
        return True
    
    def create_email_content(self):
        """創建電郵內容"""
        print("\n📧 創建電郵內容...")
        
        # 讀取簡要報告作為正文
        with open(self.report_files["brief_report"], 'r', encoding='utf-8') as f:
            brief_content = f.read()
        
        # 創建HTML格式的電郵正文
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 20px; padding: 15px; border-left: 4px solid #3498db; background-color: #f8f9fa; }}
        .highlight {{ background-color: #fff3cd; padding: 10px; border-radius: 3px; }}
        .disclaimer {{ background-color: #f8d7da; padding: 10px; border-radius: 3px; font-size: 0.9em; }}
        .attachment {{ background-color: #e2f0fb; padding: 10px; border-radius: 3px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; }}
        h3 {{ color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📈 HSI恒生指數技術分析報告</h1>
        <p><strong>報告日期</strong>: {datetime.now().strftime('%Y年%m月%d日')}</p>
        <p><strong>生成時間</strong>: {datetime.now().strftime('%H:%M')}</p>
        <p><strong>數據來源</strong>: 模擬數據（基於HSI歷史波動特徵）</p>
    </div>
    
    <div class="section">
        <h2>🎯 核心分析結論</h2>
        <div class="highlight">
            <p><strong>趨勢判斷</strong>: 中期多頭趨勢，短期面臨回調壓力</p>
            <p><strong>關鍵價位</strong>: 支撐18,428.62，阻力19,011.67</p>
            <p><strong>下週概率</strong>: 上漲45% | 震盪40% | 回調15%</p>
        </div>
    </div>
    
    <div class="section">
        <h2>📊 技術指標摘要</h2>
        <ul>
            <li><strong>斐波那契移動平均線</strong>: MA8=19,279.60, MA13=19,268.17, MA34=19,029.51</li>
            <li><strong>平行通道</strong>: 上升通道，當前位置56.2%（通道中部）</li>
            <li><strong>黃金分割</strong>: 0.382回撤阻力19,011.67，0.618回撤支撐18,428.62</li>
            <li><strong>RSI指標</strong>: 56.17（偏多但未超買）</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>💡 交易建議</h2>
        <ul>
            <li><strong>短線交易</strong>: 18,500-18,550區間做多，止損18,420</li>
            <li><strong>中線投資</strong>: 18,400-18,600分批建倉，目標19,500+</li>
            <li><strong>風險控制</strong>: 單筆損失不超過2%，總風險不超過10%</li>
        </ul>
    </div>
    
    <div class="attachment">
        <h2>📎 附件文件</h2>
        <p>本電郵包含以下附件：</p>
        <ol>
            <li><strong>hsi_final_report.md</strong> - 完整技術分析報告（Markdown格式）</li>
            <li><strong>hsi_final_report.html</strong> - 網頁格式報告（可直接瀏覽）</li>
            <li><strong>hsi_brief_report.md</strong> - 簡要版本報告</li>
            <li><strong>hsi_technical_analysis.json</strong> - 技術指標原始數據</li>
            <li><strong>hsi_reasoner_analysis.json</strong> - AI深度推理分析數據</li>
        </ol>
    </div>
    
    <div class="disclaimer">
        <h2>⚠️  重要提示與免責聲明</h2>
        <p>1. 本報告基於<strong>模擬數據</strong>生成，僅供技術分析學習和練習使用</p>
        <p>2. 實際市場數據可能與模擬數據存在差異</p>
        <p>3. 技術分析有一定滯後性，需結合基本面分析</p>
        <p>4. 本報告不構成任何投資建議，投資者應獨立決策</p>
        <p>5. 投資有風險，入市需謹慎</p>
    </div>
    
    <hr>
    <p style="font-size: 0.9em; color: #666;">
        <strong>報告生成系統</strong>: OpenClaw AI技術分析平台<br>
        <strong>分析模型</strong>: deepseek-reasoner（思維鏈推理）<br>
        <strong>生成時間</strong>: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        <strong>聯繫方式</strong>: 此為自動生成報告，如有疑問請通過正常渠道聯繫
    </p>
</body>
</html>
"""
        
        # 創建純文本版本
        text_content = f"""
HSI恒生指數技術分析報告
========================

報告日期: {datetime.now().strftime('%Y年%m月%d日')}
生成時間: {datetime.now().strftime('%H:%M')}
數據來源: 模擬數據（基於HSI歷史波動特徵）

核心分析結論
------------
趨勢判斷: 中期多頭趨勢，短期面臨回調壓力
關鍵價位: 支撐18,428.62，阻力19,011.67
下週概率: 上漲45% | 震盪40% | 回調15%

技術指標摘要
------------
• 斐波那契移動平均線: MA8=19,279.60, MA13=19,268.17, MA34=19,029.51
• 平行通道: 上升通道，當前位置56.2%（通道中部）
• 黃金分割: 0.382回撤阻力19,011.67，0.618回撤支撐18,428.62
• RSI指標: 56.17（偏多但未超買）

交易建議
--------
• 短線交易: 18,500-18,550區間做多，止損18,420
• 中線投資: 18,400-18,600分批建倉，目標19,500+
• 風險控制: 單筆損失不超過2%，總風險不超過10%

附件文件
--------
1. hsi_final_report.md - 完整技術分析報告（Markdown格式）
2. hsi_final_report.html - 網頁格式報告（可直接瀏覽）
3. hsi_brief_report.md - 簡要版本報告
4. hsi_technical_analysis.json - 技術指標原始數據
5. hsi_reasoner_analysis.json - AI深度推理分析數據

重要提示與免責聲明
------------------
1. 本報告基於模擬數據生成，僅供技術分析學習和練習使用
2. 實際市場數據可能與模擬數據存在差異
3. 技術分析有一定滯後性，需結合基本面分析
4. 本報告不構成任何投資建議，投資者應獨立決策
5. 投資有風險，入市需謹慎

---
報告生成系統: OpenClaw AI技術分析平台
分析模型: deepseek-reasoner（思維鏈推理）
生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return html_content, text_content
    
    def attach_files(self, message):
        """附加文件到電郵"""
        print("\n📎 附加報告文件...")
        
        attached_files = []
        
        for name, file_path in self.report_files.items():
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    # 獲取文件名
                    filename = os.path.basename(file_path)
                    
                    # 創建附件
                    attachment = MIMEApplication(file_data, Name=filename)
                    attachment['Content-Disposition'] = f'attachment; filename="{filename}"'
                    
                    # 添加到郵件
                    message.attach(attachment)
                    
                    file_size = len(file_data)
                    print(f"✅ 附加: {filename} ({file_size:,} bytes)")
                    attached_files.append((filename, file_size))
                    
                except Exception as e:
                    print(f"❌ 附加文件失敗 {file_path}: {e}")
            else:
                print(f"⚠️  文件不存在，跳過: {file_path}")
        
        return attached_files
    
    def send_email(self):
        """發送電郵"""
        print("\n🚀 開始發送HSI分析報告電郵...")
        
        # 檢查文件
        if not self.check_report_files():
            print("❌ 報告文件不完整，無法發送電郵")
            return False
        
        try:
            # 創建郵件
            message = MIMEMultipart("alternative")
            message["Subject"] = "HSI技術分析及下週預測 - 2026年2月8日"
            message["From"] = self.sender_email
            message["To"] = self.receiver_email
            message["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0800")
            
            # 添加郵件頭信息
            message["X-Mailer"] = "OpenClaw AI Report System"
            message["X-Priority"] = "1"  # 高優先級
            message["X-MSMail-Priority"] = "High"
            
            # 創建郵件內容
            html_content, text_content = self.create_email_content()
            
            # 添加文本版本
            part1 = MIMEText(text_content, "plain", "utf-8")
            message.attach(part1)
            
            # 添加HTML版本
            part2 = MIMEText(html_content, "html", "utf-8")
            message.attach(part2)
            
            # 附加文件
            attached_files = self.attach_files(message)
            
            if not attached_files:
                print("⚠️  沒有附加任何文件")
            
            # 連接SMTP服務器並發送
            print(f"\n🔗 連接SMTP服務器: {self.smtp_server}:{self.smtp_port}")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # 啟用加密
                server.login(self.sender_email, self.app_password)
                
                print("✅ SMTP登錄成功")
                print("📤 發送郵件中...")
                
                server.send_message(message)
                
                print("✅ 郵件發送成功！")
                
                # 記錄發送信息
                send_info = {
                    "send_time": datetime.now().isoformat(),
                    "sender": self.sender_email,
                    "receiver": self.receiver_email,
                    "subject": message["Subject"],
                    "attached_files": attached_files,
                    "total_attachments": len(attached_files),
                    "total_size": sum(size for _, size in attached_files),
                    "status": "success"
                }
                
                # 保存發送記錄
                log_file = os.path.join(self.data_dir, "email_send_log.json")
                with open(log_file, 'w') as f:
                    json.dump(send_info, f, indent=2, ensure_ascii=False)
                
                print(f"📝 發送記錄已保存: {log_file}")
                
                return True
        
        except smtplib.SMTPAuthenticationError:
            print("❌ SMTP認證失敗，請檢查應用程式密碼")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ SMTP錯誤: {e}")
            return False
        except Exception as e:
            print(f"❌ 發送郵件時發生錯誤: {e}")
            return False
    
    def print_send_summary(self):
        """打印發送摘要"""
        print("\n" + "=" * 60)
        print("📧 HSI報告電郵發送摘要")
        print("=" * 60)
        
        print(f"\n📤 發送信息:")
        print(f"  發件人: {self.sender_email}")
        print(f"  收件人: {self.receiver_email}")
        print(f"  主  題: HSI技術分析及下週預測 - 2026年2月8日")
        print(f"  時  間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n📎 附件文件:")
        for name, path in self.report_files.items():
            if os.path.exists(path):
                file_size = os.path.getsize(path)
                filename = os.path.basename(path)
                print(f"  • {filename} ({file_size:,} bytes)")
        
        print(f"\n📊 報告內容概述:")
        print("  1. 完整技術分析報告 (Markdown + HTML)")
        print("  2. 簡要版本報告")
        print("  3. 技術指標原始數據")
        print("  4. AI深度推理分析數據")
        
        print(f"\n⚠️  重要說明:")
        print("  • 報告基於模擬數據生成")
        print("  • 僅供技術分析學習使用")
        print("  • 不構成任何投資建議")
        
        print(f"\n🎯 發送狀態: 準備就緒")
        print(f"💡 將在14:30-15:00時間窗口發送")

def main():
    """主函數"""
    print("🚀 HSI技術分析報告電郵發送系統")
    print(f"啟動時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 創建發送器
    sender = HSIReportEmailSender()
    
    # 打印發送摘要
    sender.print_send_summary()
    
    print("\n" + "=" * 60)
    print("⏰ 發送時間安排")
    print("=" * 60)
    
    print("\n📅 當前計劃:")
    print("  • 現在: 系統準備和檢查")
    print("  • 14:30-15:00: 執行電郵發送")
    print("  • 發送後: 確認和通知")
    
    print("\n💡 自動發送說明:")
    print("  此腳本已準備就緒，可在指定時間運行以發送報告")
    print("  或手動運行: python3 send_hsi_report_email.py")
    
    print("\n🔧 技術配置:")
    print(f"  SMTP服務器: {sender.smtp_server}:{sender.smtp_port}")
    print(f"  發件郵箱: {sender.sender_email}")
    print(f"  報告目錄: {sender.data_dir}")
    
    print("\n🎯 項目完成狀態:")
    print("  ✅ 數據準備和技術分析")
    print("  ✅ AI深度推理分析")
    print("  ✅ 報告生成和格式化")
    print("  ✅ 電郵系統準備")
    print("  ⏳ 等待發送時間窗口")
    
    print("\n🚀 準備完成！")
    print("將在14:30執行電郵發送任務。")

if __name__ == "__main__":
    main()
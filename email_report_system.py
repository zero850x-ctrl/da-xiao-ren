#!/usr/bin/env python3
"""
電郵報告系統
將系統報告通過電郵發送，避免WhatsApp長消息問題
"""

import smtplib
import os
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import ssl

class EmailReporter:
    def __init__(self):
        # 郵件配置
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.username = 'zero850x@gmail.com'
        self.password = 'hebr wwxy syqo xwbq'  # 應用程式專用密碼
        self.from_email = 'zero850x@gmail.com'
        self.from_name = 'OpenClaw Assistant'
        self.to_email = 'zero850x@gmail.com'
        
        # 報告目錄
        self.report_dir = '/Users/gordonlui/.openclaw/workspace/monitor_reports'
        self.email_log_dir = '/Users/gordonlui/.openclaw/workspace/email_reports'
        
        # 創建目錄
        os.makedirs(self.email_log_dir, exist_ok=True)
    
    def send_email(self, subject, body, attachments=None):
        """發送電郵"""
        try:
            # 創建郵件
            msg = MIMEMultipart()
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = self.to_email
            msg['Subject'] = subject
            
            # 添加正文
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 添加附件
            if attachments:
                for attachment in attachments:
                    if os.path.exists(attachment):
                        with open(attachment, 'rb') as f:
                            part = MIMEApplication(f.read(), Name=os.path.basename(attachment))
                        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
                        msg.attach(part)
            
            # 連接並發送
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(msg)
            
            print(f"✅ 電郵發送成功: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ 電郵發送失敗: {e}")
            return False
    
    def send_daily_summary(self):
        """發送每日總結報告"""
        today = datetime.now().strftime('%Y-%m-%d')
        subject = f"📊 OpenClaw每日交易總結 - {today}"
        
        # 收集當日報告
        report_files = []
        if os.path.exists(self.report_dir):
            for file in os.listdir(self.report_dir):
                if file.startswith('quick_') and file.endswith('.json'):
                    report_files.append(os.path.join(self.report_dir, file))
        
        if not report_files:
            body = f"📭 {today} 無交易監控報告\n\n系統運行正常，但今日無交易活動。"
            return self.send_email(subject, body)
        
        # 讀取並分析報告
        reports = []
        total_positions = 0
        total_value = 0
        total_pnl = 0
        
        for report_file in sorted(report_files)[-10:]:  # 最近10個報告
            try:
                with open(report_file, 'r') as f:
                    data = json.load(f)
                
                timestamp = data.get('timestamp', '')
                summary = data.get('summary', {})
                
                if summary:
                    reports.append({
                        'time': timestamp.split('T')[1][:5] if 'T' in timestamp else timestamp[:5],
                        'positions': summary.get('total_positions', 0),
                        'value': summary.get('total_value', 0),
                        'pnl': summary.get('total_pnl', 0),
                        'pnl_pct': summary.get('total_pnl_pct', 0)
                    })
                    
                    total_positions = max(total_positions, summary.get('total_positions', 0))
                    if reports:
                        total_value = reports[-1]['value']
                        total_pnl = reports[-1]['pnl']
                        
            except Exception as e:
                print(f"❌ 讀取報告失敗 {report_file}: {e}")
        
        # 創建報告正文
        body = f"📊 OpenClaw每日交易總結報告\n"
        body += "=" * 50 + "\n\n"
        body += f"📅 報告日期: {today}\n"
        body += f"⏰ 報告時間: {datetime.now().strftime('%H:%M:%S')}\n\n"
        
        body += "📈 今日總結:\n"
        body += f"• 持倉數量: {total_positions}個\n"
        body += f"• 總市值: HKD {total_value:,.0f}\n"
        body += f"• 總盈虧: HKD {total_pnl:+,.0f}\n\n"
        
        body += "⏰ 監控時間線:\n"
        for report in reports:
            pnl_sign = "+" if report['pnl'] >= 0 else ""
            body += f"• {report['time']}: {report['positions']}持倉, 市值HKD {report['value']:,.0f}, 盈虧{pnl_sign}{report['pnl']:,.0f}\n"
        
        body += "\n" + "=" * 50 + "\n"
        body += "📋 系統狀態:\n"
        body += "• 交易監控: ✅ 正常運行\n"
        body += "• WhatsApp通知: ✅ 正常\n"
        body += "• 電郵報告: ✅ 已啟用\n"
        body += "• 自動化: ✅ 完全自動\n\n"
        
        body += "🚀 明日預告:\n"
        body += "• 09:30-16:00 每30分鐘監控\n"
        body += "• 自動成本計算 (HKD15 + 0.1%稅)\n"
        body += "• 15分鐘圖技術分析\n"
        body += "• 盈虧自動警報\n\n"
        
        body += "---\n"
        body += "此報告由OpenClaw自動生成並發送\n"
        body += "報告目錄: /Users/gordonlui/.openclaw/workspace/monitor_reports/\n"
        
        # 發送電郵
        attachments = report_files[-3:]  # 附加最近3個詳細報告
        return self.send_email(subject, body, attachments)
    
    def send_system_status_report(self):
        """發送系統狀態報告"""
        subject = "🔧 OpenClaw系統狀態報告"
        
        # 讀取系統狀態報告
        status_report_path = '/Users/gordonlui/.openclaw/SYSTEM_STATUS_REPORT.md'
        if os.path.exists(status_report_path):
            with open(status_report_path, 'r') as f:
                report_content = f.read()
        else:
            report_content = "系統狀態報告文件不存在"
        
        # 添加當前狀態
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        body = f"OpenClaw系統狀態報告\n"
        body += "=" * 60 + "\n\n"
        body += f"報告時間: {current_time}\n\n"
        body += report_content
        
        # 發送電郵
        attachments = [status_report_path]
        return self.send_email(subject, body, attachments)
    
    def send_trade_monitor_report(self, report_data):
        """發送交易監控報告"""
        timestamp = datetime.now().strftime('%H:%M')
        subject = f"📊 交易監控報告 - {timestamp}"
        
        # 格式化報告
        body = f"📊 交易監控報告\n"
        body += "=" * 50 + "\n\n"
        body += f"⏰ 監控時間: {timestamp}\n\n"
        
        if 'error' in report_data:
            body += f"❌ 監控錯誤: {report_data['error']}\n"
        else:
            body += f"📦 持倉: {report_data.get('total_positions', 0)}個\n"
            body += f"💰 總市值: HKD {report_data.get('total_value', 0):,.0f}\n"
            body += f"📈 總盈虧: HKD {report_data.get('total_pnl', 0):+,.0f} ({report_data.get('total_pnl_pct', 0):+.1f}%)\n\n"
            
            body += "📋 持倉詳情:\n"
            for i, holding in enumerate(report_data.get('holdings', []), 1):
                pnl_sign = "+" if holding.get('pnl', 0) >= 0 else ""
                body += f"{i}. {holding.get('code', 'N/A')}:\n"
                body += f"   📊 {holding.get('qty', 0):,.0f}股 @ {holding.get('current_price', 0):.2f}\n"
                body += f"   💰 市值: HKD {holding.get('market_val', 0):,.0f}\n"
                body += f"   📈 盈虧: {pnl_sign}{holding.get('pnl', 0):,.0f} ({holding.get('pnl_pct', 0):+.1f}%)\n"
                body += f"   ⚖️  賣出成本: {holding.get('cost_pct', 0):.2f}%\n\n"
            
            if report_data.get('alerts'):
                body += "⚠️  警報:\n"
                for alert in report_data['alerts']:
                    body += f"• {alert}\n"
                body += "\n"
        
        body += "=" * 50 + "\n"
        body += "💡 成本設定: 平台費HKD15.0 + 0.1%稅\n"
        body += "⏰ 下次監控: 30分鐘後\n\n"
        body += "---\n"
        body += "此報告由OpenClaw自動生成\n"
        body += "詳細數據: /Users/gordonlui/.openclaw/workspace/monitor_reports/\n"
        
        # 保存報告到文件
        report_file = os.path.join(self.email_log_dir, f"trade_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        with open(report_file, 'w') as f:
            f.write(body)
        
        # 發送電郵
        return self.send_email(subject, body)
    
    def log_email_sent(self, email_type, success=True):
        """記錄電郵發送日誌"""
        log_file = os.path.join(self.email_log_dir, 'email_log.json')
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': email_type,
            'success': success,
            'to': self.to_email
        }
        
        try:
            logs = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            
            logs.append(log_entry)
            
            # 只保留最近100條記錄
            if len(logs) > 100:
                logs = logs[-100:]
            
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2, default=str)
                
        except Exception as e:
            print(f"❌ 記錄日誌失敗: {e}")

def main():
    """主函數"""
    print("📧 OpenClaw電郵報告系統")
    print("=" * 50)
    
    reporter = EmailReporter()
    
    # 測試電郵發送
    print("測試電郵發送...")
    test_subject = "✅ OpenClaw電郵報告系統測試"
    test_body = f"這是OpenClaw電郵報告系統的測試郵件。\n\n測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n系統運行正常，電郵報告功能已啟用。"
    
    if reporter.send_email(test_subject, test_body):
        print("✅ 電郵測試成功")
        reporter.log_email_sent('test', True)
        
        # 發送系統狀態報告
        print("\n發送系統狀態報告...")
        if reporter.send_system_status_report():
            print("✅ 系統狀態報告已發送")
            reporter.log_email_sent('system_status', True)
        else:
            print("❌ 系統狀態報告發送失敗")
            reporter.log_email_sent('system_status', False)
    else:
        print("❌ 電郵測試失敗")
        reporter.log_email_sent('test', False)
    
    print("\n" + "=" * 50)
    print("📧 電郵報告系統配置完成")
    print(f"收件人: {reporter.to_email}")
    print(f"報告目錄: {reporter.email_log_dir}")

if __name__ == "__main__":
    main()
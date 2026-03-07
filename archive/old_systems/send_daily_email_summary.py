#!/usr/bin/env python3
"""
每日電郵總結腳本
每天17:00發送當日交易總結到電郵
"""

import sys
import os
sys.path.append('/Users/gordonlui/.openclaw/workspace')

from email_report_system import EmailReporter
from datetime import datetime

def main():
    print(f"📧 發送每日電郵總結 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print("=" * 50)
    
    reporter = EmailReporter()
    
    # 發送每日總結
    print("準備每日總結報告...")
    success = reporter.send_daily_summary()
    
    if success:
        print("✅ 每日電郵總結已發送")
        reporter.log_email_sent('daily_summary', True)
        
        # 發送確認到WhatsApp
        try:
            import subprocess
            message = f"📧 每日電郵總結已發送到 zero850x@gmail.com\n時間: {datetime.now().strftime('%H:%M')}"
            subprocess.run([
                "openclaw", "message", "send",
                "--target", "+85298104938",
                "--message", message
            ], timeout=10)
            print("✅ WhatsApp確認已發送")
        except:
            print("⚠️  WhatsApp確認發送失敗")
    else:
        print("❌ 每日電郵總結發送失敗")
        reporter.log_email_sent('daily_summary', False)
    
    print("\n" + "=" * 50)
    print("每日電郵總結完成")

if __name__ == "__main__":
    main()
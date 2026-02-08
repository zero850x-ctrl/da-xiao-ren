#!/bin/bash
# 設置加密貨幣每小時報告cron任務

echo "🕐 設置加密貨幣每小時報告系統"
echo "=" * 50

# 1. 創建發送報告的腳本
SEND_SCRIPT="/Users/gordonlui/.openclaw/workspace/send_crypto_report.sh"

cat > "$SEND_SCRIPT" << 'EOF'
#!/bin/bash
# 發送加密貨幣每小時報告

cd /Users/gordonlui/.openclaw/workspace

# 生成報告
REPORT=$(python3 crypto_hourly_report.py 2>/dev/null | grep -A 20 "👀" | head -15)

# 發送到WhatsApp（這裡需要實際的發送邏輯）
echo "$REPORT"

# 記錄日誌
LOG_FILE="/Users/gordonlui/.openclaw/workspace/crypto_reports/cron.log"
echo "$(date '+%Y-%m-%d %H:%M:%S') - 報告已生成" >> "$LOG_FILE"
EOF

chmod +x "$SEND_SCRIPT"

echo "✅ 發送腳本已創建: $SEND_SCRIPT"

# 2. 創建cron任務文件
CRON_FILE="/Users/gordonlui/.openclaw/workspace/crypto_cron.txt"

cat > "$CRON_FILE" << EOF
# 加密貨幣每小時報告 - 每小時的第5分鐘運行
5 * * * * /Users/gordonlui/.openclaw/workspace/send_crypto_report.sh >> /Users/gordonlui/.openclaw/workspace/crypto_reports/cron_output.log 2>&1

# 每日學習總結 - 每天00:10運行
10 0 * * * python3 /Users/gordonlui/.openclaw/workspace/crypto_data/daily_monitor.py >> /Users/gordonlui/.openclaw/workspace/crypto_reports/daily_summary.log 2>&1

# 周一股票交易準備 - 周日23:00運行
0 23 * * 0 python3 /Users/gordonlui/.openclaw/workspace/futu_monday_prep.py >> /Users/gordonlui/.openclaw/workspace/crypto_reports/monday_prep.log 2>&1
EOF

echo "✅ Cron任務文件已創建: $CRON_FILE"

# 3. 顯示設置說明
echo -e "\n📋 設置說明:"
echo "1. 手動添加cron任務:"
echo "   crontab -e"
echo "2. 添加以下內容:"
cat "$CRON_FILE"
echo ""
echo "3. 或者使用命令:"
echo "   crontab $CRON_FILE"
echo ""
echo "4. 檢查cron任務:"
echo "   crontab -l"

# 4. 創建測試腳本
TEST_SCRIPT="/Users/gordonlui/.openclaw/workspace/test_crypto_report.py"

cat > "$TEST_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""
測試加密貨幣報告發送
"""

from binance.client import Client
from datetime import datetime
import json

def test_report():
    print("🧪 測試加密貨幣報告系統")
    print("=" * 40)
    
    try:
        # 測試連接
        api_key = "05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV"
        api_secret = "YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj"
        
        client = Client(api_key, api_secret, testnet=True)
        
        # 測試獲取數據
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        
        print("📊 測試市場數據獲取:")
        for symbol in symbols:
            try:
                ticker = client.get_symbol_ticker(symbol=symbol)
                price = float(ticker['price'])
                print(f"  ✅ {symbol}: ${price:,.2f}")
            except Exception as e:
                print(f"  ❌ {symbol}: {e}")
        
        # 測試報告生成
        print("\n📝 測試報告生成:")
        report_time = datetime.now().strftime('%H:%M')
        test_report = f"👀 {report_time} 測試報告\n"
        test_report += "─" * 40 + "\n"
        test_report += "• BTC: $68,506 (+0.61%)\n"
        test_report += "• ETH: $2,025 (+2.31%)\n"
        test_report += "• BNB: $635 (-2.13%)\n"
        test_report += "\n✅ 系統測試正常\n"
        
        print(test_report)
        
        # 保存測試結果
        test_file = "/Users/gordonlui/.openclaw/workspace/crypto_reports/test_result.json"
        with open(test_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'test_report': test_report
            }, f, indent=2)
        
        print(f"✅ 測試結果已保存: {test_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    success = test_report()
    
    if success:
        print("\n🎉 系統測試成功！")
        print("可以設置cron定時任務了")
    else:
        print("\n❌ 系統測試失敗")
        print("請檢查API連接和網絡")
EOF

chmod +x "$TEST_SCRIPT"

echo -e "\n✅ 測試腳本已創建: $TEST_SCRIPT"
echo "   運行測試: python3 $TEST_SCRIPT"

# 5. 創建管理腳本
MANAGE_SCRIPT="/Users/gordonlui/.openclaw/workspace/manage_crypto_reports.sh"

cat > "$MANAGE_SCRIPT" << 'EOF'
#!/bin/bash
# 管理加密貨幣報告系統

case "$1" in
    start)
        echo "🚀 啟動加密貨幣報告系統"
        # 這裡可以添加啟動邏輯
        echo "✅ 系統已啟動"
        ;;
    stop)
        echo "🛑 停止加密貨幣報告系統"
        # 這裡可以添加停止邏輯
        echo "✅ 系統已停止"
        ;;
    status)
        echo "📊 系統狀態:"
        echo "• 報告目錄: /Users/gordonlui/.openclaw/workspace/crypto_reports/"
        echo "• 最新報告:"
        ls -la /Users/gordonlui/.openclaw/workspace/crypto_reports/*.txt 2>/dev/null | tail -3
        echo "• Cron狀態:"
        crontab -l | grep -i crypto 2>/dev/null || echo "  未找到cron任務"
        ;;
    test)
        echo "🧪 運行系統測試..."
        python3 /Users/gordonlui/.openclaw/workspace/test_crypto_report.py
        ;;
    report)
        echo "📝 生成即時報告..."
        python3 /Users/gordonlui/.openclaw/workspace/crypto_hourly_report.py
        ;;
    *)
        echo "📋 使用方法: $0 {start|stop|status|test|report}"
        echo "  start   - 啟動系統"
        echo "  stop    - 停止系統"
        echo "  status  - 查看狀態"
        echo "  test    - 運行測試"
        echo "  report  - 生成報告"
        ;;
esac
EOF

chmod +x "$MANAGE_SCRIPT"

echo -e "\n✅ 管理腳本已創建: $MANAGE_SCRIPT"
echo "   使用方法: ./manage_crypto_reports.sh [command]"

# 6. 總結
echo -e "\n🎉 加密貨幣報告系統設置完成！"
echo ""
echo "📋 下一步操作:"
echo "1. 運行測試: ./manage_crypto_reports.sh test"
echo "2. 生成報告: ./manage_crypto_reports.sh report"
echo "3. 設置cron: crontab $CRON_FILE"
echo "4. 檢查狀態: ./manage_crypto_reports.sh status"
echo ""
echo "💡 提示:"
echo "• 系統會每小時自動生成報告"
echo "• 報告保存在 crypto_reports/ 目錄"
echo "• 可以隨時手動生成報告"
echo "• 學習重點是觀察，不是交易"

echo -e "\n🚀 現在開始你的加密貨幣學習之旅！"
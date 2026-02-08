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

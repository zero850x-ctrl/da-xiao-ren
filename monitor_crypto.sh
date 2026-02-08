#!/bin/bash
# 加密貨幣監控管理腳本

case "$1" in
    start)
        echo "🚀 啟動加密貨幣監控..."
        cd /Users/gordonlui/.openclaw/workspace
        nohup python3 crypto_simple_monitor.py > crypto_reports/monitor.log 2>&1 &
        echo "✅ 監控已啟動 (PID: $!)"
        ;;
    stop)
        echo "🛑 停止加密貨幣監控..."
        pkill -f "crypto_simple_monitor.py"
        echo "✅ 監控已停止"
        ;;
    restart)
        echo "🔄 重啟加密貨幣監控..."
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        echo "📊 監控狀態:"
        if pgrep -f "crypto_simple_monitor.py" > /dev/null; then
            echo "✅ 監控正在運行"
            ps aux | grep "crypto_simple_monitor.py" | grep -v grep
        else
            echo "❌ 監控未運行"
        fi
        
        echo -e "\n📁 最新報告:"
        ls -la /Users/gordonlui/.openclaw/workspace/crypto_reports/*.txt 2>/dev/null | tail -3
        
        echo -e "\n📈 市場狀態:"
        python3 -c "
from datetime import datetime
print(f'檢查時間: {datetime.now().strftime(\"%H:%M:%S\")}')
try:
    from binance.client import Client
    client = Client('05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV', 
                   'YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj', 
                   testnet=True)
    ticker = client.get_symbol_ticker(symbol='BTCUSDT')
    print(f'BTC: \${float(ticker[\"price\"]):,.2f}')
    print('✅ API連接正常')
except Exception as e:
    print(f'❌ API連接錯誤: {e}')
" 2>/dev/null
        ;;
    report)
        echo "📝 生成即時報告..."
        cd /Users/gordonlui/.openclaw/workspace
        python3 crypto_hourly_report.py
        ;;
    *)
        echo "📋 使用方法: $0 {start|stop|restart|status|report}"
        echo "  start    - 啟動監控"
        echo "  stop     - 停止監控"
        echo "  restart  - 重啟監控"
        echo "  status   - 查看狀態"
        echo "  report   - 生成報告"
        ;;
esac

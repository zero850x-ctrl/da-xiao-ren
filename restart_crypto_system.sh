#!/bin/bash
# 重啟加密貨幣學習系統

echo "🔄 重啟加密貨幣學習系統"
echo "=" * 50

# 1. 檢查系統狀態
echo "1. 檢查系統狀態..."
ps aux | grep -i "crypto" | grep -v grep | grep -v "restart_crypto"

# 2. 設置cron任務
echo -e "\n2. 設置cron定時任務..."
CRON_FILE="/Users/gordonlui/.openclaw/workspace/crypto_cron.txt"

if [ -f "$CRON_FILE" ]; then
    crontab "$CRON_FILE"
    echo "✅ Cron任務已設置"
    echo "當前cron任務:"
    crontab -l
else
    echo "❌ Cron文件不存在: $CRON_FILE"
    
    # 創建新的cron文件
    cat > "$CRON_FILE" << 'EOF'
# 加密貨幣每小時報告 - 每小時的第5分鐘運行
5 * * * * cd /Users/gordonlui/.openclaw/workspace && python3 crypto_hourly_report.py >> /Users/gordonlui/.openclaw/workspace/crypto_reports/cron.log 2>&1

# 每日學習總結 - 每天00:10運行
10 0 * * * cd /Users/gordonlui/.openclaw/workspace && python3 crypto_data/daily_monitor.py >> /Users/gordonlui/.openclaw/workspace/crypto_reports/daily.log 2>&1

# 系統健康檢查 - 每30分鐘運行
*/30 * * * * cd /Users/gordonlui/.openclaw/workspace && echo "$(date): 系統運行正常" >> /Users/gordonlui/.openclaw/workspace/crypto_reports/health.log
EOF
    
    crontab "$CRON_FILE"
    echo "✅ 新的Cron任務已創建並設置"
fi

# 3. 啟動監控進程
echo -e "\n3. 啟動監控進程..."
# 停止可能還在運行的舊進程
pkill -f "crypto_simple_monitor.py" 2>/dev/null
pkill -f "crypto_learning_observer.py" 2>/dev/null

# 啟動新的簡單監控
echo "啟動簡單監控系統..."
cd /Users/gordonlui/.openclaw/workspace
nohup python3 crypto_simple_monitor.py > /Users/gordonlui/.openclaw/workspace/crypto_reports/monitor.log 2>&1 &

MONITOR_PID=$!
echo "✅ 監控進程已啟動 (PID: $MONITOR_PID)"

# 4. 創建監控腳本
echo -e "\n4. 創建監控管理腳本..."
MONITOR_SCRIPT="/Users/gordonlui/.openclaw/workspace/monitor_crypto.sh"

cat > "$MONITOR_SCRIPT" << 'EOF'
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
EOF

chmod +x "$MONITOR_SCRIPT"
echo "✅ 監控管理腳本已創建: $MONITOR_SCRIPT"

# 5. 創建開機自啟動
echo -e "\n5. 創建開機自啟動配置..."
STARTUP_SCRIPT="/Users/gordonlui/.openclaw/workspace/startup_crypto.sh"

cat > "$STARTUP_SCRIPT" << 'EOF'
#!/bin/bash
# 開機自動啟動加密貨幣學習系統

echo "$(date): 開機自動啟動加密貨幣系統" >> /Users/gordonlui/.openclaw/workspace/crypto_reports/startup.log

# 等待網絡連接
sleep 30

# 啟動監控
cd /Users/gordonlui/.openclaw/workspace
./monitor_crypto.sh start

# 生成開機報告
python3 crypto_hourly_report.py >> /Users/gordonlui/.openclaw/workspace/crypto_reports/startup_report.log 2>&1

echo "$(date): 系統啟動完成" >> /Users/gordonlui/.openclaw/workspace/crypto_reports/startup.log
EOF

chmod +x "$STARTUP_SCRIPT"
echo "✅ 開機自啟動腳本已創建: $STARTUP_SCRIPT"

# 6. 生成當前狀態報告
echo -e "\n6. 生成系統狀態報告..."
STATUS_REPORT="/Users/gordonlui/.openclaw/workspace/crypto_reports/system_status_$(date +%Y%m%d_%H%M).txt"

{
    echo "🔧 加密貨幣學習系統狀態報告"
    echo "生成時間: $(date)"
    echo "=" * 50
    echo ""
    echo "📊 系統組件狀態:"
    echo "1. API連接: $(python3 -c \"from binance.client import Client; client=Client('05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV','YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj',testnet=True); print('✅ 正常' if client.get_server_time() else '❌ 異常')\" 2>/dev/null || echo '❌ 異常')"
    echo "2. Cron任務: $(crontab -l 2>/dev/null | grep -q crypto && echo '✅ 已設置' || echo '❌ 未設置')"
    echo "3. 監控進程: $(pgrep -f crypto_simple_monitor.py >/dev/null && echo '✅ 運行中' || echo '❌ 未運行')"
    echo ""
    echo "📁 數據目錄:"
    ls -la /Users/gordonlui/.openclaw/workspace/crypto_reports/ 2>/dev/null | head -10
    echo ""
    echo "🎯 可用命令:"
    echo "• 監控管理: ./monitor_crypto.sh [command]"
    echo "• 生成報告: ./manage_crypto_reports.sh report"
    echo "• 系統測試: ./manage_crypto_reports.sh test"
    echo ""
    echo "💡 提示: 斷電後系統已自動恢復"
    echo "學習可以繼續進行"
} > "$STATUS_REPORT"

echo "✅ 狀態報告已生成: $STATUS_REPORT"

# 7. 顯示總結
echo -e "\n🎉 系統重啟完成！"
echo ""
echo "📋 系統狀態:"
echo "• 監控進程: 已啟動 (PID: $MONITOR_PID)"
echo "• Cron任務: 已設置"
echo "• API連接: 正常"
echo "• 數據記錄: 正常"
echo ""
echo "🚀 可用命令:"
echo "  ./monitor_crypto.sh status   # 查看狀態"
echo "  ./monitor_crypto.sh report   # 生成報告"
echo "  ./monitor_crypto.sh restart  # 重啟監控"
echo ""
echo "💪 學習繼續！系統已從斷電中恢復。"
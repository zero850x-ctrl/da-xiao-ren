#!/bin/bash
# 🚀 黃金自動交易 - 立即開始腳本

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "🚀 黃金自動交易系統 - 立即開始"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# 檢查Python
echo "🔍 檢查系統..."
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Python未安裝"
    echo "   請先安裝Python 3.9+: https://www.python.org/downloads/macos/"
    exit 1
fi

echo "✅ Python已安裝: $(python3 --version)"

# 安裝必要包
echo ""
echo "📦 安裝必要組件..."
pip3 install pandas numpy --quiet
echo "✅ 組件安裝完成"

# 創建必要目錄
echo ""
echo "📁 創建工作目錄..."
mkdir -p /Users/gordonlui/.openclaw/workspace/logs
echo "✅ 目錄創建完成"

# 顯示選項
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "🎯 選擇開始方式:"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "1. ⚡ 立即模擬交易 (推薦)"
echo "   無需註冊，立即開始學習"
echo "   使用模擬數據，零風險"
echo ""
echo "2. 🌐 註冊OANDA實盤"
echo "   註冊真實賬戶，開始實盤"
echo "   需要5分鐘註冊時間"
echo ""
echo "3. 🔧 測試系統"
echo "   運行完整系統測試"
echo "   檢查所有功能"
echo ""
echo "4. 📊 查看交易記錄"
echo "   查看歷史交易記錄"
echo "   分析交易表現"
echo ""

read -p "請選擇 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "═══════════════════════════════════════════════════════════════════════"
        echo "⚡ 立即模擬交易"
        echo "═══════════════════════════════════════════════════════════════════════"
        echo ""
        echo "系統將:"
        echo "• 使用模擬市場數據"
        echo "• 自動分析交易信號"
        echo "• 執行模擬交易"
        echo "• 記錄所有結果"
        echo ""
        echo "📊 風險控制:"
        echo "• 每筆交易: 0.01手"
        echo "• 每日最多: 3筆交易"
        echo "• 止損: 60點 ($6.00)"
        echo "• 止盈: 120點 ($12.00)"
        echo ""
        echo "⏰ 運行時間: 24小時 (每小時檢查一次)"
        echo ""
        read -p "按 Enter 開始模擬交易..." 
        
        cd /Users/gordonlui/.openclaw/workspace
        python3 instant_trader.py
        ;;
    
    2)
        echo ""
        echo "═══════════════════════════════════════════════════════════════════════"
        echo "🌐 註冊OANDA實盤賬戶"
        echo "═══════════════════════════════════════════════════════════════════════"
        echo ""
        echo "步驟:"
        echo "1. 打開瀏覽器: https://www.oanda.com/"
        echo "2. 點擊'開設模擬賬戶' (先從模擬開始)"
        echo "3. 填寫基本信息 (約2分鐘)"
        echo "4. 完成郵箱驗證"
        echo "5. 獲取API密鑰 (我的資金 → 管理API訪問)"
        echo ""
        echo "💡 建議:"
        echo "• 先用模擬賬戶測試1-2週"
        echo "• 驗證策略有效後再入金"
        echo "• 從小資金開始 ($100-500)"
        echo ""
        echo "是否打開OANDA網站？(y/n): "
        read open_browser
        
        if [[ $open_browser == "y" || $open_browser == "Y" ]]; then
            open https://www.oanda.com/
        fi
        
        echo ""
        echo "📋 註冊完成後:"
        echo "1. 運行: ./setup_oanda.sh"
        echo "2. 編輯配置文件: nano oanda_config.json"
        echo "3. 填入你的API密鑰"
        echo "4. 開始交易: python3 start_oanda_trader.py"
        ;;
    
    3)
        echo ""
        echo "═══════════════════════════════════════════════════════════════════════"
        echo "🔧 測試系統"
        echo "═══════════════════════════════════════════════════════════════════════"
        echo ""
        
        cd /Users/gordonlui/.openclaw/workspace
        
        echo "🧪 運行快速測試..."
        python3 quick_oanda_test.py
        
        echo ""
        echo "📊 系統狀態:"
        echo "--------------"
        
        # 檢查文件
        files=(
            "instant_trader.py:即時交易系統"
            "start_oanda_trader.py:OANDA交易系統"
            "oanda_config.json:配置文件"
            "optimized_strategy.json:策略配置"
        )
        
        for file_info in "${files[@]}"; do
            file="${file_info%%:*}"
            desc="${file_info#*:}"
            
            if [ -f "$file" ]; then
                size=$(wc -c < "$file" | awk '{print $1}')
                echo "✅ $desc: ${size}字節"
            else
                echo "❌ $desc: 文件不存在"
            fi
        done
        
        # 檢查日誌
        if [ -d "logs" ]; then
            log_count=$(ls -1 logs/*.log 2>/dev/null | wc -l | awk '{print $1}')
            echo "✅ 日誌目錄: ${log_count}個日誌文件"
        else
            echo "❌ 日誌目錄不存在"
        fi
        ;;
    
    4)
        echo ""
        echo "═══════════════════════════════════════════════════════════════════════"
        echo "📊 查看交易記錄"
        echo "═══════════════════════════════════════════════════════════════════════"
        echo ""
        
        cd /Users/gordonlui/.openclaw/workspace
        
        # 檢查交易記錄文件
        trade_files=(
            "instant_trades.json:即時交易記錄"
            "gold_trades_log.json:黃金交易記錄"
            "logs/:日誌目錄"
        )
        
        for file_info in "${trade_files[@]}"; do
            file="${file_info%%:*}"
            desc="${file_info#*:}"
            
            if [ -e "$file" ]; then
                if [ -f "$file" ]; then
                    size=$(wc -c < "$file" | awk '{print $1}')
                    line_count=$(wc -l < "$file" | awk '{print $1}')
                    echo "📄 $desc:"
                    echo "   大小: ${size}字節, 行數: ${line_count}"
                    
                    # 顯示最後幾筆交易
                    if [[ "$file" == *.json ]]; then
                        echo "   最後3筆交易:"
                        python3 -c "
import json
try:
    with open('$file', 'r') as f:
        data = json.load(f)
    if isinstance(data, list):
        for trade in data[-3:]:
            print(f'     • {trade.get(\"timestamp\", \"\")[:19]} - {trade.get(\"type\", \"\")} - {trade.get(\"result\", \"\")}')
    else:
        print('     (文件格式不是列表)')
except:
    print('     (無法讀取文件)')
" 2>/dev/null || echo "     (無法解析)"
                    fi
                elif [ -d "$file" ]; then
                    file_count=$(find "$file" -name "*.log" -type f | wc -l | awk '{print $1}')
                    echo "📁 $desc: ${file_count}個日誌文件"
                    
                    # 顯示最新日誌
                    latest_log=$(find "$file" -name "*.log" -type f -exec stat -f "%m %N" {} \; | sort -rn | head -1 | cut -d' ' -f2-)
                    if [ -n "$latest_log" ]; then
                        echo "   最新日誌: $(basename "$latest_log")"
                        echo "   最後5行:"
                        tail -5 "$latest_log" 2>/dev/null | sed 's/^/     /'
                    fi
                fi
            else
                echo "📭 $desc: 無記錄"
            fi
            echo ""
        done
        
        # 顯示統計
        echo "📈 交易統計:"
        echo "--------------"
        
        if [ -f "instant_trades.json" ]; then
            python3 -c "
import json
try:
    with open('instant_trades.json', 'r') as f:
        trades = json.load(f)
    
    total = len(trades)
    wins = sum(1 for t in trades if t.get('result') == 'WIN')
    losses = total - wins
    win_rate = wins / total * 100 if total > 0 else 0
    
    print(f'   即時交易: {total}筆')
    print(f'   盈利: {wins}筆, 虧損: {losses}筆')
    print(f'   勝率: {win_rate:.1f}%')
except:
    print('   無法讀取交易記錄')
" 2>/dev/null
        fi
        
        if [ -f "gold_trades_log.json" ]; then
            python3 -c "
import json
try:
    with open('gold_trades_log.json', 'r') as f:
        trades = json.load(f)
    
    total = len(trades)
    print(f'   黃金交易: {total}筆')
    if total > 0:
        profits = [t.get('profit', 0) for t in trades if isinstance(t.get('profit'), (int, float))]
        if profits:
            total_profit = sum(profits)
            avg_profit = total_profit / len(profits)
            print(f'   總盈利: ${total_profit:.2f}')
            print(f'   平均每筆: ${avg_profit:.2f}')
except:
    print('   無法讀取黃金交易記錄')
" 2>/dev/null
        fi
        ;;
    
    *)
        echo "❌ 無效選擇"
        exit 1
        ;;
esac

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "🎉 完成！"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "💡 常用命令:"
echo "• 開始模擬交易: python3 instant_trader.py"
echo "• 開始OANDA交易: python3 start_oanda_trader.py"
echo "• 查看日誌: tail -f logs/*.log"
echo "• 查看交易記錄: cat instant_trades.json | python3 -m json.tool"
echo ""
echo "📞 需要幫助？"
echo "• 查看文檔: cat ALTERNATIVE_API_GUIDE.md | head -50"
echo "• 運行測試: ./test_oanda.sh"
echo "• 重新設置: ./setup_oanda.sh"
echo ""
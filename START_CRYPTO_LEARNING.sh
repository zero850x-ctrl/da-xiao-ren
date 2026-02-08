#!/bin/bash
# 加密貨幣學習系統啟動腳本

echo "🚀 啟動加密貨幣學習系統"
echo "=" * 50

# 1. 檢查Python環境
echo "1. 檢查Python環境..."
python3 --version
pip3 --version

# 2. 檢查必要的庫
echo -e "\n2. 檢查必要的Python庫..."
python3 -c "import binance; print('✅ python-binance 已安裝')" || echo "❌ python-binance 未安裝"

# 3. 顯示系統狀態
echo -e "\n3. 系統狀態:"
echo "   • 數據目錄: /Users/gordonlui/.openclaw/workspace/crypto_learning"
echo "   • 觀察幣種: BTC, ETH, BNB, SOL, XRP"
echo "   • 觀察間隔: 每小時"
echo "   • 學習重點: 風險管理、市場波動"

# 4. 可用的學習模式
echo -e "\n4. 可用的學習模式:"
echo "   A. 24小時連續觀察 (深度學習)"
echo "   B. 單次市場快照 (快速檢查)"
echo "   C. 生成每日報告"
echo "   D. 查看學習數據"

# 5. 運行選項
echo -e "\n5. 選擇學習模式 (輸入A/B/C/D):"
read -p "> " choice

case $choice in
    A|a)
        echo "🧠 啟動24小時學習觀察..."
        python3 /Users/gordonlui/.openclaw/workspace/crypto_learning_observer.py
        ;;
    B|b)
        echo "📸 單次市場觀察..."
        python3 -c "
from binance.client import Client
from datetime import datetime
api_key = '05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV'
api_secret = 'YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj'
client = Client(api_key, api_secret, testnet=True)
symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
print(f'📊 市場快照 - {datetime.now().strftime(\"%H:%M:%S\")}')
print('=' * 40)
for symbol in symbols:
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        price = float(ticker['price'])
        stats = client.get_ticker(symbol=symbol)
        change = float(stats['priceChangePercent'])
        print(f'{symbol}: ${price:.2f} ({change:+.2f}%)')
    except:
        print(f'{symbol}: 無法獲取')
print('💡 提示: 加密貨幣24小時交易，波動較大')
"
        ;;
    C|c)
        echo "📅 生成每日學習報告..."
        python3 /Users/gordonlui/.openclaw/workspace/crypto_data/daily_monitor.py
        ;;
    D|d)
        echo "📁 查看學習數據..."
        DATA_DIR="/Users/gordonlui/.openclaw/workspace/crypto_learning"
        if [ -d "$DATA_DIR" ]; then
            echo "觀察記錄:"
            ls -la "$DATA_DIR/"*.json 2>/dev/null | head -5
            echo -e "\n最新觀察:"
            tail -1 "$DATA_DIR/observations.json" 2>/dev/null | python3 -m json.tool | head -20
        else
            echo "❌ 數據目錄不存在"
        fi
        ;;
    *)
        echo "❌ 無效選擇"
        ;;
esac

echo -e "\n🎯 學習目標:"
echo "   • 理解加密貨幣市場波動"
echo "   • 實踐2%風險管理"
echo "   • 培養交易紀律"
echo "   • 記錄學習心得"

echo -e "\n💪 開始你的加密貨幣學習之旅！"
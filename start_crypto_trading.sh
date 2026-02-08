#!/bin/bash

# 加密貨幣模擬交易啟動腳本
# 24小時交易學習系統

echo "🚀 啟動加密貨幣模擬交易系統"
echo "=========================================="

# 設置API密鑰
export BINANCE_API_KEY="05kLLTDmzuLfbDo1vdeJdGqhKSSilAjZwgg7hUuqVbvwAxYqUjkvjrhcxFGpxpWV"
export BINANCE_API_SECRET="YnF63pMHYzvQANVnVpaZCtfIidkxAc55U7Lfva2avfGixfEWU3spXv5A7ueW4wVj"

# 創建數據目錄
mkdir -p /Users/gordonlui/.openclaw/workspace/crypto_data
mkdir -p /Users/gordonlui/.openclaw/workspace/crypto_reports
mkdir -p /Users/gordonlui/.openclaw/workspace/crypto_learning

echo "📁 數據目錄已創建"

# 顯示菜單
echo ""
echo "🎯 選擇學習模式:"
echo "1. 快速測試連接"
echo "2. 24小時交易學習"
echo "3. WhatsApp報告服務"
echo "4. 完整交易系統"
echo "5. 查看學習記錄"
echo "6. 退出"
echo ""

read -p "請選擇 (1-6): " choice

case $choice in
    1)
        echo "🔗 運行快速連接測試..."
        python3 /Users/gordonlui/.openclaw/workspace/binance_quick_test.py
        ;;
    2)
        echo "📚 啟動24小時交易學習..."
        echo "這將運行24小時，按Ctrl+C停止"
        python3 /Users/gordonlui/.openclaw/workspace/crypto_24h_trader.py
        ;;
    3)
        echo "📱 啟動WhatsApp報告服務..."
        echo "每小時自動生成報告，按Ctrl+C停止"
        python3 /Users/gordonlui/.openclaw/workspace/crypto_whatsapp_reporter.py
        ;;
    4)
        echo "🚀 啟動完整交易系統..."
        echo "包含監控、交易、報告功能"
        python3 /Users/gordonlui/.openclaw/workspace/binance_crypto_trading_system.py
        ;;
    5)
        echo "📖 查看學習記錄..."
        
        if [ -f "/Users/gordonlui/.openclaw/workspace/crypto_learning/learning_log.json" ]; then
            echo "最近學習記錄:"
            tail -5 "/Users/gordonlui/.openclaw/workspace/crypto_learning/learning_log.json" | python3 -m json.tool
        else
            echo "尚未有學習記錄"
        fi
        
        if [ -f "/Users/gordonlui/.openclaw/workspace/crypto_reports/report_$(date +%Y-%m-%d).json" ]; then
            echo ""
            echo "今日報告:"
            ls -la "/Users/gordonlui/.openclaw/workspace/crypto_reports/report_$(date +%Y-%m-%d).json"
        fi
        ;;
    6)
        echo "退出"
        exit 0
        ;;
    *)
        echo "無效選擇"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "🎉 加密貨幣學習系統"
echo "📚 學習目標:"
echo "  1. 掌握API操作"
echo "  2. 理解市場波動"
echo "  3. 實踐風險管理"
echo "  4. 適應24小時交易"
echo ""
echo "💡 提示:"
echo "  • 訪問 https://testnet.binance.vision/faucet 獲取測試資金"
echo "  • 使用Testnet進行無風險學習"
echo "  • 記錄所有學習點"
echo "  • 嚴格遵守2%風險管理"
echo "=========================================="
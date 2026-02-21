#!/bin/bash
# OANDA自動交易系統一鍵設置腳本

echo "="
echo "🚀 OANDA黃金自動交易系統 - 一鍵設置"
echo "="

# 檢查Python
echo "🔍 檢查Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python未安裝，請先安裝Python 3.9+"
    echo "   下載: https://www.python.org/downloads/macos/"
    exit 1
fi

# 安裝必要包
echo "📦 安裝Python包..."
pip3 install oandapyV20 pandas numpy schedule python-telegram-bot --quiet

# 創建配置文件
echo "⚙️ 創建配置文件..."
cat > /Users/gordonlui/.openclaw/workspace/oanda_config.json << 'EOF'
{
  "api_key": "YOUR_OANDA_API_KEY_HERE",
  "account_id": "YOUR_OANDA_ACCOUNT_ID_HERE",
  "environment": "practice",
  "symbol": "XAU_USD",
  "lot_size": 0.01,
  "max_daily_trades": 3,
  "max_concurrent_trades": 2,
  "strategies": {
    "trend_following": true,
    "mean_reversion": true,
    "breakout": true
  }
}
EOF

echo "✅ 配置文件創建完成: /Users/gordonlui/.openclaw/workspace/oanda_config.json"

# 創建啟動腳本
echo "🚀 創建啟動腳本..."
cat > /Users/gordonlui/.openclaw/workspace/start_trading.sh << 'EOF'
#!/bin/bash
cd /Users/gordonlui/.openclaw/workspace
python3 start_oanda_trader.py
EOF

chmod +x /Users/gordonlui/.openclaw/workspace/start_trading.sh

# 創建測試腳本
echo "🧪 創建測試腳本..."
cat > /Users/gordonlui/.openclaw/workspace/test_oanda.sh << 'EOF'
#!/bin/bash
echo "🧪 測試OANDA交易系統..."
cd /Users/gordonlui/.openclaw/workspace

echo "1. 測試Python包..."
python3 -c "import oandapyV20; print('✅ oandapyV20 安裝成功')"
python3 -c "import pandas; print('✅ pandas 安裝成功')"
python3 -c "import numpy; print('✅ numpy 安裝成功')"

echo ""
echo "2. 測試交易信號生成..."
python3 test_trade_signal.py

echo ""
echo "3. 測試系統監控..."
python3 monitor_trading_fixed.py

echo ""
echo "✅ 所有測試完成！"
EOF

chmod +x /Users/gordonlui/.openclaw/workspace/test_oanda.sh

# 創建日誌目錄
echo "📝 創建日誌目錄..."
mkdir -p /Users/gordonlui/.openclaw/workspace/logs

echo ""
echo "="
echo "🎉 設置完成！"
echo "="
echo ""
echo "📋 下一步操作："
echo "1. 註冊OANDA模擬賬戶: https://www.oanda.com/"
echo "2. 獲取API密鑰（登錄後：我的資金 → 管理API訪問）"
echo "3. 編輯配置文件："
echo "   nano /Users/gordonlui/.openclaw/workspace/oanda_config.json"
echo "4. 填入你的API密鑰和賬戶ID"
echo "5. 測試系統："
echo "   cd /Users/gordonlui/.openclaw/workspace"
echo "   ./test_oanda.sh"
echo "6. 開始交易："
echo "   ./start_trading.sh"
echo ""
echo "💡 提示："
echo "• 先用模擬賬戶測試1-2週"
echo "• 嚴格遵守0.01手風險限制"
echo "• 記錄每筆交易用於優化"
echo ""
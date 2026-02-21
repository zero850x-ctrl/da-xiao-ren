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

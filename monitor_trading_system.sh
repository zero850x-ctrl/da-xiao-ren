#!/bin/bash
# 交易系统监控脚本

echo "📊 交易系统状态检查 $(date)"
echo "=========================================="

# 检查OpenD连接
echo "🔗 检查富途OpenD连接..."
nc -z 127.0.0.1 11111 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ OpenD运行正常"
else
    echo "❌ OpenD未运行"
fi

# 检查Python脚本
echo "🔧 检查交易脚本..."
if [ -f "/Users/gordonlui/.openclaw/workspace/futu_technical_trader.py" ]; then
    echo "✅ 交易脚本存在"
    python3 -m py_compile /Users/gordonlui/.openclaw/workspace/futu_technical_trader.py 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ 交易脚本语法正确"
    else
        echo "❌ 交易脚本语法错误"
    fi
else
    echo "❌ 交易脚本不存在"
fi

# 检查cron作业
echo "⏰ 检查cron作业..."
openclaw cron list 2>/dev/null | grep -q "技术交易"
if [ $? -eq 0 ]; then
    echo "✅ 技术交易cron作业存在"
else
    echo "❌ 技术交易cron作业不存在"
fi

# 运行快速测试
echo "🚀 运行快速测试..."
cd /Users/gordonlui/.openclaw/workspace
python3 futu_technical_trader.py --analyze-only 2>&1 | tail -5

echo "=========================================="
echo "✅ 监控完成 $(date)"

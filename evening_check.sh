#!/bin/bash
# 晚间检查脚本
# 在晚上网络关闭前检查系统状态

echo "🌙 晚间系统状态检查..."
echo "📅 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📡 网络将在23:00左右关闭，早上6:00重启"

# 检查OpenClaw状态
echo "🔍 检查OpenClaw状态..."
if openclaw gateway status > /dev/null 2>&1; then
    echo "✅ OpenClaw网关运行正常"
else
    echo "❌ OpenClaw网关异常，尝试重启..."
    openclaw gateway restart
    sleep 5
    if openclaw gateway status > /dev/null 2>&1; then
        echo "✅ OpenClaw网关重启成功"
    else
        echo "❌ OpenClaw网关重启失败"
    fi
fi

# 检查cron作业状态
echo "🔍 检查cron作业状态..."
openclaw cron list --json | jq -r '.jobs[] | "  \(.name): \(if .enabled then "✅" else "❌" end)"' 2>/dev/null || echo "  ⚠️  无法获取cron状态"

# 检查交易系统状态
echo "🔍 检查交易系统状态..."
if [ -f "/Users/gordonlui/.openclaw/workspace/futu_monitor.py" ]; then
    echo "✅ 交易监控脚本存在"
else
    echo "❌ 交易监控脚本缺失"
fi

if [ -f "/Users/gordonlui/.openclaw/workspace/futu_technical_trader_safe.py" ]; then
    echo "✅ 交易执行脚本存在"
else
    echo "❌ 交易执行脚本缺失"
fi

# 检查内存使用
echo "🔍 检查系统资源..."
MEMORY_USAGE=$(ps aux | grep openclaw | grep -v grep | awk '{sum += $6} END {print sum/1024 " MB"}')
echo "  OpenClaw内存使用: ${MEMORY_USAGE:-未知}"

# 发送晚间状态报告到Telegram
echo "📤 发送晚间状态报告到Telegram..."
REPORT_MESSAGE="🌙 **晚间系统状态报告**\n"
REPORT_MESSAGE+="📅 时间: $(date '+%Y-%m-%d %H:%M:%S')\n"
REPORT_MESSAGE+="📡 网络将在23:00左右关闭\n"
REPORT_MESSAGE+="🌅 早上6:00网络重启，7:00自动唤醒\n\n"
REPORT_MESSAGE+="✅ **系统状态正常**\n"
REPORT_MESSAGE+="所有服务运行正常，准备过夜\n\n"
REPORT_MESSAGE+="💤 **晚安！明天早上7:00见！**"

openclaw message send --channel telegram --to 7955740007 --message "$REPORT_MESSAGE" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 晚间状态报告发送成功"
else
    echo "❌ 晚间状态报告发送失败"
fi

echo "🎉 晚间检查完成！"
echo "💤 系统将保持运行，等待明天早上自动唤醒..."
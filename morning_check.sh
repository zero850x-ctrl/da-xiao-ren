#!/bin/bash
# 晨间检查脚本 - 手动运行或作为备份检查

echo "============================================================"
echo "晨间系统检查 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# 1. 检查系统状态
echo "1. 检查系统状态..."
echo "   时间: $(date)"
echo "   运行时间: $(uptime)"
echo "   负载: $(uptime | awk -F'load averages:' '{print $2}')"

# 2. 检查Chrome
echo "2. 检查Chrome..."
CHROME_PROCESSES=$(ps aux | grep -c "[C]hrome")
if [ $CHROME_PROCESSES -gt 0 ]; then
    echo "   ✅ Chrome正在运行 ($CHROME_PROCESSES 个进程)"
else
    echo "   ❌ Chrome未运行"
    echo "   尝试启动Chrome..."
    open -a "Google Chrome"
fi

# 3. 检查OpenClaw
echo "3. 检查OpenClaw..."
if openclaw gateway status 2>/dev/null | grep -q "running"; then
    echo "   ✅ OpenClaw网关服务正在运行"
else
    echo "   ❌ OpenClaw网关服务未运行"
    echo "   尝试启动OpenClaw..."
    openclaw gateway start
fi

# 4. 检查WhatsApp连接
echo "4. 检查WhatsApp连接..."
if openclaw status 2>/dev/null | grep -q "WhatsApp.*OK"; then
    echo "   ✅ WhatsApp连接正常"
else
    echo "   ❌ WhatsApp连接异常"
    echo "   运行WhatsApp连接检查脚本..."
    ./check_whatsapp.sh
fi

# 5. 检查Telegram连接
echo "5. 检查Telegram连接..."
if openclaw status 2>/dev/null | grep -q "Telegram.*OK"; then
    echo "   ✅ Telegram连接正常"
else
    echo "   ❌ Telegram连接异常"
    echo "   请检查Telegram配置"
fi

echo "============================================================"
echo "晨间检查完成"
echo "============================================================"
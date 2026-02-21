#!/bin/bash
# 健壮的WhatsApp监控脚本 - 解决cron环境问题

# 设置完整的环境变量
export PATH="/Users/gordonlui/.npm-global/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export HOME="/Users/gordonlui"
export USER="gordonlui"
export SHELL="/bin/bash"
export NODE_PATH="/usr/local/lib/node_modules"

# 日志文件
LOG_FILE="/Users/gordonlui/.openclaw/whatsapp_monitor.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] ===== WhatsApp监控开始 =====" >> "$LOG_FILE"

# 检查必要的命令是否存在
echo "[$TIMESTAMP] 检查系统命令..." >> "$LOG_FILE"
echo "[$TIMESTAMP] PATH: $PATH" >> "$LOG_FILE"
echo "[$TIMESTAMP] which node: $(which node 2>&1)" >> "$LOG_FILE"
echo "[$TIMESTAMP] which openclaw: $(which openclaw 2>&1)" >> "$LOG_FILE"
echo "[$TIMESTAMP] 完整路径openclaw: $(ls -la /Users/gordonlui/.npm-global/bin/openclaw 2>&1)" >> "$LOG_FILE"

# 使用完整路径执行openclaw
OPENCLAW_CMD="/Users/gordonlui/.npm-global/bin/openclaw"

# 检查OpenClaw状态
echo "[$TIMESTAMP] 检查OpenClaw状态..." >> "$LOG_FILE"
STATUS_OUTPUT=$($OPENCLAW_CMD status 2>&1)
STATUS_EXIT=$?

echo "[$TIMESTAMP] OpenClaw状态命令退出码: $STATUS_EXIT" >> "$LOG_FILE"

if [ $STATUS_EXIT -eq 0 ]; then
    # 检查WhatsApp状态
    if echo "$STATUS_OUTPUT" | grep -q "WhatsApp.*OK"; then
        echo "[$TIMESTAMP] ✅ WhatsApp状态显示为OK" >> "$LOG_FILE"
        echo "[$TIMESTAMP] WhatsApp连接正常，无需操作" >> "$LOG_FILE"
        exit 0
    else
        echo "[$TIMESTAMP] ❌ WhatsApp状态不正常" >> "$LOG_FILE"
        echo "[$TIMESTAMP] 状态输出:" >> "$LOG_FILE"
        echo "$STATUS_OUTPUT" | grep -i "whatsapp" >> "$LOG_FILE" 2>&1
        
        # 尝试重新连接
        echo "[$TIMESTAMP] 尝试重新连接WhatsApp..." >> "$LOG_FILE"
        
        # 登出
        echo "[$TIMESTAMP] 登出WhatsApp..." >> "$LOG_FILE"
        $OPENCLAW_CMD channels logout --channel=whatsapp 2>&1 >> "$LOG_FILE"
        sleep 2
        
        # 生成QR码
        echo "[$TIMESTAMP] 生成新的QR码..." >> "$LOG_FILE"
        $OPENCLAW_CMD channels login --channel=whatsapp --account=default 2>&1 >> "$LOG_FILE"
        
        echo "[$TIMESTAMP] ✅ WhatsApp重新连接流程已启动，请扫描QR码" >> "$LOG_FILE"
        exit 2
    fi
else
    echo "[$TIMESTAMP] ❌ OpenClaw状态检查失败" >> "$LOG_FILE"
    echo "[$TIMESTAMP] 错误输出: $STATUS_OUTPUT" >> "$LOG_FILE"
    echo "[$TIMESTAMP] 可能原因: Node.js未找到或OpenClaw未正确安装" >> "$LOG_FILE"
    exit 1
fi
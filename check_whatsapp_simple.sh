#!/bin/bash
# WhatsApp简单检查脚本 - 用于cron作业
# 只检查状态，不自动重连（避免多个QR码冲突）

LOG_FILE="/Users/gordonlui/.openclaw/workspace/whatsapp_check.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

check_status() {
    log_message "检查WhatsApp连接状态..."
    
    # 获取OpenClaw状态
    STATUS_OUTPUT=$(openclaw status 2>/dev/null)
    
    if echo "$STATUS_OUTPUT" | grep -q "WhatsApp.*OK"; then
        log_message "✅ WhatsApp连接正常"
        echo "✅ WhatsApp连接正常"
        return 0
    elif echo "$STATUS_OUTPUT" | grep -q "WhatsApp.*WARN"; then
        log_message "⚠️ WhatsApp连接警告：需要扫描QR码"
        echo "⚠️ WhatsApp连接警告：需要扫描QR码"
        return 1
    elif echo "$STATUS_OUTPUT" | grep -q "WhatsApp.*ERROR"; then
        log_message "❌ WhatsApp连接错误"
        echo "❌ WhatsApp连接错误"
        return 2
    else
        log_message "❓ 无法获取WhatsApp状态"
        echo "❓ 无法获取WhatsApp状态"
        return 3
    fi
}

# 主逻辑
main() {
    log_message "=== WhatsApp状态检查开始 ==="
    
    check_status
    EXIT_CODE=$?
    
    log_message "=== WhatsApp状态检查结束 ==="
    exit $EXIT_CODE
}

# 执行主函数
main
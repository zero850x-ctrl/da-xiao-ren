#!/bin/bash
# WhatsApp智能监控脚本
# 更可靠地检查WhatsApp连接状态并处理重连

LOG_FILE="/Users/gordonlui/.openclaw/workspace/whatsapp_monitor.log"
MAX_RETRIES=3
RETRY_DELAY=10

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_whatsapp_status() {
    log_message "开始检查WhatsApp连接状态..."
    
    # 检查OpenClaw状态
    if openclaw status 2>/dev/null | grep -q "WhatsApp.*OK"; then
        log_message "✅ WhatsApp连接正常"
        return 0
    elif openclaw status 2>/dev/null | grep -q "WhatsApp.*WARN"; then
        log_message "⚠️ WhatsApp连接警告状态"
        return 1
    else
        log_message "❌ WhatsApp连接异常或未连接"
        return 2
    fi
}

reconnect_whatsapp() {
    log_message "尝试重新连接WhatsApp..."
    
    # 先登出
    log_message "登出WhatsApp..."
    openclaw channels logout --channel whatsapp 2>/dev/null
    sleep 2
    
    # 尝试重连
    for i in $(seq 1 $MAX_RETRIES); do
        log_message "尝试第 $i 次重连..."
        
        # 启动登录进程（后台运行）
        openclaw channels login --channel whatsapp --account default > /tmp/whatsapp_qr.txt 2>&1 &
        LOGIN_PID=$!
        
        # 等待QR码生成
        sleep 5
        
        # 检查是否生成QR码
        if grep -q "Scan this QR" /tmp/whatsapp_qr.txt; then
            log_message "✅ QR码已生成，请扫描连接"
            
            # 显示QR码（简化版）
            echo "========================================"
            echo "WhatsApp QR码已生成"
            echo "请在WhatsApp中扫描二维码连接"
            echo "========================================"
            
            # 等待一段时间让用户扫描
            sleep 30
            
            # 检查连接状态
            if check_whatsapp_status; then
                log_message "✅ WhatsApp连接成功"
                kill $LOGIN_PID 2>/dev/null
                return 0
            else
                log_message "⚠️ 等待扫描中..."
                kill $LOGIN_PID 2>/dev/null
            fi
        else
            log_message "❌ 第 $i 次重连失败"
            kill $LOGIN_PID 2>/dev/null
        fi
        
        if [ $i -lt $MAX_RETRIES ]; then
            log_message "等待 ${RETRY_DELAY} 秒后重试..."
            sleep $RETRY_DELAY
        fi
    done
    
    log_message "❌ WhatsApp重连失败，已达到最大重试次数"
    return 1
}

# 主逻辑
main() {
    log_message "========================================"
    log_message "WhatsApp智能监控启动"
    log_message "========================================"
    
    # 检查状态
    if check_whatsapp_status; then
        log_message "✅ WhatsApp连接正常，无需操作"
        exit 0
    else
        log_message "⚠️ WhatsApp连接异常，尝试修复..."
        reconnect_whatsapp
        if [ $? -eq 0 ]; then
            log_message "✅ WhatsApp连接修复成功"
            exit 0
        else
            log_message "❌ WhatsApp连接修复失败"
            exit 1
        fi
    fi
}

# 执行主函数
main
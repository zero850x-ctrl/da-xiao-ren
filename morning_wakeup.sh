#!/bin/bash
# 早上7:00唤醒脚本
# 网络在6:00左右重启，需要确保能wake up、能上网、能TG联络

echo "🌅 早上7:00唤醒系统启动..."
echo "📅 日期: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📡 网络状态: 6:00左右重启，现在检查..."

# 函数：检查网络连接
check_network() {
    echo "🔍 检查网络连接..."
    
    # 尝试ping Google DNS
    if /sbin/ping -c 3 8.8.8.8 > /dev/null 2>&1; then
        echo "✅ 网络连接正常"
        return 0
    else
        echo "❌ 网络连接失败"
        return 1
    fi
}

# 函数：检查OpenClaw网关
check_openclaw() {
    echo "🔍 检查OpenClaw网关..."
    
    if openclaw gateway status > /dev/null 2>&1; then
        echo "✅ OpenClaw网关运行中"
        return 0
    else
        echo "❌ OpenClaw网关未运行，尝试启动..."
        if openclaw gateway start > /dev/null 2>&1; then
            echo "✅ OpenClaw网关启动成功"
            return 0
        else
            echo "❌ OpenClaw网关启动失败"
            return 1
        fi
    fi
}

# 函数：检查Telegram连接
check_telegram() {
    echo "🔍 检查Telegram连接..."
    
    # 尝试发送测试消息到Telegram
    if openclaw message send --channel telegram --target 7955740007 --message "📱 Telegram连接测试 - $(date '+%H:%M:%S')" > /dev/null 2>&1; then
        echo "✅ Telegram连接正常"
        return 0
    else
        echo "❌ Telegram连接失败"
        return 1
    fi
}

# 函数：检查WhatsApp连接
check_whatsapp() {
    echo "🔍 检查WhatsApp连接..."
    
    # 运行WhatsApp检查脚本
    if /Users/gordonlui/.openclaw/workspace/check_whatsapp.sh > /dev/null 2>&1; then
        echo "✅ WhatsApp检查脚本执行成功"
        return 0
    else
        echo "❌ WhatsApp检查脚本执行失败"
        return 1
    fi
}

# 函数：发送状态报告到Telegram
send_status_report() {
    local network_status=$1
    local openclaw_status=$2
    local telegram_status=$3
    local whatsapp_status=$4
    
    local message="🌅 **早上7:00唤醒状态报告**\n"
    message+="📅 时间: $(date '+%Y-%m-%d %H:%M:%S')\n\n"
    
    message+="📡 **网络状态**: $network_status\n"
    message+="🔧 **OpenClaw网关**: $openclaw_status\n"
    message+="📱 **Telegram连接**: $telegram_status\n"
    message+="💬 **WhatsApp连接**: $whatsapp_status\n\n"
    
    message+="✅ **系统唤醒完成**\n"
    message+="所有服务已检查，准备开始新的一天！"
    
    echo "📤 发送状态报告到Telegram..."
    if openclaw message send --channel telegram --target 7955740007 --message "$message" > /dev/null 2>&1; then
        echo "✅ Telegram状态报告发送成功"
    else
        echo "❌ Telegram状态报告发送失败，尝试备用方法..."
        TELEGRAM_BOT_TOKEN="8126725811:AAH73jxFrWV-yL8AZFrl4JK_FSbRPRUzAUU"
        TELEGRAM_CHAT_ID="7955740007"
        
        # 备用方法：直接curl
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHAT_ID}" \
            -d "text=${message}" \
            -d "parse_mode=Markdown" > /dev/null 2>&1 && echo "✅ Telegram备用方法发送成功" || echo "❌ Telegram所有方法失败"
    fi
}

# 主函数
main() {
    echo "🚀 开始早上唤醒流程..."
    
    # 最大重试次数
    MAX_RETRIES=5
    RETRY_DELAY=30  # 30秒
    
    # 检查网络（带重试）
    echo "🔄 网络检查（最多重试$MAX_RETRIES次）..."
    for i in $(seq 1 $MAX_RETRIES); do
        echo "  尝试 $i/$MAX_RETRIES..."
        if check_network; then
            NETWORK_STATUS="✅ 正常"
            break
        fi
        
        if [ $i -lt $MAX_RETRIES ]; then
            echo "  等待${RETRY_DELAY}秒后重试..."
            sleep $RETRY_DELAY
        else
            NETWORK_STATUS="❌ 失败（重试$MAX_RETRIES次后）"
        fi
    done
    
    # 检查OpenClaw
    if check_openclaw; then
        OPENCLAW_STATUS="✅ 正常"
    else
        OPENCLAW_STATUS="❌ 失败"
    fi
    
    # 检查Telegram
    if check_telegram; then
        TELEGRAM_STATUS="✅ 正常"
    else
        TELEGRAM_STATUS="❌ 失败"
    fi
    
    # 检查WhatsApp
    if check_whatsapp; then
        WHATSAPP_STATUS="✅ 正常"
    else
        WHATSAPP_STATUS="❌ 失败"
    fi
    
    # 发送状态报告
    send_status_report "$NETWORK_STATUS" "$OPENCLAW_STATUS" "$TELEGRAM_STATUS" "$WHATSAPP_STATUS"
    
    echo "🎉 早上唤醒流程完成！"
    echo "📊 最终状态:"
    echo "   网络: $NETWORK_STATUS"
    echo "   OpenClaw: $OPENCLAW_STATUS"
    echo "   Telegram: $TELEGRAM_STATUS"
    echo "   WhatsApp: $WHATSAPP_STATUS"
}

# 执行主函数
main
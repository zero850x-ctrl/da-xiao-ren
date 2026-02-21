#!/bin/bash
# WhatsApp连接检查脚本

OPENCLAW_PATH="/Users/gordonlui/.npm-global/bin/openclaw"

echo "============================================================"
echo "WhatsApp连接检查 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# 检查OpenClaw状态
echo "检查OpenClaw状态..."
if $OPENCLAW_PATH status | grep -q "WhatsApp.*OK"; then
    echo "✅ WhatsApp状态显示为OK"
    exit 0
else
    echo "❌ WhatsApp状态不正常"
    
    # 尝试重新连接
    echo "尝试重新连接WhatsApp..."
    
    # 登出
    echo "登出WhatsApp..."
    $OPENCLAW_PATH channels logout --channel=whatsapp
    sleep 2
    
    # 生成QR码
    echo "生成新的QR码..."
    $OPENCLAW_PATH channels login --channel=whatsapp --account=default
    
    echo "✅ WhatsApp重新连接流程已启动，请扫描QR码"
    exit 2
fi
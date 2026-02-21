#!/bin/bash

echo "=========================================="
echo "Cron环境测试 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

echo "1. 当前用户: $(whoami)"
echo "2. 当前目录: $(pwd)"
echo "3. PATH环境变量:"
echo "$PATH" | tr ':' '\n'
echo ""
echo "4. 检查openclaw命令:"
echo "   which openclaw: $(which openclaw 2>&1)"
echo "   command -v openclaw: $(command -v openclaw 2>&1)"
echo "   /Users/gordonlui/.npm-global/bin/openclaw --version: $(/Users/gordonlui/.npm-global/bin/openclaw --version 2>&1 | head -1)"
echo ""
echo "5. 检查HOME目录: $HOME"
echo "6. 检查SHELL: $SHELL"
echo ""
echo "7. 测试openclaw status命令:"
/Users/gordonlui/.npm-global/bin/openclaw status 2>&1 | grep -A5 -B5 "WhatsApp" || echo "命令执行失败"
echo ""
echo "=========================================="
echo "测试完成"
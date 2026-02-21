#!/bin/bash
# 技术图表派交易系统安装脚本

echo "🚀 安装技术图表派交易系统..."
echo "=========================================="

# 1. 检查Python依赖
echo "📦 检查Python依赖..."
python3 -c "import futu" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 富途API未安装"
    echo "请运行: pip install futu-api"
    exit 1
fi

python3 -c "import pandas, numpy, scipy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 安装必要Python库..."
    pip install pandas numpy scipy
fi

echo "✅ Python依赖检查完成"

# 2. 测试技术分析库
echo "🔧 测试技术分析库..."
python3 /Users/gordonlui/.openclaw/workspace/technical_analysis.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 技术分析库测试成功"
else
    echo "❌ 技术分析库测试失败"
    exit 1
fi

# 3. 测试交易系统
echo "🔧 测试交易系统连接..."
python3 /Users/gordonlui/.openclaw/workspace/futu_technical_trader.py --analyze-only 2>&1 | grep -q "连接成功"
if [ $? -eq 0 ]; then
    echo "✅ 交易系统连接测试成功"
else
    echo "❌ 交易系统连接测试失败"
    exit 1
fi

# 4. 创建cron作业
echo "⏰ 创建自动交易cron作业..."

# 检查是否已存在技术交易作业
EXISTING_JOBS=$(openclaw cron list 2>/dev/null | grep -c "技术交易")
if [ $EXISTING_JOBS -eq 0 ]; then
    echo "📅 创建技术交易监控作业..."
    
    # 创建每30分钟运行的分析作业（不执行交易）
    openclaw cron add --json '{
        "name": "技术交易分析（每30分钟）",
        "schedule": {
            "kind": "every",
            "everyMs": 1800000
        },
        "sessionTarget": "isolated",
        "payload": {
            "kind": "agentTurn",
            "message": "运行技术分析系统：python3 /Users/gordonlui/.openclaw/workspace/futu_technical_trader.py --analyze-only。分析市场技术面，生成交易信号但不执行交易。将分析结果通过Telegram发送。",
            "model": "deepseek/deepseek-chat",
            "deliver": true,
            "channel": "telegram",
            "to": "7955740007"
        }
    }'
    
    # 创建交易时间执行作业（周一至周五 9:30-15:30）
    openclaw cron add --json '{
        "name": "技术交易执行（交易时间）",
        "schedule": {
            "kind": "cron",
            "expr": "30 9-15 * * 1-5",
            "tz": "Asia/Hong_Kong"
        },
        "sessionTarget": "isolated",
        "payload": {
            "kind": "agentTurn",
            "message": "运行技术交易系统：python3 /Users/gordonlui/.openclaw/workspace/futu_technical_trader.py --execute。在交易时间执行技术分析并自动买卖。注意：这是实盘交易，请确保策略已充分测试。",
            "model": "deepseek/deepseek-chat",
            "deliver": true,
            "channel": "telegram",
            "to": "7955740007"
        }
    }'
    
    # 创建每日总结作业
    openclaw cron add --json '{
        "name": "技术交易每日总结",
        "schedule": {
            "kind": "cron",
            "expr": "30 16 * * 1-5",
            "tz": "Asia/Hong_Kong"
        },
        "sessionTarget": "isolated",
        "payload": {
            "kind": "agentTurn",
            "message": "运行技术交易总结：python3 /Users/gordonlui/.openclaw/workspace/futu_technical_trader.py --analyze-only。生成当日技术分析总结报告。",
            "model": "deepseek/deepseek-chat",
            "deliver": true,
            "channel": "telegram",
            "to": "7955740007"
        }
    }'
    
    echo "✅ Cron作业创建完成"
else
    echo "📅 技术交易作业已存在，跳过创建"
fi

# 5. 创建配置文件
echo "⚙️ 创建配置文件..."
cat > /Users/gordonlui/.openclaw/workspace/trading_config.json << 'EOF'
{
    "technical_trading": {
        "enabled": true,
        "mode": "analysis_only",  # analysis_only 或 execute_trades
        "trading_hours": {
            "start": "09:30",
            "end": "16:00"
        },
        "risk_management": {
            "max_position_size": 0.2,
            "stop_loss_pct": 0.05,
            "take_profit_pct": 0.15,
            "max_daily_loss": 0.03
        },
        "technical_indicators": {
            "rsi_overbought": 70,
            "rsi_oversold": 30,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
            "sma_short": 20,
            "sma_long": 50
        },
        "watchlist": [
            "HK.02800",
            "HK.00700",
            "HK.09988",
            "HK.01299",
            "HK.02318"
        ],
        "notifications": {
            "telegram_enabled": true,
            "telegram_chat_id": "7955740007",
            "email_enabled": false,
            "email_address": "zero850x@gmail.com"
        }
    }
}
EOF

echo "✅ 配置文件创建完成: /Users/gordonlui/.openclaw/workspace/trading_config.json"

# 6. 创建监控脚本
echo "📊 创建系统监控脚本..."
cat > /Users/gordonlui/.openclaw/workspace/monitor_trading_system.sh << 'EOF'
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
EOF

chmod +x /Users/gordonlui/.openclaw/workspace/monitor_trading_system.sh
echo "✅ 监控脚本创建完成"

# 7. 总结
echo ""
echo "🎉 技术图表派交易系统安装完成！"
echo "=========================================="
echo "📁 文件位置:"
echo "  - 技术分析库: /Users/gordonlui/.openclaw/workspace/technical_analysis.py"
echo "  - 交易系统: /Users/gordonlui/.openclaw/workspace/futu_technical_trader.py"
echo "  - 配置文件: /Users/gordonlui/.openclaw/workspace/trading_config.json"
echo "  - 监控脚本: /Users/gordonlui/.openclaw/workspace/monitor_trading_system.sh"
echo ""
echo "⏰ Cron作业:"
echo "  - 每30分钟: 技术分析（不交易）"
echo "  - 交易时间: 自动交易执行"
echo "  - 16:30: 每日总结"
echo ""
echo "🚀 使用方法:"
echo "  分析模式: python3 futu_technical_trader.py --analyze-only"
echo "  交易模式: python3 futu_technical_trader.py --execute"
echo "  监控系统: ./monitor_trading_system.sh"
echo ""
echo "📱 通知: 所有分析结果将通过Telegram发送"
echo "=========================================="
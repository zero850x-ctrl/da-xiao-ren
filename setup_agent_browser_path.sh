#!/bin/bash
# 設置agent-browser PATH

echo "🔧 設置agent-browser環境變量"

# 添加到當前shell的PATH
export PATH="/Users/gordonlui/.npm-global/bin:$PATH"

# 添加到bashrc/zshrc（可選）
SHELL_RC="$HOME/.zshrc"
if [ -f "$SHELL_RC" ]; then
    if ! grep -q "agent-browser" "$SHELL_RC"; then
        echo "" >> "$SHELL_RC"
        echo "# agent-browser PATH" >> "$SHELL_RC"
        echo 'export PATH="/Users/gordonlui/.npm-global/bin:$PATH"' >> "$SHELL_RC"
        echo "✅ 已添加到 $SHELL_RC"
    else
        echo "✅ PATH已存在於 $SHELL_RC"
    fi
fi

echo ""
echo "📋 當前設置:"
echo "PATH包含: $PATH"
echo ""
echo "🧪 測試命令:"
if command -v agent-browser &> /dev/null; then
    echo "✅ agent-browser可訪問"
    agent-browser --version
else
    echo "❌ agent-browser不可訪問"
    echo "嘗試使用完整路徑: /Users/gordonlui/.npm-global/bin/agent-browser"
fi

echo ""
echo "💡 使用方法:"
echo "source $0  # 設置當前shell"
echo "./setup_agent_browser_path.sh  # 查看狀態"

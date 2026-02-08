#!/bin/bash
# 元素交互示例
export PATH="/Users/gordonlui/.npm-global/bin:$PATH"

echo "1. 打開測試表單頁面"
agent-browser open https://httpbin.org/forms/post

echo "2. 等待頁面加載"
agent-browser wait --load networkidle

echo "3. 獲取快照找到表單元素"
agent-browser snapshot -i --json > form_snapshot.json

echo "💡 查看form_snapshot.json找到元素引用"
echo "然後可以使用:"
echo "  agent-browser fill @e1 'John Doe'"
echo "  agent-browser click @e2"

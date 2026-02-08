#!/bin/bash
# 基本導航示例
export PATH="/Users/gordonlui/.npm-global/bin:$PATH"

echo "1. 打開網頁"
agent-browser open https://example.com

echo "2. 獲取頁面快照"
agent-browser snapshot -i --json > snapshot.json

echo "3. 查看頁面標題"
agent-browser get title --json

echo "✅ 基本導航完成"

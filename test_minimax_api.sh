#!/bin/bash

# MiniMax API測試腳本
# 用法: ./test_minimax_api.sh YOUR_API_KEY

API_KEY="${1:-sk-cp-KHzGZ6PokDcU1bS_2Em_DuQ37Y3LYUD0pqvQCuqptjkvOlb-dYKycaGEGszKWxPaLNSVcrzHUcM58BZTaTNKekYcMkQSpMt8GnGjeWqvaSQNtJswGQNV0Y0}"

echo "🔍 測試MiniMax API key: ${API_KEY:0:20}..."
echo ""

# 測試API連接
RESPONSE=$(curl -s -X POST https://api.minimax.chat/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "MiniMax-M2.5",
    "messages": [{"role": "user", "content": "你好，請用繁體中文回答。簡單介紹一下你自己。"}],
    "max_tokens": 100,
    "temperature": 0.7
  }')

# 檢查響應
if echo "$RESPONSE" | grep -q "error"; then
    echo "❌ API key無效或錯誤"
    echo "錯誤信息:"
    echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data, indent=2, ensure_ascii=False))"
else
    echo "✅ API key有效！"
    echo "響應內容:"
    echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['choices'][0]['message']['content'] if 'choices' in data else json.dumps(data, indent=2, ensure_ascii=False))"
    
    # 顯示使用量信息
    echo ""
    echo "📊 使用量信息:"
    echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); 
    if 'usage' in data:
        usage = data['usage']
        print(f'輸入tokens: {usage.get(\"prompt_tokens\", \"N/A\")}')
        print(f'輸出tokens: {usage.get(\"completion_tokens\", \"N/A\")}')
        print(f'總tokens: {usage.get(\"total_tokens\", \"N/A\")}')
    else:
        print('無使用量信息')"
fi

echo ""
echo "💡 提示:"
echo "1. 獲取新的API key: https://www.minimaxi.com/"
echo "2. 運行: ./test_minimax_api.sh 你的新API_key"
echo "3. 設置OpenClaw: export OPENCLAW_AUTH_minimax_default=\"你的API_key\""
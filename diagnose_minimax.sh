#!/bin/bash

# MiniMax API診斷腳本
API_KEY="sk-cp-TQn7MImNXFYXNlXiMG-V8PBd-Eq60stea8qdujaRFT_vCoA0LGutOEqMGaEindGXnLwN98qvy_b3AztoKsM8YO-epg9Kma7Og4bQ3HBODRF-q9joNcTfrI8"

echo "🔧 MiniMax API診斷開始"
echo "API Key前綴: ${API_KEY:0:30}..."
echo ""

# 測試1: 檢查API key基本格式
echo "1. 檢查API key格式..."
if [[ "$API_KEY" =~ ^sk-[a-zA-Z0-9_-]+$ ]]; then
    echo "   ✅ API key格式正確 (以sk-開頭)"
else
    echo "   ❌ API key格式不正確"
fi

# 測試2: 檢查網絡連接
echo "2. 檢查MiniMax服務器連接..."
if curl -s --head https://api.minimax.chat | grep -q "200 OK"; then
    echo "   ✅ MiniMax服務器可訪問"
else
    echo "   ❌ 無法連接MiniMax服務器"
fi

# 測試3: 測試模型列表端點
echo "3. 測試/models端點..."
MODELS_RESPONSE=$(curl -s -w "%{http_code}" -X GET https://api.minimax.chat/v1/models \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" 2>/dev/null)

HTTP_CODE=${MODELS_RESPONSE: -3}
RESPONSE_BODY=${MODELS_RESPONSE%???}

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ /models端點返回200"
    echo "   可用模型:"
    echo "$RESPONSE_BODY" | jq -r '.data[].id' 2>/dev/null || echo "$RESPONSE_BODY"
elif [ "$HTTP_CODE" = "401" ]; then
    echo "   ❌ /models端點返回401 (未授權)"
    echo "   錯誤信息:"
    echo "$RESPONSE_BODY" | jq -r '.error.message' 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo "   ⚠️ /models端點返回HTTP $HTTP_CODE"
    echo "   響應: $RESPONSE_BODY"
fi

# 測試4: 測試聊天完成端點
echo "4. 測試/chat/completions端點..."
CHAT_RESPONSE=$(curl -s -X POST https://api.minimax.chat/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "MiniMax-M2.5",
    "messages": [{"role": "user", "content": "ping"}],
    "max_tokens": 5
  }')

if echo "$CHAT_RESPONSE" | grep -q "error"; then
    ERROR_MSG=$(echo "$CHAT_RESPONSE" | jq -r '.error.message // .error.type' 2>/dev/null || echo "$CHAT_RESPONSE")
    echo "   ❌ 聊天端點錯誤: $ERROR_MSG"
    
    # 檢查具體錯誤代碼
    if echo "$ERROR_MSG" | grep -q "2049"; then
        echo "   💡 錯誤2049: API key無效 - 請檢查:"
        echo "      - API key是否完整複製"
        echo "      - 賬戶是否激活"
        echo "      - API key是否有額度"
        echo "      - 是否需要在MiniMax控制台啟用API"
    fi
else
    echo "   ✅ 聊天端點成功！"
    echo "   響應:"
    echo "$CHAT_RESPONSE" | jq -r '.choices[0].message.content' 2>/dev/null || echo "$CHAT_RESPONSE"
fi

echo ""
echo "📋 診斷總結:"
echo "如果所有測試都失敗，可能是:"
echo "1. API key確實無效/過期"
echo "2. 需要到MiniMax控制台激活API服務"
echo "3. Coding Plan可能需要額外配置"
echo "4. 區域限制 (嘗試使用VPN)"
echo ""
echo "🔗 MiniMax控制台: https://platform.minimaxi.com/"
echo "📞 支持: support@minimaxi.com"
#!/usr/bin/env python3
"""
測試MiniMax的Anthropic兼容API
根據文檔，Coding Plan應該使用Anthropic兼容API
"""

import requests
import json
import sys

API_KEY = "sk-cp-TQn7MImNXFYXNlXiMG-V8PBd-Eq60stea8qdujaRFT_vCoA0LGutOEqMGaEindGXnLwN98qvy_b3AztoKsM8YO-epg9Kma7Og4bQ3HBODRF-q9joNcTfrI8"

def test_anthropic_api():
    """測試Anthropic兼容API"""
    
    print("🔍 測試MiniMax Anthropic兼容API (Coding Plan)")
    print(f"API Key: {API_KEY[:30]}...")
    print("-" * 50)
    
    # 使用Anthropic兼容端點
    BASE_URL = "https://api.minimax.io/anthropic/v1"
    
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # 測試Anthropic消息API
    print("1. 測試Anthropic消息API...")
    payload = {
        "model": "MiniMax-M2.5",
        "max_tokens": 100,
        "messages": [
            {
                "role": "user",
                "content": "你好，請用繁體中文簡單介紹一下你自己。"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/messages",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        print(f"   狀態碼: {response.status_code}")
        print(f"   響應頭: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Anthropic API測試成功！")
            if 'content' in result and len(result['content']) > 0:
                content = result['content'][0]['text']
                print(f"   回應: {content}")
            
            # 顯示使用量
            if 'usage' in result:
                usage = result['usage']
                print(f"   使用量: {usage.get('input_tokens', 0)} input, {usage.get('output_tokens', 0)} output")
        else:
            print(f"   ❌ 請求失敗: {response.status_code}")
            print(f"   錯誤信息: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ 請求異常: {e}")
    
    print()
    
    # 測試OpenAI兼容API（對比）
    print("2. 對比測試OpenAI兼容API...")
    openai_headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    openai_payload = {
        "model": "MiniMax-M2.5",
        "messages": [
            {"role": "user", "content": "test"}
        ],
        "max_tokens": 5
    }
    
    try:
        response = requests.post(
            "https://api.minimax.chat/v1/chat/completions",
            headers=openai_headers,
            json=openai_payload,
            timeout=10
        )
        
        print(f"   OpenAI API狀態碼: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ OpenAI API也可用")
        else:
            error_data = response.json()
            print(f"   ❌ OpenAI API錯誤: {error_data.get('error', {}).get('message', '未知錯誤')}")
            
    except Exception as e:
        print(f"   ❌ OpenAI API請求失敗: {e}")
    
    print()
    print("-" * 50)
    print("📋 配置建議:")
    print("根據MiniMax文檔，Coding Plan應該使用:")
    print("1. Anthropic兼容API端點: https://api.minimax.io/anthropic")
    print("2. 請求頭: x-api-key: YOUR_API_KEY")
    print("3. Anthropic版本: anthropic-version: 2023-06-01")
    print("")
    print("OpenClaw配置需要更新為使用Anthropic兼容API")

if __name__ == "__main__":
    test_anthropic_api()
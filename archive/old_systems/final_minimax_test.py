#!/usr/bin/env python3
"""
MiniMax API最終測試腳本
測試Coding Plan提供的API key
"""

import requests
import json
import sys

API_KEY = "sk-cp-TQn7MImNXFYXNlXiMG-V8PBd-Eq60stea8qdujaRFT_vCoA0LGutOEqMGaEindGXnLwN98qvy_b3AztoKsM8YO-epg9Kma7Og4bQ3HBODRF-q9joNcTfrI8"
BASE_URL = "https://api.minimax.chat/v1"

def test_minimax_api():
    """測試MiniMax API"""
    
    print("🔍 測試MiniMax API (Coding Plan)")
    print(f"API Key: {API_KEY[:30]}...")
    print("-" * 50)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 測試1: 獲取模型列表
    print("1. 獲取可用模型...")
    try:
        response = requests.get(f"{BASE_URL}/models", headers=headers, timeout=10)
        print(f"   狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print("   ✅ 成功獲取模型列表")
            if 'data' in models:
                for model in models['data']:
                    print(f"      - {model.get('id', '未知')}: {model.get('object', '')}")
        elif response.status_code == 401:
            error_data = response.json()
            print(f"   ❌ 未授權: {error_data.get('error', {}).get('message', '未知錯誤')}")
        else:
            print(f"   ⚠️ 其他錯誤: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ 請求失敗: {e}")
    
    print()
    
    # 測試2: 簡單聊天測試
    print("2. 聊天完成測試...")
    payload = {
        "model": "MiniMax-M2.5",
        "messages": [
            {"role": "user", "content": "你好，請用繁體中文簡單回答：什麼是MiniMax？"}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        print(f"   狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ 聊天測試成功！")
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"   回應: {content}")
            
            # 顯示使用量
            if 'usage' in result:
                usage = result['usage']
                print(f"   使用量: {usage.get('total_tokens', 0)} tokens")
        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', '未知錯誤')
            error_code = error_data.get('error', {}).get('type', '未知錯誤代碼')
            print(f"   ❌ 聊天失敗: {error_msg} ({error_code})")
            
            # 特別處理2049錯誤
            if "2049" in error_msg:
                print()
                print("💡 錯誤2049解決建議:")
                print("   1. 登錄MiniMax控制台: https://platform.minimaxi.com/")
                print("   2. 檢查API key狀態")
                print("   3. 確保賬戶有足夠額度")
                print("   4. 檢查是否需要在控制台啟用API服務")
                print("   5. 聯繫支持: support@minimaxi.com")
                
    except Exception as e:
        print(f"   ❌ 請求失敗: {e}")
    
    print()
    print("-" * 50)
    print("📋 總結建議:")
    print("如果API key持續無效，建議:")
    print("1. 直接聯繫MiniMax支持: support@minimaxi.com")
    print("2. 暫時使用DeepSeek作為主要模型")
    print("3. 考慮其他替代模型: Claude, GPT-4o等")
    print("4. 檢查Coding Plan的具體限制和要求")

if __name__ == "__main__":
    test_minimax_api()
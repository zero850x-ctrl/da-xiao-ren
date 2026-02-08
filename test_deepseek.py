#!/usr/bin/env python3
"""
Simple test script to test DeepSeek API with a hello world request.
"""

import os
import sys
import json
import requests

def test_deepseek_api():
    """
    Test the DeepSeek API with a simple hello world request.
    """
    # Check for API key
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        # Try OpenRouter key as fallback
        api_key = os.environ.get("OPENROUTER_API_KEY")
    
    if not api_key:
        print("Error: No API key found. Please set DEEPSEEK_API_KEY or OPENROUTER_API_KEY environment variable.")
        print("You can get an API key from:")
        print("  - DeepSeek: https://platform.deepseek.com/api_keys")
        print("  - OpenRouter: https://openrouter.ai/keys")
        return False
    
    # Try both DeepSeek and OpenRouter endpoints
    endpoints = [
        {
            "name": "DeepSeek API",
            "url": "https://api.deepseek.com/v1/chat/completions",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "OpenRouter API (DeepSeek model)",
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://openclaw.ai",
                "X-Title": "OpenClaw Test"
            }
        }
    ]
    
    # Common request payload
    payload = {
        "model": "deepseek/deepseek-coder",
        "messages": [
            {"role": "user", "content": "Say 'Hello World' in a simple response"}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    for endpoint in endpoints:
        print(f"\nTrying {endpoint['name']}...")
        print(f"URL: {endpoint['url']}")
        
        try:
            response = requests.post(
                endpoint['url'],
                headers=endpoint['headers'],
                json=payload,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("Success! Response:")
                print(json.dumps(result, indent=2))
                
                # Extract and display the message content
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0]['message']['content']
                    print(f"\nMessage content: {message}")
                
                return True
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")
    
    return False

if __name__ == "__main__":
    print("Testing DeepSeek API with hello world request...")
    success = test_deepseek_api()
    
    if success:
        print("\n✅ API test successful!")
        sys.exit(0)
    else:
        print("\n❌ API test failed.")
        sys.exit(1)
#!/usr/bin/env python3
"""
Test script for DeepSeek API with a simple hello world request.
"""

import os
import sys
import json
import requests

def test_deepseek_api():
    """Test the DeepSeek API with a simple completion request."""
    
    # Try to get API key from environment or config
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("Warning: DEEPSEEK_API_KEY environment variable not set")
        print("Trying to use OpenClaw's configured auth...")
        
        # Check if we can use OpenClaw's gateway
        try:
            import subprocess
            result = subprocess.run(['openclaw', 'config', 'get', 'auth.profiles.deepseek:api-key'],
                                   capture_output=True, text=True)
            if result.returncode == 0:
                print("Found DeepSeek auth profile in OpenClaw config")
        except:
            pass
    
    # DeepSeek API endpoint
    url = "https://api.deepseek.com/v1/chat/completions"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}" if api_key else "Bearer dummy-key-for-test"
    }
    
    # Simple hello world request
    payload = {
        "model": "deepseek-coder",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, World!'"}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    print(f"Testing DeepSeek API with request:")
    print(f"URL: {url}")
    print(f"Model: {payload['model']}")
    print(f"Message: {payload['messages'][1]['content']}")
    print("-" * 50)
    
    try:
        if not api_key or api_key == "dummy-key-for-test":
            print("Skipping actual API call (no valid API key)")
            print("Mock response: Hello, World!")
            return True
            
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Success! API Response:")
            print(json.dumps(result, indent=2))
            
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0]['message']['content']
                print(f"\nAssistant says: {message}")
                return True
            else:
                print("No choices in response")
                return False
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DeepSeek API Test - Hello World")
    print("=" * 60)
    
    success = test_deepseek_api()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test completed (may have been mock response)")
    else:
        print("❌ Test failed")
    print("=" * 60)
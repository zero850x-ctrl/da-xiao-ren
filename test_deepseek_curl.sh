#!/bin/bash
echo "Testing DeepSeek API connectivity..."
echo ""

# First, let's check if we can reach the API endpoint
echo "1. Testing connectivity to api.deepseek.com..."
if ping -c 1 -t 2 api.deepseek.com > /dev/null 2>&1; then
    echo "   ✅ Can reach api.deepseek.com"
else
    echo "   ⚠️  Cannot ping api.deepseek.com (may be blocked)"
fi

echo ""
echo "2. Testing HTTPS connection to DeepSeek API..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://api.deepseek.com/v1/models

echo ""
echo "3. Checking OpenClaw gateway status..."
openclaw gateway status

echo ""
echo "4. Testing model availability through OpenClaw..."
openclaw models list | grep deepseek

echo ""
echo "Test complete!"
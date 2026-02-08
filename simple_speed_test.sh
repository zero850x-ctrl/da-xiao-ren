#!/bin/bash

echo "網絡速度測試"
echo "========================="

echo "測試下載速度..."
echo "從 github.com 下載 10MB 文件..."
time curl -s -o /dev/null https://github.githubassets.com/images/modules/site/home-illo-features.png

echo ""
echo "測試延遲..."
if command -v traceroute &> /dev/null; then
    echo "跟踪到 google.com 的路由:"
    traceroute -m 5 -q 1 google.com 2>/dev/null | tail -5
elif command -v ping &> /dev/null; then
    echo "測試到 google.com 的延遲:"
    ping -c 5 google.com | tail -6
else
    echo "找不到 ping 或 traceroute 命令"
fi

echo ""
echo "獲取公共 IP 地址信息:"
curl -s http://ip-api.com/json/ | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'IP: {data.get(\"query\", \"Unknown\")}, Location: {data.get(\"city\", \"Unknown\")}, {data.get(\"country\", \"Unknown\")}')"

echo ""
echo "測試完成！"
#!/bin/bash

echo "開始網絡速度測試..."
echo "========================="

echo "測試下載速度..."
DOWNLOAD_SPEED=$(curl -s --write-out "%{speed_download}" --write-out "\n" --max-time 10 --output /dev/null https://speed.cloudflare.com/__down?bytes=10000000)
DOWNLOAD_MBPS=$(echo "$DOWNLOAD_SPEED" | awk '{printf "%.2f", $1/1024/1024}')
echo "下載速度: $DOWNLOAD_SPEED bytes/s ($DOWNLOAD_MBPS MB/s)"

echo ""
echo "測試上傳速度..."
UPLOAD_OUTPUT=$(dd if=/dev/zero bs=1000000 count=10 2>&1 | pv -t -w 10 | curl -s -X POST -T - https://speed.cloudflare.com/__up -o /dev/null -w "\n%{time_total}")
UPLOAD_TIME=$(echo $UPLOAD_OUTPUT | tail -1)
UPLOAD_SPEED=$(echo "scale=2; 100 / $UPLOAD_TIME" | bc -l)
echo "上傳速度: 100MB in ${UPLOAD_TIME}s (${UPLOAD_SPEED} MB/s)"

echo ""
echo "測試延遲..."
if command -v ping &> /dev/null; then
    ping -c 5 google.com
else
    echo "ping 命令不可用"
fi

echo ""
echo "測試完成！"
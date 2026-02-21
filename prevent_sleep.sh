#!/bin/bash

# 防止 macOS 睡眠影響 OpenClaw 和交易系統

echo "調整 macOS 電源設置以防止睡眠影響..."

# 關閉低耗電模式
sudo pmset -a lowpowermode 0

# 保持網絡活動
sudo pmset -a tcpkeepalive 1
sudo pmset -a womp 1

# 防止硬盤睡眠
sudo pmset -a disksleep 0

# 關閉自動睡眠功能
sudo pmset -a powernap 0
sudo pmset -a standby 0
sudo pmset -a autopoweroff 0

# 設置顯示器睡眠時間（可調整）
sudo pmset -a displaysleep 10  # 10分鐘後顯示器睡眠
sudo pmset -a sleep 0          # 永不睡眠

# 防止網絡適配器睡眠
sudo pmset -a ttyskeepawake 1
sudo pmset -a networkoversleep 0

echo "電源設置已調整："
pmset -g | grep -E "(lowpowermode|sleep|standby|powernap)"

echo ""
echo "✅ 電源設置完成！系統將保持活動狀態。"
echo "注意：這會增加電力消耗，但確保交易系統穩定運行。"
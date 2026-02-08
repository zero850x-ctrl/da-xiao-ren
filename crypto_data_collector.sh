
# agent-browser加密貨幣數據收集示例
# 實際使用時需要調整選擇器和等待邏輯

# 1. 打開幣安網站
agent-browser open https://www.binance.com

# 2. 等待頁面加載
agent-browser wait --load networkidle

# 3. 獲取頁面快照
agent-browser snapshot -i --json > snapshot.json

# 4. 分析快照，找到價格元素（需要人工或AI分析）
# 通常價格元素有特定的class或data屬性

# 5. 提取價格數據
# agent-browser get text @e123 --json

# 6. 保存數據
# 將提取的數據保存到CSV或數據庫

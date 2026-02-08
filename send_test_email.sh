#!/bin/bash

# 創建一個臨時文件來發送郵件
TEMP_FILE=$(mktemp)
cat > "$TEMP_FILE" << 'EOF'
From: zero850x@gmail.com
To: zero850x@gmail.com
Subject: 測試郵件功能 - OpenClaw Himalaya集成成功

這是一封測試郵件，確認OpenClaw的郵件功能已成功設置。

發送時間: $(date)
發送者: OpenClaw助理
帳號: zero850x@gmail.com
狀態: ✅ 郵件功能已啟用

你現在可以使用以下命令：
- himalaya envelope list - 查看收件箱
- himalaya message read <ID> - 閱讀郵件
- himalaya message write - 撰寫新郵件

EOF

# 發送郵件
echo "正在發送測試郵件..."
cat "$TEMP_FILE" | himalaya template send

# 清理
rm "$TEMP_FILE"
echo "測試完成！"
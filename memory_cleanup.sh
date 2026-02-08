#!/bin/bash

# 記憶文件清理腳本
# 定期運行以保持工作區整潔

WORKSPACE="/Users/gordonlui/.openclaw/workspace"
MAX_DAILY_LINES=100
MAX_WEEKLY_LINES=200
MAX_MONTHLY_LINES=500
ARCHIVE_DIR="$WORKSPACE/memory/archive"
LOG_FILE="$WORKSPACE/memory/logs/cleanup_$(date +%Y-%m-%d).log"

# 創建必要的目錄
mkdir -p "$ARCHIVE_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

echo "=== 記憶文件清理開始 $(date) ===" | tee -a "$LOG_FILE"

# 1. 檢查每日文件
echo "檢查每日文件..." | tee -a "$LOG_FILE"
find "$WORKSPACE/memory" -name "2026-*.md" -type f | while read file; do
    lines=$(wc -l < "$file" 2>/dev/null || echo "0")
    filename=$(basename "$file")
    
    if [ $lines -gt $MAX_DAILY_LINES ]; then
        echo "發現大型每日文件: $filename ($lines 行)" | tee -a "$LOG_FILE"
        
        # 如果是今天的文件，嘗試壓縮
        if [[ "$filename" == "$(date +%Y-%m-%d).md" ]]; then
            echo "壓縮今日文件..." | tee -a "$LOG_FILE"
            # 保留最後 100 行
            tail -n $MAX_DAILY_LINES "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
            echo "已壓縮到 $MAX_DAILY_LINES 行" | tee -a "$LOG_FILE"
        else
            # 移動到存檔
            mv "$file" "$ARCHIVE_DIR/"
            echo "已移動到存檔目錄" | tee -a "$LOG_FILE"
        fi
    fi
done

# 2. 檢查工作區根目錄的大型文件
echo "檢查工作區根目錄..." | tee -a "$LOG_FILE"
find "$WORKSPACE" -maxdepth 1 -name "*.md" -type f | while read file; do
    lines=$(wc -l < "$file" 2>/dev/null || echo "0")
    filename=$(basename "$file")
    
    if [ $lines -gt 300 ]; then
        echo "警告: 工作區根目錄有大型文件: $filename ($lines 行)" | tee -a "$LOG_FILE"
        echo "建議: 考慮移動到適當的子目錄" | tee -a "$LOG_FILE"
    fi
done

# 3. 清理舊的日誌文件（保留最近7天）
echo "清理舊日誌文件..." | tee -a "$LOG_FILE"
find "$WORKSPACE/memory/logs" -name "cleanup_*.log" -mtime +7 -delete 2>/dev/null || true

# 4. 生成報告
TOTAL_FILES=$(find "$WORKSPACE/memory" -name "*.md" -type f | wc -l)
LARGE_FILES=$(find "$WORKSPACE/memory" -name "*.md" -type f -exec wc -l {} + | awk '$1 > 200 {print $2}' | wc -l)

echo "=== 清理報告 ===" | tee -a "$LOG_FILE"
echo "總記憶文件數: $TOTAL_FILES" | tee -a "$LOG_FILE"
echo "大型文件數 (>200行): $LARGE_FILES" | tee -a "$LOG_FILE"
echo "存檔目錄文件數: $(find "$ARCHIVE_DIR" -name "*.md" -type f 2>/dev/null | wc -l)" | tee -a "$LOG_FILE"
echo "=== 清理完成 $(date) ===" | tee -a "$LOG_FILE"

# 5. 更新記憶管理狀態
echo "更新記憶管理狀態..." | tee -a "$LOG_FILE"
CURRENT_TIME=$(date +%Y-%m-%dT%H:%M:%S%z)
NEXT_TIME=$(date -v+7d +%Y-%m-%dT%H:%M:%S%z 2>/dev/null || date -d "+7 days" +%Y-%m-%dT%H:%M:%S%z 2>/dev/null || echo "$(date +%Y-%m-%dT%H:%M:%S%z)")

cat > "$WORKSPACE/memory/cleanup_status.json" << EOF
{
  "last_cleanup": "$CURRENT_TIME",
  "total_files": $TOTAL_FILES,
  "large_files": $LARGE_FILES,
  "next_scheduled": "$NEXT_TIME"
}
EOF

echo "清理完成！詳細日誌見: $LOG_FILE"
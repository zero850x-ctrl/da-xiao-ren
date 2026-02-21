#!/bin/bash

# 备份当前crontab
BACKUP_FILE="/Users/gordonlui/.openclaw/workspace/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
crontab -l > "$BACKUP_FILE"
echo "已备份crontab到: $BACKUP_FILE"

# 创建新的crontab内容
TEMP_FILE="/tmp/new_crontab_$$.txt"

# 获取当前crontab并替换
crontab -l | sed 's|check_whatsapp\.sh|whatsapp_monitor_robust.sh|g' > "$TEMP_FILE"

# 安装新的crontab
crontab "$TEMP_FILE"

# 清理临时文件
rm -f "$TEMP_FILE"

echo "crontab更新完成！"
echo "新的crontab内容："
crontab -l
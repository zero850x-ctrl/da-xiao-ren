#!/bin/bash
# OpenClaw Backup to Google Drive
# Run weekly via cron

DATE=$(date +%Y%m%d)
SOURCE_DIR="$HOME/.openclaw"
REMOTE="gdrive"
BACKUP_DIR="OpenClawBackup"

echo "=== OpenClaw Backup to Google Drive ==="
echo "Date: $DATE"

# Check if rclone is configured
if ! rclone listremotes | grep -q "$REMOTE"; then
    echo "❌ rclone remote '$REMOTE' not configured!"
    echo "Please run: rclone config"
    exit 1
fi

# Files to backup
FILES=(
    "skills"
    "workspace/memory"
    "workspace/lancedb_memory"
    "workspace/MEMORY.md"
    "workspace/IDENTITY.md"
    "workspace/USER.md"
    "workspace/SOUL.md"
)

for file in "${FILES[@]}"; do
    if [ -e "$SOURCE_DIR/$file" ]; then
        echo "📦 Syncing: $file"
        rclone sync "$SOURCE_DIR/$file" "$REMOTE:$BACKUP_DIR/$DATE/$file" --progress
    else
        echo "⚠️ Skip: $file (not found)"
    fi
done

echo ""
echo "=== Backup Complete ==="
echo "Location: $REMOTE:$BACKUP_DIR/$DATE/"

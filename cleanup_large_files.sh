#!/bin/bash

# Script to find and move large memory files to archive
WORKSPACE="/Users/gordonlui/.openclaw/workspace"
MAX_LINES=200

echo "Checking for large files in workspace..."

# Find large .md files in memory directory
find "$WORKSPACE/memory" -name "*.md" -type f | while read file; do
    lines=$(wc -l < "$file")
    if [ $lines -gt $MAX_LINES ]; then
        echo "Moving large file: $file ($lines lines)"
        mv "$file" "$WORKSPACE/memory/archive/"
    fi
done

# Also check workspace root for large files that might be loaded
find "$WORKSPACE" -maxdepth 1 -name "*.md" -type f | while read file; do
    lines=$(wc -l < "$file")
    if [ $lines -gt $MAX_LINES ]; then
        echo "Large file in workspace root: $file ($lines lines)"
        # Don't move automatically, just warn
    fi
done

echo "Cleanup complete!"
#!/usr/bin/env python3
"""
Import MEMORY.md into LanceDB
"""

import re
import os
import lancedb

def parse_memory_file(filepath):
    """Parse MEMORY.md and extract memories"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    memories = []
    
    # Split by headers
    sections = re.split(r'^## ', content, flags=re.MULTILINE)
    
    for section in sections:
        if not section.strip():
            continue
            
        lines = section.strip().split('\n')
        title = lines[0] if lines else "Unknown"
        body = '\n'.join(lines[1:]) if len(lines) > 1 else ""
        
        # Extract category from title
        if "核心提醒" in title or "兩個倉" in title:
            category = "portfolio"
        elif "Cron" in title:
            category = "system"
        elif "Language" in title:
            category = "settings"
        elif "Workspace" in title:
            category = "system"
        elif "System Issues" in title:
            category = "system"
        elif "Trading System" in title:
            category = "trading"
        elif "MiniMax" in title:
            category = "system"
        elif "Volume Analysis" in title:
            category = "trading"
        elif "OANDA" in title:
            category = "trading"
        else:
            category = "general"
        
        # Clean up body - remove tables for now
        body_clean = re.sub(r'\|.*\|', '', body)
        body_clean = re.sub(r'\n+', '\n', body_clean).strip()
        
        if len(body_clean) > 50:  # Only add substantial content
            memories.append({
                "title": title,
                "content": body_clean[:1000],  # Limit length
                "category": category
            })
    
    return memories

def main():
    # Import from MEMORY.md
    memory_file = os.path.expanduser("~/.openclaw/workspace/MEMORY.md")
    
    if not os.path.exists(memory_file):
        print(f"❌ File not found: {memory_file}")
        return
    
    memories = parse_memory_file(memory_file)
    print(f"=== Importing {len(memories)} memories from MEMORY.md ===")
    
    # Connect directly to existing DB
    db = lancedb.connect(os.path.expanduser("~/.openclaw/workspace/lancedb_memory"))
    tbl = db.open_table("memories")
    
    for i, m in enumerate(memories):
        import uuid
        memory_id = str(uuid.uuid4())[:8]
        
        # Add to LanceDB
        data = [{
            "id": memory_id,
            "content": f"## {m['title']}\n\n{m['content']}",
            "timestamp": "2026-02-27T00:00:00",
            "category": m['category'],
            "tags": m['category']
        }]
        
        try:
            tbl.add(data)
            print(f"  ✅ [{i+1}] {m['title'][:50]}...")
        except Exception as e:
            print(f"  ❌ Error adding {m['title']}: {e}")
    
    print(f"\n=== Import Complete ===")
    
    # Test search
    df = tbl.to_pandas()
    print(f"📊 Total memories: {len(df)}")
    
    matches = df[df['content'].str.contains('久留美', na=False)]
    print(f"🔍 Search '久留美': {len(matches)} found")

if __name__ == "__main__":
    main()

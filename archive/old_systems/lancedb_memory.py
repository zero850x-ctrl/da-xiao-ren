#!/usr/bin/env python3
"""
LanceDB Memory System for OpenClaw
為久留美提供長期記憶功能
"""

import os
import json
import lancedb
import pandas as pd
import pyarrow as pa
from datetime import datetime

# Config
DB_PATH = os.path.expanduser("~/.openclaw/workspace/lancedb_memory")
TABLE_NAME = "memories"

class LanceDBMemory:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.db = lancedb.connect(db_path)
        self._init_table()
    
    def _init_table(self):
        """Initialize the memory table"""
        # Check if table exists using new API
        try:
            table_names = list(self.db.list_tables())
        except:
            try:
                table_names = self.db.table_names()
            except:
                table_names = []
        
        if TABLE_NAME not in table_names:
            # Create table with schema using pyarrow
            schema = pa.schema([
                ("id", pa.string()),
                ("content", pa.string()),
                ("timestamp", pa.string()),
                ("category", pa.string()),
                ("tags", pa.string())
            ])
            
            # Create empty table with initial empty data
            empty_data = [{
                "id": "init",
                "content": "Initial memory entry",
                "timestamp": datetime.now().isoformat(),
                "category": "system",
                "tags": "init"
            }]
            
            self.db.create_table(TABLE_NAME, data=empty_data, schema=schema)
            print(f"✅ Created memory table: {TABLE_NAME}")
        else:
            print(f"📂 Using existing table: {TABLE_NAME}")
    
    def add_memory(self, content, category="general", tags=None):
        """Add a new memory"""
        import uuid
        memory_id = str(uuid.uuid4())[:8]
        
        data = [{
            "id": memory_id,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "tags": ",".join(tags) if tags else ""
        }]
        
        tbl = self.db.open_table(TABLE_NAME)
        tbl.add(data)
        return memory_id
    
    def search(self, query, limit=5):
        """Search memories (simple text match for now)"""
        # Get all and filter
        df = self._get_df()
        
        # Basic keyword matching
        if df is None or df.empty:
            return []
            
        matches = df[df['content'].str.contains(query, case=False, na=False)]
        return matches.tail(limit).to_dict('records')
    
    def _get_df(self):
        """Get dataframe"""
        try:
            tbl = self.db.open_table(TABLE_NAME)
            return tbl.to_pandas()
        except:
            return None
    
    def get_all(self, limit=50):
        """Get all memories"""
        df = self._get_df()
        if df is None or df.empty:
            return []
        return df.tail(limit).to_dict('records')
    
    def count(self):
        """Count total memories"""
        df = self._get_df()
        if df is None:
            return 0
        return len(df)

def main():
    """Test the memory system"""
    memory = LanceDBMemory()
    
    print("\n=== LanceDB Memory System ===")
    print(f"📊 Total memories: {memory.count()}")
    
    # Add a test memory
    test_id = memory.add_memory(
        "テストメモ: 久留美システム起動", 
        category="system",
        tags=["test", "japanese"]
    )
    print(f"✅ Added memory: {test_id}")
    
    # Search
    results = memory.search("久留美")
    print(f"\n🔍 Search results for '久留美': {len(results)} found")
    
    # Show all
    all_memories = memory.get_all(5)
    print(f"\n📋 Recent memories: {len(all_memories)}")
    
    return memory

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Inspect ollama_reviews.db to understand its structure
"""

import sqlite3
import os

def inspect_ollama_db():
    if not os.path.exists('ollama_reviews.db'):
        print("❌ ollama_reviews.db not found")
        return
    
    print("🔍 Inspecting ollama_reviews.db...")
    conn = sqlite3.connect('ollama_reviews.db')
    cursor = conn.cursor()
    
    # Get tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"📋 Tables found: {[table[0] for table in tables]}")
    
    for table_name in [table[0] for table in tables]:
        print(f"\n📊 Table: {table_name}")
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print("📝 Columns:")
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        # Get sample data
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"📊 Row count: {count}")
        
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            sample_rows = cursor.fetchall()
            print("🔍 Sample rows:")
            for i, row in enumerate(sample_rows, 1):
                print(f"   Row {i}: {row[:3]}..." if len(row) > 3 else f"   Row {i}: {row}")
    
    conn.close()

if __name__ == "__main__":
    inspect_ollama_db()

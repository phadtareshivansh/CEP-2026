#!/usr/bin/env python
"""
PostgreSQL Migration Helper for Saarthi
Helps migrate data from SQLite to PostgreSQL
Usage: python migrate_to_postgres.py <postgres_url>
"""

import os
import sys
import sqlite3
import json
from pathlib import Path

def get_sqlite_connection():
    """Get SQLite database connection"""
    db_path = Path(__file__).parent / 'db.sqlite3'
    if not db_path.exists():
        print(f"❌ ERROR: db.sqlite3 not found at {db_path}")
        sys.exit(1)
    return sqlite3.connect(str(db_path))

def export_sqlite_dump(output_file='sqlite_export.sql'):
    """Export SQLite database as SQL dump"""
    import subprocess
    db_path = Path(__file__).parent / 'db.sqlite3'
    
    try:
        result = subprocess.run(
            ['sqlite3', str(db_path), '.dump'],
            capture_output=True,
            text=True,
            check=True
        )
        
        with open(output_file, 'w') as f:
            f.write(result.stdout)
        
        print(f"✅ SQLite dump exported to {output_file}")
        print(f"   Lines of SQL: {len(result.stdout.splitlines())}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR exporting SQLite: {e}")
        return False
    except FileNotFoundError:
        print("❌ ERROR: sqlite3 command not found. Install PostgreSQL tools.")
        return False

def get_sqlite_stats():
    """Get statistics about SQLite database"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    
    print("\n📊 SQLite Database Statistics:")
    print(f"   Total tables: {len(tables)}")
    
    total_rows = 0
    for table in tables:
        table_name = table[0]
        if table_name.startswith('sqlite_'):
            continue
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        total_rows += count
        if count > 0:
            print(f"   ✓ {table_name}: {count} rows")
    
    print(f"\n   Total data rows: {total_rows}")
    conn.close()

def test_postgres_connection(database_url):
    """Test PostgreSQL connection"""
    try:
        import psycopg2
        print(f"\n🔗 Testing PostgreSQL connection...")
        print(f"   URL: {database_url}")
        conn = psycopg2.connect(database_url)
        print(f"   ✅ Connection successful!")
        conn.close()
        return True
    except ImportError:
        print("❌ ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    print("\n🚀 Saarthi PostgreSQL Migration Helper")
    print("=" * 60)
    
    # Show SQLite statistics
    get_sqlite_stats()
    
    # Export SQLite dump
    print("\n📝 Exporting SQLite database...")
    if export_sqlite_dump():
        print("\n✅ Next steps:")
        print("   1. Create PostgreSQL database on Supabase if not done")
        print("   2. Get connection string from Supabase")
        print("   3. Run migration:")
        print("      psql <connection_string> < sqlite_export.sql")
        print("   4. Add DATABASE_URL to Vercel env vars")
        print("   5. Redeploy on Vercel")
    
    # Optional: Test PostgreSQL connection if URL provided
    if len(sys.argv) > 1:
        database_url = sys.argv[1]
        test_postgres_connection(database_url)

if __name__ == '__main__':
    main()

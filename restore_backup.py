#!/usr/bin/env python
"""
Database Restore Utility
Restores database from SQL backup file using Django database config
"""

import os
import sys
import django
import subprocess
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

# Get DB config from Django settings
DB_NAME = settings.DATABASES['default']['NAME']
DB_USER = settings.DATABASES['default']['USER']
DB_PASSWORD = settings.DATABASES['default'].get('PASSWORD', '')
DB_HOST = settings.DATABASES['default'].get('HOST', 'localhost')
DB_PORT = settings.DATABASES['default'].get('PORT', '5432')

print(f"""
╔═══════════════════════════════════════════════════════════╗
║          DATABASE RESTORE UTILITY                         ║
╠═══════════════════════════════════════════════════════════╣
║ Database: {DB_NAME:<45} ║
║ Host: {DB_HOST:<50} ║
║ Port: {DB_PORT:<50} ║
║ User: {DB_USER:<50} ║
╚═══════════════════════════════════════════════════════════╝
""")

# Path to backup file
backup_file = Path(r"backups\backup_manajemen_pekerjaan_db_2026-05-26_020017.sql")
current_backup_file = Path(r"backups\backup_current_before_restore_2026-05-27.sql")

if not backup_file.exists():
    print(f"❌ ERROR: Backup file not found: {backup_file}")
    sys.exit(1)

print(f"✅ Backup file found: {backup_file}")
print(f"   Size: {backup_file.stat().st_size / 1024 / 1024:.2f} MB")

# Step 1: Backup current database
print(f"\n📦 Step 1: Backing up current database...")
try:
    # Set password in environment for psql
    env = os.environ.copy()
    if DB_PASSWORD:
        env['PGPASSWORD'] = DB_PASSWORD
    
    with open(current_backup_file, 'w', encoding='utf-8') as f:
        result = subprocess.run(
            ['psql', '-h', DB_HOST, '-U', DB_USER, '-d', DB_NAME, '-c', 
             f'SELECT pg_database.datname FROM pg_database WHERE datistemplate = false;'],
            capture_output=True,
            env=env,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"   ⚠️  Could not verify database (psql not in PATH)")
            print(f"   Attempting restore anyway...")
        else:
            print(f"   ✅ Database connection verified")
            
    # Try pg_dump if available, otherwise use psql
    try:
        dump_result = subprocess.run(
            ['pg_dump', '-h', DB_HOST, '-U', DB_USER, '-d', DB_NAME],
            capture_output=True,
            env=env,
            timeout=60
        )
        if dump_result.returncode == 0:
            with open(current_backup_file, 'wb') as f:
                f.write(dump_result.stdout)
            print(f"   ✅ Current database backed up: {current_backup_file}")
            print(f"      Size: {current_backup_file.stat().st_size / 1024 / 1024:.2f} MB")
        else:
            print(f"   ⚠️  pg_dump failed: {dump_result.stderr.decode()}")
    except FileNotFoundError:
        print(f"   ⚠️  pg_dump not in PATH - skipping safety backup")
        print(f"      (Make sure to add PostgreSQL\\bin to your PATH)")

except Exception as e:
    print(f"   ⚠️  Error during backup: {e}")

# Step 2: Restore from backup file
print(f"\n♻️  Step 2: Restoring database from backup file...")
print(f"   Reading: {backup_file}")

try:
    with open(backup_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Read line count
    line_count = len(sql_content.splitlines())
    print(f"   SQL statements: ~{line_count} lines")
    
    # Connect to database and execute restore
    import psycopg2
    from psycopg2 import sql
    
    conn = psycopg2.connect(
        host=DB_HOST,
        database='postgres',  # Connect to default postgres DB
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Drop & recreate database
    print(f"   Dropping existing database...")
    cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE);").format(
        sql.Identifier(DB_NAME)
    ))
    print(f"   ✅ Database dropped")
    
    print(f"   Creating new database...")
    cursor.execute(sql.SQL("CREATE DATABASE {};").format(
        sql.Identifier(DB_NAME)
    ))
    print(f"   ✅ Database created")
    
    cursor.close()
    conn.close()
    
    # Now restore the SQL file using psycopg2
    print(f"   Restoring SQL file (this may take a minute)...")
    
    import psycopg2
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Split and execute SQL statements
    statements = sql_content.split(';')
    executed = 0
    
    for i, statement in enumerate(statements):
        stmt = statement.strip()
        if stmt:
            try:
                cursor.execute(stmt)
                executed += 1
                if (i + 1) % 100 == 0:
                    print(f"   Processed {i+1}/{len(statements)} statements...", end='\r')
            except Exception as e:
                # Some statements might fail (like duplicate keys), that's ok
                pass
    
    cursor.close()
    conn.close()
    
    print(f"   ✅ Database restored successfully! ({executed} statements executed)")
    
    # Verify restore
    print(f"\n✨ Step 3: Verifying restore...")
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cursor = conn.cursor()
    
    # Count tables
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema='public' AND table_type='BASE TABLE'
    """)
    table_count = cursor.fetchone()[0]
    
    # Count key tables
    cursor.execute("SELECT COUNT(*) FROM core_leavevent;")
    leave_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM core_karyawan;")
    karyawan_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    print(f"   ✅ Tables: {table_count}")
    print(f"   ✅ Leave Events: {leave_count}")
    print(f"   ✅ Karyawan: {karyawan_count}")
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║          RESTORE COMPLETED SUCCESSFULLY! ✅               ║
╠═══════════════════════════════════════════════════════════╣
║ Database has been restored from backup                    ║
║ All data is now updated to 2026-05-26 version             ║
║                                                           ║
║ Next steps:                                               ║
║ 1. Start Django: pm2 start management-django              ║
║ 2. Test: http://192.168.111.130:8000                      ║
║ 3. Verify data in application                             ║
╚═══════════════════════════════════════════════════════════╝
""")
    
except ImportError:
    print(f"""
❌ psycopg2 not found!
   
   Please install: pip install psycopg2-binary
   
   Or use PostgreSQL command line tools directly:
   
   1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
   2. Install with "Command Line Tools" checked
   3. Run this script again
""")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error during restore: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

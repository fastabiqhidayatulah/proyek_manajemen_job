import os
import subprocess
import tempfile
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.db import connection
from .forms_backup import DatabaseBackupForm
import logging
import platform

logger = logging.getLogger(__name__)

# Detect PostgreSQL path based on OS
if platform.system() == 'Windows':
    # PostgreSQL Windows installation path
    PSQL_PATHS = [
        'C:\\apps\\postgresql\\bin\\psql.exe',
        'C:\\Program Files\\PostgreSQL\\16\\bin\\psql.exe',
        'C:\\Program Files\\PostgreSQL\\15\\bin\\psql.exe',
        'C:\\Program Files\\PostgreSQL\\14\\bin\\psql.exe',
        'C:\\Program Files (x86)\\PostgreSQL\\16\\bin\\psql.exe',
    ]
    PG_DUMP_PATHS = [
        'C:\\apps\\postgresql\\bin\\pg_dump.exe',
        'C:\\Program Files\\PostgreSQL\\16\\bin\\pg_dump.exe',
        'C:\\Program Files\\PostgreSQL\\15\\bin\\pg_dump.exe',
        'C:\\Program Files\\PostgreSQL\\14\\bin\\pg_dump.exe',
        'C:\\Program Files (x86)\\PostgreSQL\\16\\bin\\pg_dump.exe',
    ]
    
    # Find first available path
    PSQL_CMD = next((p for p in PSQL_PATHS if os.path.exists(p)), 'psql')
    PG_DUMP_CMD = next((p for p in PG_DUMP_PATHS if os.path.exists(p)), 'pg_dump')
else:
    PSQL_CMD = 'psql'
    PG_DUMP_CMD = 'pg_dump'


def is_admin(user):
    """Check if user is admin/superuser"""
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def backup_restore_management(request):
    """
    Halaman untuk manage database backup & restore
    """
    context = {
        'page_title': 'Database Backup & Restore',
        'form': DatabaseBackupForm(),
    }
    
    if request.method == 'POST':
        form = DatabaseBackupForm(request.POST, request.FILES)
        
        if form.is_valid():
            backup_file = request.FILES['backup_file']
            
            try:
                # Save uploaded file to temp directory
                temp_dir = tempfile.gettempdir()
                temp_file_path = os.path.join(temp_dir, backup_file.name)
                
                # Write file to disk
                with open(temp_file_path, 'wb+') as destination:
                    for chunk in backup_file.chunks():
                        destination.write(chunk)
                
                logger.info(f"Backup file uploaded: {temp_file_path}")
                
                # Get database credentials from settings
                db_name = settings.DATABASES['default']['NAME']
                db_user = settings.DATABASES['default']['USER']
                db_host = settings.DATABASES['default']['HOST']
                db_port = settings.DATABASES['default']['PORT']
                db_password = settings.DATABASES['default']['PASSWORD']
                
                # Create backup of current database (safety)
                backup_current_filename = f"backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
                backup_current_path = os.path.join(settings.BASE_DIR, 'backups', backup_current_filename)
                
                messages.info(request, f'🔄 Backing up current database ke {backup_current_filename}...')
                
                # Create backup of current data
                backup_cmd = [PG_DUMP_CMD, '-U', db_user, '-h', db_host, '-p', str(db_port), '-d', db_name]
                with open(backup_current_path, 'w') as backup_file_handle:
                    try:
                        env = os.environ.copy()
                        env['PGPASSWORD'] = db_password
                        result = subprocess.run(
                            backup_cmd,
                            stdout=backup_file_handle,
                            stderr=subprocess.PIPE,
                            text=True,
                            env=env,
                            timeout=300
                        )
                        
                        if result.returncode != 0:
                            messages.warning(request, f'⚠️ Backup current database mungkin tidak lengkap: {result.stderr}')
                        else:
                            messages.success(request, f'✅ Backup current database berhasil')
                            
                    except subprocess.TimeoutExpired:
                        messages.warning(request, '⚠️ Backup current database timeout (data mungkin besar)')
                    except Exception as e:
                        messages.warning(request, f'⚠️ Error backup current: {str(e)}')
                
                logger.info(f"Current database backed up to: {backup_current_path}")
                
                # Restore from uploaded backup
                messages.info(request, '🔄 Melakukan restore database...')
                
                restore_cmd = [PSQL_CMD, '-U', db_user, '-h', db_host, '-p', str(db_port), '-d', db_name]
                
                try:
                    with open(temp_file_path, 'r') as restore_file:
                        env = os.environ.copy()
                        env['PGPASSWORD'] = db_password
                        result = subprocess.run(
                            restore_cmd,
                            stdin=restore_file,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            env=env,
                            timeout=600
                        )
                    
                    if result.returncode == 0:
                        messages.success(request, '✅ Restore database BERHASIL!')
                        logger.info('Database restore completed successfully')
                        
                        # Clean up temp file
                        try:
                            os.remove(temp_file_path)
                        except:
                            pass
                        
                        # Get backup info
                        context['restore_success'] = True
                        context['backup_file'] = backup_file.name
                        context['restore_time'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                        context['form'] = DatabaseBackupForm()
                        
                        return render(request, 'backup_restore.html', context)
                    else:
                        messages.error(request, f'❌ Restore GAGAL: {result.stderr[:500]}')
                        logger.error(f'Restore failed: {result.stderr}')
                        
                except subprocess.TimeoutExpired:
                    messages.error(request, '❌ Restore timeout (data terlalu besar atau koneksi lambat)')
                    logger.error('Restore timeout')
                    
                except Exception as e:
                    messages.error(request, f'❌ Error restore: {str(e)}')
                    logger.error(f'Restore error: {str(e)}')
                
            except Exception as e:
                messages.error(request, f'❌ Error: {str(e)}')
                logger.error(f'Backup/Restore error: {str(e)}', exc_info=True)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        
        context['form'] = form
    
    # Get list of recent backups
    try:
        backups_dir = os.path.join(settings.BASE_DIR, 'backups')
        if os.path.exists(backups_dir):
            backup_files = []
            for file in os.listdir(backups_dir):
                if file.endswith('.sql'):
                    file_path = os.path.join(backups_dir, file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    backup_files.append({
                        'name': file,
                        'size': f'{file_size:.2f} MB',
                        'modified': file_mtime.strftime('%d/%m/%Y %H:%M:%S'),
                        'path': file_path,
                    })
            
            # Sort by modified date (newest first)
            backup_files.sort(key=lambda x: x['modified'], reverse=True)
            context['backup_files'] = backup_files[:10]  # Show 10 latest
            context['total_backups'] = len(backup_files)
    except Exception as e:
        logger.error(f'Error reading backups: {str(e)}')
        context['backup_error'] = str(e)
    
    return render(request, 'backup_restore.html', context)


@login_required
@user_passes_test(is_admin)
def backup_create_now(request):
    """
    Create database backup immediately
    """
    if request.method == 'POST':
        try:
            db_name = settings.DATABASES['default']['NAME']
            db_user = settings.DATABASES['default']['USER']
            db_host = settings.DATABASES['default']['HOST']
            db_port = settings.DATABASES['default']['PORT']
            db_password = settings.DATABASES['default']['PASSWORD']
            
            filename = f"backup_manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            filepath = os.path.join(settings.BASE_DIR, 'backups', filename)
            
            # Make sure backups directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            backup_cmd = [PG_DUMP_CMD, '-U', db_user, '-h', db_host, '-p', str(db_port), '-d', db_name]
            
            with open(filepath, 'w') as f:
                env = os.environ.copy()
                env['PGPASSWORD'] = db_password
                result = subprocess.run(
                    backup_cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    timeout=300
                )
            
            if result.returncode == 0:
                file_size = os.path.getsize(filepath) / (1024 * 1024)
                messages.success(request, f'✅ Backup berhasil dibuat: {filename} ({file_size:.2f} MB)')
                logger.info(f'Backup created: {filename}')
            else:
                messages.error(request, f'❌ Backup gagal: {result.stderr[:200]}')
                logger.error(f'Backup failed: {result.stderr}')
                
        except subprocess.TimeoutExpired:
            messages.error(request, '❌ Backup timeout')
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
            logger.error(f'Backup error: {str(e)}', exc_info=True)
    
    return redirect('core:backup_restore')


@login_required
@user_passes_test(is_admin)
def database_health_check(request):
    """
    Check database health and statistics
    """
    context = {}
    
    try:
        with connection.cursor() as cursor:
            # Get table sizes
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
                FROM pg_tables
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)
            
            context['table_sizes'] = [
                {
                    'schema': row[0],
                    'table': row[1],
                    'size': row[2],
                }
                for row in cursor.fetchall()
            ]
            
            # Get row counts
            cursor.execute("""
                SELECT tablename, n_live_tup as row_count
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
            """)
            
            context['table_rows'] = [
                {
                    'table': row[0],
                    'rows': row[1],
                }
                for row in cursor.fetchall()
            ]
            
            # Get database size
            cursor.execute(f"""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)
            context['database_size'] = cursor.fetchone()[0]
            
            # Connection count
            cursor.execute("""
                SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()
            """)
            context['connection_count'] = cursor.fetchone()[0]
            
            # Last vacuum
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    last_vacuum,
                    last_autovacuum
                FROM pg_stat_user_tables
                WHERE last_vacuum IS NOT NULL OR last_autovacuum IS NOT NULL
                ORDER BY last_autovacuum DESC
                LIMIT 5
            """)
            
            context['last_vacuums'] = [
                {
                    'table': row[1],
                    'last_vacuum': row[2],
                    'last_autovacuum': row[3],
                }
                for row in cursor.fetchall()
            ]
            
    except Exception as e:
        context['error'] = str(e)
        logger.error(f'Health check error: {str(e)}', exc_info=True)
    
    return render(request, 'database_health.html', context)

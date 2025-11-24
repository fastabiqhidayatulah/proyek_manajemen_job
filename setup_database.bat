@echo off
REM Setup PostgreSQL Database dan User
REM Jalankan sebagai Administrator
REM Sesuaikan password sebelum menjalankan

echo.
echo ========================================
echo SETUP POSTGRESQL DATABASE
echo ========================================
echo.

set DB_NAME=proyek_manajemen_job
set DB_USER=django_user
set DB_PASSWORD=django_password_123
set PG_USER=postgres
set PG_HOST=localhost
set PG_PORT=5432

echo Database Name: %DB_NAME%
echo Database User: %DB_USER%
echo.
echo PASTIKAN:
echo 1. PostgreSQL sudah terinstall
echo 2. PostgreSQL service sudah running
echo 3. Anda tahu password untuk user 'postgres'
echo.
pause

echo Connecting to PostgreSQL...
echo.

REM Create database dan user menggunakan psql
psql -U %PG_USER% -h %PG_HOST% -p %PG_PORT% <<EOF
-- Buat database baru
CREATE DATABASE %DB_NAME%;

-- Buat user baru
CREATE USER %DB_USER% WITH PASSWORD '%DB_PASSWORD%';

-- Set default parameters
ALTER ROLE %DB_USER% SET client_encoding TO 'utf8';
ALTER ROLE %DB_USER% SET default_transaction_isolation TO 'read committed';
ALTER ROLE %DB_USER% SET default_transaction_deferrable TO on;
ALTER ROLE %DB_USER% SET timezone TO 'UTC';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;

-- Koneksi ke database
\c %DB_NAME%

-- Grant schema privileges
GRANT USAGE ON SCHEMA public TO %DB_USER%;
GRANT CREATE ON SCHEMA public TO %DB_USER%;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO %DB_USER%;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO %DB_USER%;

\echo.
\echo ========================================
\echo DATABASE SETUP COMPLETE!
\echo ========================================
\echo Database: %DB_NAME%
\echo User: %DB_USER%
\echo Host: %PG_HOST%:%PG_PORT%
\echo ========================================
EOF

echo.
pause

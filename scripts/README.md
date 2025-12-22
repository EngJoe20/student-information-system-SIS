# Scripts Directory

Utility scripts for database management and testing.

## 📁 Available Scripts

### 1. seed_database.py
Seeds the database with initial data for development/testing.

**What it creates:**
- System users (Admin, Registrar, Instructors)
- 20 student accounts
- 13 courses across different departments
- 20 rooms across 4 buildings
- 20 class sections
- Enrollments, attendance, grades
- Notifications, messages, student requests

**Usage:**
```bash
# Run directly
python scripts/seed_database.py

# Or as management command (if created)
python manage.py seed_database
```

**Test Accounts Created:**
| Role | Username | Password |
|------|----------|----------|
| Admin | admin | Admin123! |
| Registrar | registrar1 | Registrar123! |
| Instructor | instructor1 | Instructor123! |
| Student | student1 | Student123! |

---

### 2. generate_test_data.py
Generates comprehensive test data with historical records.

**What it creates:**
- 3 semesters of historical data
- Completed courses with final grades
- Realistic attendance patterns
- Performance trends
- Updated student GPAs

**Usage:**
```bash
# Must run seed_database.py first!
python scripts/generate_test_data.py
```

**Prerequisites:**
- Run `seed_database.py` first
- Database must be initialized

---

### 3. backup_database.sh (Linux/Mac)
Automated backup script for production systems.

**Features:**
- PostgreSQL/SQLite database backup
- Media files backup
- Static files backup
- Log files backup
- Automatic compression
- Old backup cleanup
- Backup manifest generation

**Usage:**
```bash
# Make executable (first time only)
chmod +x scripts/backup_database.sh

# Full backup (default)
./scripts/backup_database.sh

# Database only
./scripts/backup_database.sh --type db-only

# Custom destination
./scripts/backup_database.sh --dest /mnt/backup

# Keep 60 backups instead of 30
./scripts/backup_database.sh --keep 60

# Show help
./scripts/backup_database.sh --help
```

**Options:**
- `-t, --type` : Backup type (full, db-only, media-only)
- `-d, --dest` : Destination directory (default: ./backups)
- `-k, --keep` : Number of backups to keep (default: 30)
- `-c, --compress` : Compress backups (default: true)
- `-h, --help` : Show help message

---

### 4. backup_database.bat (Windows)
Windows version of the backup script.

**Usage:**
```cmd
# Full backup
scripts\backup_database.bat

# Database only
scripts\backup_database.bat db-only

# Custom destination
scripts\backup_database.bat full C:\Backups
```

---

## 🚀 Quick Start

### First Time Setup
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python manage.py migrate

# 4. Seed database with initial data
python scripts/seed_database.py

# 5. Generate comprehensive test data (optional)
python scripts/generate_test_data.py

# 6. Start server
python manage.py runserver
```

### Development Workflow
```bash
# Reset and reseed database
python manage.py flush --no-input
python scripts/seed_database.py

# Add more test data
python scripts/generate_test_data.py
```

### Production Backup
```bash
# Setup automated backups (Linux cron)
# Add to crontab: crontab -e
0 2 * * * /path/to/scripts/backup_database.sh

# Manual backup before major changes
./scripts/backup_database.sh --type full
```

---

## 📊 Data Volumes

### seed_database.py Creates:
- ~25 users (5 staff + 20 students)
- 20 student profiles
- 13 courses
- 20 rooms
- ~20 classes
- ~100 enrollments
- ~1000 attendance records
- ~400 grade records
- ~30 notifications
- ~10 messages
- ~20 student requests

### generate_test_data.py Adds:
- ~24 additional classes (3 semesters)
- ~360 enrollments
- ~7200 attendance records
- ~2520 grade records
- Completed course data
- Updated GPAs

**Total:** ~500 enrollments, ~8000 attendance records, ~3000 grades

---

## 🛠️ Customization

### Modify seed_database.py
```python
# Change number of students
for i in range(1, 21):  # Change 21 to desired number + 1

# Change courses
courses_data = [
    ('YOUR_CODE', 'Your Course', 'Department', credits, ''),
    # Add more courses
]

# Change rooms
for i in range(5):  # Change 5 to desired number per building
```

### Modify generate_test_data.py
```python
# Change historical semesters
semesters = [
    (self.current_year - 2, 'FALL'),   # Add more
    (self.current_year - 1, 'SPRING'),
    # etc.
]

# Change performance patterns
performance_factor = random.uniform(0.6, 1.0)  # Adjust range
```

---

## 🔧 Troubleshooting

### "Module not found" errors
```bash
# Make sure you're in project root
cd /path/to/student-information-system-SIS

# Activate virtual environment
source venv/bin/activate
```

### Database connection errors
```bash
# Check database is running
# PostgreSQL
sudo systemctl status postgresql

# Check .env file has correct credentials
cat .env | grep DB_
```

### Permission denied (backup script)
```bash
# Make script executable
chmod +x scripts/backup_database.sh
```

### Backup fails
```bash
# Check dependencies
which pg_dump sqlite3 tar gzip

# Check disk space
df -h
```

---

## 📝 Notes

### For Production:
- Run `seed_database.py` only once during initial setup
- Use `backup_database.sh` in cron for automated backups
- Store backups off-site for disaster recovery
- Test restore procedure regularly

### For Development:
- Run `seed_database.py` whenever you need fresh test data
- Run `generate_test_data.py` for realistic historical data
- Use backup scripts before major database changes

### For Testing:
- `seed_database.py` provides consistent baseline data
- `generate_test_data.py` adds variability for testing
- Both scripts are idempotent (safe to run multiple times)

---

## 🎯 Best Practices

1. **Always backup before:**
   - Major database migrations
   - Production deployments
   - Database schema changes

2. **Test your backups:**
   - Restore to a test environment monthly
   - Verify data integrity
   - Document restore procedures

3. **Monitor backup size:**
   - Clean up old backups regularly
   - Monitor disk space
   - Compress backups

4. **Secure your backups:**
   - Encrypt sensitive data
   - Restrict access permissions
   - Store off-site copies

---

## 📧 Support

For issues or questions:
- Check logs in `logs/` directory
- Review error messages
- Consult main documentation

---

## Windows Backup Script (backup_database.bat)

```batch
@echo off
REM ============================================================================
REM Database Backup Script for Windows
REM ============================================================================

setlocal enabledelayedexpansion

REM Configuration
set BACKUP_TYPE=%1
if "%BACKUP_TYPE%"=="" set BACKUP_TYPE=full

set BACKUP_DIR=%2
if "%BACKUP_DIR%"=="" set BACKUP_DIR=.\backups

set TIMESTAMP=%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

REM Load environment variables from .env
if exist .env (
    for /f "tokens=*" %%a in (.env) do (
        set %%a
    )
)

REM Default database config
if "%DB_NAME%"=="" set DB_NAME=sis_db
if "%DB_USER%"=="" set DB_USER=sis_user
if "%DB_HOST%"=="" set DB_HOST=localhost
if "%DB_PORT%"=="" set DB_PORT=5432

echo ================================
echo    SIS Database Backup
echo ================================
echo.

REM Create backup directory
if not exist "%BACKUP_DIR%" (
    mkdir "%BACKUP_DIR%"
    echo Created backup directory: %BACKUP_DIR%
)

REM Backup based on type
if "%BACKUP_TYPE%"=="full" (
    echo Performing full backup...
    call :backup_database
    call :backup_media
    call :backup_static
    goto :end
)

if "%BACKUP_TYPE%"=="db-only" (
    echo Performing database-only backup...
    call :backup_database
    goto :end
)

if "%BACKUP_TYPE%"=="media-only" (
    echo Performing media-only backup...
    call :backup_media
    goto :end
)

echo Unknown backup type: %BACKUP_TYPE%
goto :end

:backup_database
echo Backing up database...

REM Try SQLite first
if exist "db.sqlite3" (
    copy /Y "db.sqlite3" "%BACKUP_DIR%\sqlite_%TIMESTAMP%.db"
    echo SQLite backup created
) else (
    REM PostgreSQL backup
    set PGPASSWORD=%DB_PASSWORD%
    pg_dump -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% > "%BACKUP_DIR%\postgres_%DB_NAME%_%TIMESTAMP%.sql"
    echo PostgreSQL backup created
)
goto :eof

:backup_media
if exist "media" (
    echo Backing up media files...
    tar -czf "%BACKUP_DIR%\media_%TIMESTAMP%.tar.gz" media
    echo Media backup created
)
goto :eof

:backup_static
if exist "staticfiles" (
    echo Backing up static files...
    tar -czf "%BACKUP_DIR%\static_%TIMESTAMP%.tar.gz" staticfiles
    echo Static files backup created
)
goto :eof

:end
echo.
echo Backup completed!
echo Location: %BACKUP_DIR%
echo.
pause
```

Save this as `scripts/backup_database.bat` for Windows users.
#!/bin/bash

################################################################################
# Database Backup Script for Student Information System
################################################################################
#
# This script creates backups of:
# - PostgreSQL database
# - SQLite database (development)
# - Media files (uploads)
# - Static files
#
# Usage:
#   ./scripts/backup_database.sh [options]
#
# Options:
#   -t, --type      Backup type: full, db-only, media-only (default: full)
#   -d, --dest      Destination directory (default: ./backups)
#   -k, --keep      Number of backups to keep (default: 30)
#   -c, --compress  Compress backups (default: true)
#   -h, --help      Show this help message
#
# Examples:
#   ./scripts/backup_database.sh
#   ./scripts/backup_database.sh --type db-only --keep 60
#   ./scripts/backup_database.sh --dest /mnt/backup
#
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
BACKUP_TYPE="full"
BACKUP_DIR="./backups"
KEEP_BACKUPS=30
COMPRESS=true
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Database configuration (loaded from .env if exists)
DB_NAME="${DB_NAME:-sis_db}"
DB_USER="${DB_USER:-sis_user}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

################################################################################
# Functions
################################################################################

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}   SIS Database Backup${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

show_help() {
    head -n 30 "$0" | grep "^#" | sed 's/^# \?//'
    exit 0
}

load_env() {
    if [ -f "$PROJECT_ROOT/.env" ]; then
        print_info "Loading environment variables from .env"
        export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
    fi
}

check_dependencies() {
    print_info "Checking dependencies..."
    
    local missing_deps=0
    
    # Check for required commands
    for cmd in pg_dump sqlite3 tar gzip; do
        if ! command -v $cmd &> /dev/null; then
            print_warning "$cmd is not installed"
            missing_deps=$((missing_deps + 1))
        fi
    done
    
    if [ $missing_deps -gt 0 ]; then
        print_error "Missing $missing_deps required dependencies"
        exit 1
    fi
    
    print_success "All dependencies found"
}

create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        print_success "Created backup directory: $BACKUP_DIR"
    fi
}

backup_postgresql() {
    print_info "Backing up PostgreSQL database..."
    
    local backup_file="$BACKUP_DIR/postgres_${DB_NAME}_${TIMESTAMP}.sql"
    
    # Export password for pg_dump
    export PGPASSWORD="$DB_PASSWORD"
    
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > "$backup_file" 2>/dev/null; then
        print_success "PostgreSQL backup created: $(basename $backup_file)"
        
        # Compress if enabled
        if [ "$COMPRESS" = true ]; then
            gzip "$backup_file"
            print_success "Backup compressed: $(basename $backup_file).gz"
            echo "$backup_file.gz"
        else
            echo "$backup_file"
        fi
    else
        print_error "Failed to backup PostgreSQL database"
        return 1
    fi
    
    # Unset password
    unset PGPASSWORD
}

backup_sqlite() {
    print_info "Backing up SQLite database..."
    
    local sqlite_db="$PROJECT_ROOT/db.sqlite3"
    
    if [ -f "$sqlite_db" ]; then
        local backup_file="$BACKUP_DIR/sqlite_${TIMESTAMP}.db"
        
        # Use sqlite3 to create a clean backup
        sqlite3 "$sqlite_db" ".backup '$backup_file'"
        
        print_success "SQLite backup created: $(basename $backup_file)"
        
        # Compress if enabled
        if [ "$COMPRESS" = true ]; then
            gzip "$backup_file"
            print_success "Backup compressed: $(basename $backup_file).gz"
            echo "$backup_file.gz"
        else
            echo "$backup_file"
        fi
    else
        print_warning "SQLite database not found: $sqlite_db"
    fi
}

backup_media_files() {
    print_info "Backing up media files..."
    
    local media_dir="$PROJECT_ROOT/media"
    
    if [ -d "$media_dir" ] && [ "$(ls -A $media_dir)" ]; then
        local backup_file="$BACKUP_DIR/media_${TIMESTAMP}.tar"
        
        tar -cf "$backup_file" -C "$PROJECT_ROOT" media/
        
        print_success "Media backup created: $(basename $backup_file)"
        
        # Compress if enabled
        if [ "$COMPRESS" = true ]; then
            gzip "$backup_file"
            print_success "Backup compressed: $(basename $backup_file).gz"
            echo "$backup_file.gz"
        else
            echo "$backup_file"
        fi
    else
        print_warning "No media files to backup"
    fi
}

backup_static_files() {
    print_info "Backing up static files..."
    
    local static_dir="$PROJECT_ROOT/staticfiles"
    
    if [ -d "$static_dir" ] && [ "$(ls -A $static_dir)" ]; then
        local backup_file="$BACKUP_DIR/static_${TIMESTAMP}.tar"
        
        tar -cf "$backup_file" -C "$PROJECT_ROOT" staticfiles/
        
        print_success "Static files backup created: $(basename $backup_file)"
        
        # Compress if enabled
        if [ "$COMPRESS" = true ]; then
            gzip "$backup_file"
            print_success "Backup compressed: $(basename $backup_file).gz"
            echo "$backup_file.gz"
        else
            echo "$backup_file"
        fi
    else
        print_warning "No static files to backup"
    fi
}

backup_logs() {
    print_info "Backing up log files..."
    
    local logs_dir="$PROJECT_ROOT/logs"
    
    if [ -d "$logs_dir" ] && [ "$(ls -A $logs_dir)" ]; then
        local backup_file="$BACKUP_DIR/logs_${TIMESTAMP}.tar.gz"
        
        tar -czf "$backup_file" -C "$PROJECT_ROOT" logs/
        
        print_success "Logs backup created: $(basename $backup_file)"
        echo "$backup_file"
    else
        print_warning "No log files to backup"
    fi
}

create_manifest() {
    local manifest_file="$BACKUP_DIR/manifest_${TIMESTAMP}.txt"
    
    print_info "Creating backup manifest..."
    
    {
        echo "SIS Database Backup Manifest"
        echo "============================"
        echo "Backup Date: $(date)"
        echo "Backup Type: $BACKUP_TYPE"
        echo "Project Root: $PROJECT_ROOT"
        echo ""
        echo "Files Created:"
        echo "-------------"
        ls -lh "$BACKUP_DIR" | grep "$TIMESTAMP"
        echo ""
        echo "Database Info:"
        echo "-------------"
        echo "DB Name: $DB_NAME"
        echo "DB Host: $DB_HOST"
        echo ""
        echo "System Info:"
        echo "-----------"
        uname -a
    } > "$manifest_file"
    
    print_success "Manifest created: $(basename $manifest_file)"
}

cleanup_old_backups() {
    print_info "Cleaning up old backups (keeping last $KEEP_BACKUPS)..."
    
    # Count current backups
    local backup_count=$(ls -1 "$BACKUP_DIR" | grep -E '\.(sql|db|tar)(\.gz)?$' | wc -l)
    
    if [ "$backup_count" -gt "$KEEP_BACKUPS" ]; then
        # Remove oldest backups
        ls -1t "$BACKUP_DIR" | grep -E '\.(sql|db|tar)(\.gz)?$' | tail -n +$((KEEP_BACKUPS + 1)) | while read file; do
            rm -f "$BACKUP_DIR/$file"
            print_info "Removed old backup: $file"
        done
        
        print_success "Old backups cleaned up"
    else
        print_info "No old backups to remove (current: $backup_count, keep: $KEEP_BACKUPS)"
    fi
}

get_backup_size() {
    local size=$(du -sh "$BACKUP_DIR" | cut -f1)
    print_info "Total backup size: $size"
}

perform_backup() {
    print_header
    
    case "$BACKUP_TYPE" in
        full)
            print_info "Performing full backup..."
            backup_postgresql || backup_sqlite
            backup_media_files
            backup_static_files
            backup_logs
            ;;
        db-only)
            print_info "Performing database-only backup..."
            backup_postgresql || backup_sqlite
            ;;
        media-only)
            print_info "Performing media-only backup..."
            backup_media_files
            ;;
        *)
            print_error "Unknown backup type: $BACKUP_TYPE"
            exit 1
            ;;
    esac
    
    create_manifest
    cleanup_old_backups
    get_backup_size
    
    echo ""
    print_success "Backup completed successfully!"
    print_info "Backup location: $BACKUP_DIR"
}

################################################################################
# Parse command line arguments
################################################################################

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            BACKUP_TYPE="$2"
            shift 2
            ;;
        -d|--dest)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -k|--keep)
            KEEP_BACKUPS="$2"
            shift 2
            ;;
        -c|--compress)
            COMPRESS="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            ;;
    esac
done

################################################################################
# Main execution
################################################################################

# Change to project root
cd "$PROJECT_ROOT"

# Load environment variables
load_env

# Check dependencies
check_dependencies

# Create backup directory
create_backup_dir

# Perform backup
perform_backup

exit 0
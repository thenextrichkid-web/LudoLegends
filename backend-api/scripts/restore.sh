#!/bin/bash
# PostgreSQL restore script for Ludo Legends
# Usage: ./restore.sh <backup_file.sql.gz>

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lh /backups/postgres/*.sql.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "WARNING: This will DROP and recreate the ludo_legends database!"
echo "File: $BACKUP_FILE"
read -p "Type 'YES RESTORE' to confirm: " CONFIRM

if [ "$CONFIRM" != "YES RESTORE" ]; then
    echo "Aborted."
    exit 1
fi

echo "[$(date -u)] Stopping application connections..."
psql -h "${DB_HOST:-localhost}" -U "${DB_USER:-ludo}" -d postgres \
    -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'ludo_legends' AND pid <> pg_backend_pid();" || true

echo "[$(date -u)] Dropping and recreating database..."
psql -h "${DB_HOST:-localhost}" -U "${DB_USER:-ludo}" -d postgres \
    -c "DROP DATABASE IF EXISTS ludo_legends;"
psql -h "${DB_HOST:-localhost}" -U "${DB_USER:-ludo}" -d postgres \
    -c "CREATE DATABASE ludo_legends OWNER ludo;"

echo "[$(date -u)] Restoring from backup..."
pg_restore -h "${DB_HOST:-localhost}" -U "${DB_USER:-ludo}" -d ludo_legends \
    --no-owner --no-privileges --verbose "$BACKUP_FILE" 2>&1 | tail -5

echo "[$(date -u)] Restore complete. Verify with: SELECT count(*) FROM users;"

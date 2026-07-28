#!/bin/bash
# PostgreSQL backup script for Ludo Legends
# Run daily via cron: 0 2 * * * /app/scripts/backup.sh

set -euo pipefail

BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/ludo_legends_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=7

mkdir -p "$BACKUP_DIR"

echo "[$(date -u)] Starting backup..."

pg_dump -h "${DB_HOST:-localhost}" -U "${DB_USER:-ludo}" -d "${DB_NAME:-ludo_legends}" \
    --format=custom --compress=9 > "$BACKUP_FILE"

FILESIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "[$(date -u)] Backup complete: $BACKUP_FILE ($FILESIZE)"

echo "[$(date -u)] Cleaning backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete
REMAINING=$(find "$BACKUP_DIR" -name "*.sql.gz" | wc -l)
echo "[$(date -u)] Remaining backups: $REMAINING"

echo "[$(date -u)] Backup cycle complete."

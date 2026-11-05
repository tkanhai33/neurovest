#!/usr/bin/env bash
# NeuroVest database backup — failure-safe compressed snapshot.

set -Eeuo pipefail
umask 077

BACKUP_DIR="/home/tkanhai/Neurovest/backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/neurovest_backup_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

TEMP_FILE="$(mktemp "$BACKUP_DIR/.neurovest_backup_XXXXXXXX.sql.gz")"

cleanup() {
    if [ -n "${TEMP_FILE:-}" ] && [ -f "$TEMP_FILE" ]; then
        rm -f -- "$TEMP_FILE"
    fi
}
trap cleanup EXIT

echo "Backup initialization: Creating PostgreSQL snapshot..."

# This service runs as root. No sudo is required here.
# -i avoids allocating a pseudo-terminal in the SQL stream.
# pipefail catches failures from either docker/pg_dump or gzip.
if ! docker exec -i neurovest_postgres \
    pg_dump -U postgres -d neurovest |
    gzip -c > "$TEMP_FILE"; then

    echo "Backup error: Database dump or compression failed." >&2
    exit 1
fi

if [ ! -s "$TEMP_FILE" ]; then
    echo "Backup error: Compressed output is empty." >&2
    exit 1
fi

if ! gzip -t "$TEMP_FILE"; then
    echo "Backup error: Compressed output failed integrity check." >&2
    exit 1
fi

chmod 600 "$TEMP_FILE"
mv -- "$TEMP_FILE" "$BACKUP_FILE"
TEMP_FILE=""

echo "Backup success: $BACKUP_FILE"

# Prune only after the new archive is successfully committed.
find "$BACKUP_DIR" \
    -maxdepth 1 \
    -type f \
    -name 'neurovest_backup_*.sql.gz' \
    -mtime +7 \
    -delete

echo "Retention cleanup completed."

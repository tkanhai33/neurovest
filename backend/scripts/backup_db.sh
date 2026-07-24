#!/bin/bash
# DOMAIN_LOGIC_V1 automated database backup engine script

BACKUP_DIR="/home/tkanhai/Neurovest/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/neurovest_backup_$TIMESTAMP.sql.gz"

# Create our backup folder on the host machine if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Backup Initialization: Harvesting PostgreSQL container rows..."

# Execute standard compressed pg_dump snapshot over our docker volume space securely
sudo docker exec -t neurovest_postgres pg_dump -U postgres -d neurovest | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Backup Success: Snapshot saved directly onto host disk storage:"
    echo " -> $BACKUP_FILE"

    # Standard cleanup rule retention pass: auto prune snapshot copies older than 7 days
    find "$BACKUP_DIR" -name "neurovest_backup_*.sql.gz" -mtime +7 -delete
    echo "Pruning Phase complete."
else
    echo "Backup Error: Snapshot compilation encountered a critical terminal exception flag."
    exit 1
fi

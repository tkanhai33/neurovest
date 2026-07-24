-- PREVIEW ONLY. DO NOT RUN AUTOMATICALLY.
CREATE TABLE IF NOT EXISTS macro_dataset_registry (
    dataset_id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    country TEXT NOT NULL,
    repo_raw_file TEXT NOT NULL,
    checksum_sha256 TEXT NOT NULL,
    approved BOOLEAN NOT NULL,
    read_only BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

-- Metadata only. Raw workbook remains on disk.

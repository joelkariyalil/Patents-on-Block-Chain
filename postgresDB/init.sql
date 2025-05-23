CREATE TABLE IF NOT EXISTS patents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    region TEXT NOT NULL,
    content_hash TEXT UNIQUE NOT NULL,
    ipfs_cid TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
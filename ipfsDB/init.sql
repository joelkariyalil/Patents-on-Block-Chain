CREATE TABLE ipfs_table (
    ipfs_cid TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    region TEXT NOT NULL,
    content_hash TEXT UNIQUE NOT NULL,
    author TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

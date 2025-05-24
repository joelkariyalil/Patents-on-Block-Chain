CREATE TABLE IF NOT EXISTS patentDB (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    research_sectors TEXT NOT NULL,
    region TEXT NOT NULL,
    content_hash TEXT UNIQUE NOT NULL,
    ipfs_cid TEXT UNIQUE NOT NULL,
    ipfs_url TEXT GENERATED ALWAYS AS ('https://gateway.pinata.cloud/ipfs/' || ipfs_cid) STORED,

    -- 🔐 Simplified Blockchain Fields
    tx_hash TEXT NOT NULL,           -- Transaction hash of the patent submission
    wallet_address TEXT NOT NULL,    -- Ethereum address of the submitter

    author TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- N5 Semantic Memory Schema
-- SQLite database schema for vector storage and search

CREATE TABLE IF NOT EXISTS resources (
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    hash TEXT,
    last_indexed_at DATETIME,
    content_date DATETIME  -- Authoritative date from frontmatter (last_edited or created)
);

CREATE TABLE IF NOT EXISTS blocks (
    id TEXT PRIMARY KEY,
    resource_id TEXT NOT NULL,
    block_type TEXT,
    content TEXT NOT NULL,
    start_line INTEGER,
    end_line INTEGER,
    token_count INTEGER,
    content_date DATETIME,  -- Denormalized from resource for fast search
    FOREIGN KEY(resource_id) REFERENCES resources(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vectors (
    block_id TEXT PRIMARY KEY,
    embedding BLOB NOT NULL,
    FOREIGN KEY(block_id) REFERENCES blocks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tags (
    resource_id TEXT, 
    tag TEXT, 
    PRIMARY KEY (resource_id, tag), 
    FOREIGN KEY(resource_id) REFERENCES resources(id) ON DELETE CASCADE
);

-- Useful indexes for common queries
CREATE INDEX IF NOT EXISTS idx_resources_path ON resources(path);
CREATE INDEX IF NOT EXISTS idx_blocks_resource ON blocks(resource_id);
CREATE INDEX IF NOT EXISTS idx_blocks_date ON blocks(content_date);
CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);


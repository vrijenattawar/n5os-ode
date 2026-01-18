# Semantic Memory System

> **Attribution**: The semantic memory architecture in N5OS Ode is based on foundational work by **[The Fork Project](https://github.com/theforkproject-dev)**. Their [zo-local-memory](https://github.com/theforkproject-dev/zo-local-memory) project established the core patterns for local semantic memory on Zo Computer. We gratefully acknowledge their contribution.

The N5 Semantic Memory system provides AI-native retrieval over your workspace. It transforms documents into searchable vector embeddings, enabling semantic search that understands meaning rather than just keywords.

## Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Your Documents                        │
│  (Markdown, code, notes, transcripts, any text)         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Indexing Pipeline                       │
│  1. Read file content                                    │
│  2. Extract metadata (dates, tags from frontmatter)      │
│  3. Chunk intelligently (markdown-aware)                 │
│  4. Generate embeddings (OpenAI or local)                │
│  5. Store in SQLite + optional HNSW index                │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Search Pipeline                        │
│  1. Convert query to embedding                           │
│  2. Vector similarity search                             │
│  3. Optional: Hybrid with BM25 keyword matching          │
│  4. Optional: Recency weighting                          │
│  5. Optional: Cross-encoder reranking                    │
│  6. Return ranked results                                │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

The semantic memory system requires a few Python packages:

```bash
# Core requirement
pip install numpy

# For OpenAI embeddings (recommended)
pip install openai

# For local embeddings (no API needed)
pip install sentence-transformers

# Optional: Hybrid search with BM25
pip install rank-bm25

# Optional: Cross-encoder reranking
# (included with sentence-transformers)

# Optional: Fast approximate search
pip install hnswlib
```

### Basic Usage

```python
from N5.cognition.n5_memory_client import N5MemoryClient

# Initialize client
client = N5MemoryClient()

# Index a file
client.index_file("/path/to/document.md")

# Search
results = client.search("your query", limit=5)

for r in results:
    print(f"Score: {r['score']:.3f}")
    print(f"Path: {r['path']}")
    print(f"Content: {r['content'][:200]}...")
```

### CLI Usage

```bash
# Search indexed content
python -m N5.cognition.n5_memory_client search "your query" -n 5

# Index a file
python -m N5.cognition.n5_memory_client index /path/to/file.md

# Show statistics
python -m N5.cognition.n5_memory_client stats
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `N5_WORKSPACE` | Root workspace path | `~/workspace` |
| `N5_BRAIN_DB` | Path to SQLite database | `{workspace}/N5/cognition/brain.db` |
| `N5_HNSW_INDEX` | Path to HNSW index | `{workspace}/N5/cognition/brain.hnsw` |
| `N5_EMBEDDING_PROVIDER` | `openai` or `local` | `local` |
| `N5_OPENAI_EMBEDDING_MODEL` | OpenAI model name | `text-embedding-3-large` |
| `OPENAI_API_KEY` | OpenAI API key | (none) |
| `USE_VECTOR_INDEX` | Enable HNSW index | `true` |

### API Key Setup

For OpenAI embeddings, set your API key:

```bash
# Environment variable (preferred)
export OPENAI_API_KEY="sk-..."

# Or create a secret file
echo "sk-..." > ~/workspace/N5/config/secrets/openai.key
```

The client will automatically detect and use the key from either location.

## Embedding Providers

### OpenAI Embeddings (Recommended)

- Model: `text-embedding-3-large`
- Dimensions: 3072
- Best quality for semantic understanding
- Requires API key and internet connection
- Rate limited to ~10 requests/second

### Local Embeddings

- Model: `all-MiniLM-L6-v2` (SentenceTransformers)
- Dimensions: 384
- Runs entirely offline
- Faster indexing for large batches
- Good quality, slightly less nuanced than OpenAI

## Search Features

### Basic Search

```python
results = client.search("machine learning fundamentals", limit=10)
```

### Hybrid Search (Semantic + Keyword)

Combines vector similarity with BM25 keyword matching for better recall:

```python
results = client.search(
    "python async programming",
    use_hybrid=True,
    semantic_weight=0.7,
    bm25_weight=0.3
)
```

### Recency-Weighted Search

Favor more recent documents:

```python
results = client.search(
    "project updates",
    recency_weight=0.3  # 30% recency, 70% relevance
)
```

### Profile-Based Search

Search within specific domains using named profiles:

```python
results = client.search(
    "API design patterns",
    profile="documents"  # Only search in Documents/
)
```

Define custom profiles in the client initialization.

### Reranking

Use a cross-encoder for high-precision reranking:

```python
results = client.search(
    "complex technical query",
    use_reranker=True,
    rerank_top_k=50  # Rerank top 50 candidates
)
```

## Indexing

### Single File

```python
client.index_file("/path/to/document.md", tags=["project", "draft"])
```

### Batch Indexing

```python
from pathlib import Path

workspace = Path("/path/to/workspace")
for md_file in workspace.rglob("*.md"):
    if client.needs_indexing(str(md_file)):
        client.index_file(str(md_file))
```

### Incremental Updates

The client tracks file hashes to avoid re-indexing unchanged content:

```python
if client.needs_indexing(file_path):
    client.index_file(file_path)
```

## Document Chunking

The system uses intelligent chunking to preserve document structure:

### Markdown-Aware Chunking

- Splits at headers (respects document hierarchy)
- Keeps code blocks together
- Preserves bullet list groupings
- Maintains paragraph boundaries

### Frontmatter Extraction

Automatically extracts metadata from YAML frontmatter:

```yaml
---
created: 2024-01-15
last_edited: 2024-01-20
tags: [project, design]
---
```

The `content_date` is used for recency weighting.

## Database Schema

The SQLite database uses four tables:

```sql
-- Indexed files
resources (id, path, hash, last_indexed_at, content_date)

-- Document chunks
blocks (id, resource_id, block_type, content, start_line, end_line, token_count, content_date)

-- Vector embeddings
vectors (block_id, embedding)

-- Resource tags
tags (resource_id, tag)
```

## Performance Tips

### For Large Workspaces

1. **Use HNSW index**: Pre-build an approximate nearest neighbor index for sub-linear search time:

```python
# The client loads the index automatically if present
# Build it separately with hnswlib when you have many documents
```

2. **Batch indexing**: Index files in batches during off-hours

3. **Selective indexing**: Use profiles to limit search scope

### For Quality

1. **Enable hybrid search**: Combines semantic understanding with keyword matching

2. **Use reranking**: Cross-encoder reranking significantly improves precision for complex queries

3. **Tune recency weight**: Adjust based on whether freshness matters for your use case

## Troubleshooting

### "No results found"

- Check that files are indexed: `client.get_stats()`
- Verify the search profile doesn't filter too aggressively
- Try broader queries

### "OpenAI API error"

- Verify `OPENAI_API_KEY` is set correctly
- Check rate limits (built-in throttling helps)
- Fall back to local embeddings if needed

### "Memory errors with large index"

- Use HNSW approximate search instead of brute force
- Index in smaller batches
- Consider increasing system memory

## Integration with N5OS

The semantic memory system integrates with other N5OS components:

- **Prompts**: Search for relevant prompts by capability
- **Meetings**: Find past discussions on a topic
- **Knowledge**: Retrieve contextual information for AI tasks
- **CRM**: Find people and relationship context

Configure profiles in `n5_memory_client.py` to match your workspace structure.

## Further Reading

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Sentence Transformers Documentation](https://www.sbert.net/)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)
- [HNSW Paper](https://arxiv.org/abs/1603.09320)


"""
N5 Semantic Memory Client
=========================
A portable vector database client for semantic search over your workspace.

Features:
- Multi-provider embeddings (OpenAI, local SentenceTransformers)
- Hybrid search (BM25 + semantic similarity)
- Cross-encoder reranking for precision
- HNSW approximate nearest neighbors for scale
- Markdown-aware document chunking
- Recency-weighted retrieval

Packaged for n5OS Ode distribution.
"""

import sqlite3
import os
import datetime
import json
import logging
import hashlib
import re
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
import sys

# ============================================================================
# CONFIGURATION - EDIT THESE PATHS FOR YOUR WORKSPACE
# ============================================================================
# Default paths - override via environment variables or constructor args
DEFAULT_WORKSPACE = os.getenv("N5_WORKSPACE", str(Path.home() / "workspace"))
DEFAULT_BRAIN_DB = os.getenv("N5_BRAIN_DB", str(Path(DEFAULT_WORKSPACE) / "N5/cognition/brain.db"))
DEFAULT_HNSW_INDEX = os.getenv("N5_HNSW_INDEX", str(Path(DEFAULT_WORKSPACE) / "N5/cognition/brain.hnsw"))

# ============================================================================
# OPTIONAL DEPENDENCIES - graceful degradation if not installed
# ============================================================================
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from sentence_transformers import SentenceTransformer
    HAS_SBERT = True
except ImportError:
    HAS_SBERT = False

try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False

try:
    from sentence_transformers import CrossEncoder
    HAS_CROSS_ENCODER = True
except ImportError:
    HAS_CROSS_ENCODER = False

try:
    import hnswlib
    HAS_HNSWLIB = True
except ImportError:
    HAS_HNSWLIB = False

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("n5_memory_client")


class N5MemoryClient:
    """
    Semantic memory client for N5OS.
    
    Example usage:
        client = N5MemoryClient()
        client.index_file("/path/to/document.md")
        results = client.search("your query", limit=5)
    """
    
    def __init__(self, db_path: Optional[str] = None, 
                 ann_index_path: Optional[str] = None,
                 workspace_root: Optional[str] = None):
        """
        Initialize the memory client.
        
        Args:
            db_path: Path to SQLite database (default: N5_BRAIN_DB env or ~/workspace/N5/cognition/brain.db)
            ann_index_path: Path to HNSW index (default: N5_HNSW_INDEX env or ~/workspace/N5/cognition/brain.hnsw)
            workspace_root: Root workspace path for relative paths (default: N5_WORKSPACE env)
        """
        self.workspace_root = workspace_root or DEFAULT_WORKSPACE
        self.db_path = db_path or DEFAULT_BRAIN_DB
        self.ann_index_path = ann_index_path or DEFAULT_HNSW_INDEX
        self._conn = None
        
        # Embedding provider configuration
        self.provider = os.getenv("N5_EMBEDDING_PROVIDER", "local")  # 'local' or 'openai'
        self.openai_model = os.getenv("N5_OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        self.local_model_name = "all-MiniLM-L6-v2"
        
        # Semantic retrieval profiles - customize for your workspace structure
        # These define path prefixes for domain-specific searches
        self.profiles = {
            "documents": {
                "path_prefixes": [
                    f"{self.workspace_root}/Documents/",
                ]
            },
            "notes": {
                "path_prefixes": [
                    f"{self.workspace_root}/Notes/",
                    f"{self.workspace_root}/Knowledge/",
                ]
            },
            "prompts": {
                "path_prefixes": [
                    f"{self.workspace_root}/Prompts/",
                    f"{self.workspace_root}/N5/workflows/",
                ]
            },
        }
        
        self.openai_client = None
        self.local_model = None
        self.cross_encoder = None
        
        # Rate limiting for API calls
        self._last_embedding_time = 0
        self._min_embedding_interval = 0.1  # 100ms between calls
        
        # ANN Index state
        self.use_vector_index = os.getenv("USE_VECTOR_INDEX", "true").lower() == "true"
        self.ann_index = None
        self.ann_block_ids = []  # Ordered list mapping index position → block_id
        
        self._init_provider()
        self._init_db()
        self._init_reranker()
        
        if self.use_vector_index:
            self._load_ann_index()

    def _init_provider(self):
        """Initialize the embedding provider (OpenAI or local)."""
        # Check for API key in environment
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Also check common secret file locations
        secret_paths = [
            Path(self.workspace_root) / "N5/config/secrets/openai.key",
            Path.home() / ".config/openai/api_key",
            Path.home() / ".openai_api_key",
        ]
        
        if not api_key:
            for path in secret_paths:
                if path.exists():
                    api_key = path.read_text().strip()
                    os.environ["OPENAI_API_KEY"] = api_key
                    self.provider = "openai"
                    break
        
        if self.provider == "openai":
            if not HAS_OPENAI:
                LOG.warning("OpenAI provider requested but 'openai' package not installed. Falling back to local.")
                self.provider = "local"
            elif not api_key:
                LOG.warning("OpenAI provider requested but OPENAI_API_KEY not set. Falling back to local.")
                self.provider = "local"
            else:
                self.openai_client = OpenAI()
                LOG.info(f"Using OpenAI Embeddings: {self.openai_model}")
                return

        if self.provider == "local":
            if not HAS_SBERT:
                raise ImportError(
                    "sentence-transformers not installed for local embeddings.\n"
                    "Install with: pip install sentence-transformers\n"
                    "Or set OPENAI_API_KEY for cloud embeddings."
                )
            self.local_model = SentenceTransformer(self.local_model_name)
            LOG.info(f"Using Local Embeddings: {self.local_model_name}")

    def _init_db(self):
        """Initialize SQLite database with schema."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL UNIQUE,
                hash TEXT,
                last_indexed_at DATETIME,
                content_date DATETIME
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                id TEXT PRIMARY KEY,
                resource_id TEXT NOT NULL,
                block_type TEXT,
                content TEXT NOT NULL,
                start_line INTEGER,
                end_line INTEGER,
                token_count INTEGER,
                content_date DATETIME,
                FOREIGN KEY(resource_id) REFERENCES resources(id) ON DELETE CASCADE
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                block_id TEXT PRIMARY KEY,
                embedding BLOB NOT NULL,
                FOREIGN KEY(block_id) REFERENCES blocks(id) ON DELETE CASCADE
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                resource_id TEXT, 
                tag TEXT, 
                PRIMARY KEY (resource_id, tag), 
                FOREIGN KEY(resource_id) REFERENCES resources(id) ON DELETE CASCADE
            )
        """)
        self._conn.commit()

    def _init_reranker(self):
        """Initialize cross-encoder for reranking if available."""
        if HAS_CROSS_ENCODER:
            try:
                self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
                LOG.info("Reranker initialized: cross-encoder/ms-marco-MiniLM-L-6-v2")
            except Exception as e:
                LOG.warning(f"Could not load cross-encoder: {e}")
                self.cross_encoder = None

    def _load_ann_index(self) -> bool:
        """Load the pre-built HNSW index if available."""
        if not HAS_HNSWLIB:
            LOG.warning("hnswlib not installed, falling back to brute-force search")
            return False

        index_path = self.ann_index_path
        mapping_path = self.ann_index_path + ".ids"

        if not os.path.exists(index_path) or not os.path.exists(mapping_path):
            LOG.info("ANN index not found, will use brute-force search")
            return False

        try:
            # Load ID mapping first to get dimensions
            with open(mapping_path, 'r') as f:
                self.ann_block_ids = json.load(f)

            # Determine embedding dimension
            dim = 3072 if self.provider == "openai" else 384
            
            self.ann_index = hnswlib.Index(space='cosine', dim=dim)
            self.ann_index.load_index(index_path)
            LOG.info(f"Loaded ANN index with {len(self.ann_block_ids)} vectors")
            return True
        except Exception as e:
            LOG.error(f"Failed to load ANN index: {e}")
            self.ann_index = None
            return False

    def _get_db(self) -> sqlite3.Connection:
        """Get database connection, reconnecting if needed."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
        return self._conn

    def get_embedding(self, text: str) -> bytes:
        """Generate embedding for text, respecting rate limits."""
        # Rate limiting
        now = time.time()
        elapsed = now - self._last_embedding_time
        if elapsed < self._min_embedding_interval:
            time.sleep(self._min_embedding_interval - elapsed)
        self._last_embedding_time = time.time()
        
        if self.provider == "openai" and self.openai_client:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.openai_model
            )
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
        else:
            embedding = self.local_model.encode(text, convert_to_numpy=True).astype(np.float32)
        
        return embedding.tobytes()

    def _cosine_similarity(self, a: bytes, b: bytes) -> float:
        """Compute cosine similarity between two embedding blobs."""
        vec_a = np.frombuffer(a, dtype=np.float32)
        vec_b = np.frombuffer(b, dtype=np.float32)
        dot = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer for BM25 - lowercase and split on non-alphanumeric."""
        return re.findall(r'\w+', text.lower())

    def _compute_bm25_scores(self, query: str, documents: List[Dict]) -> Dict[str, float]:
        """Compute BM25 scores for documents given a query."""
        if not HAS_BM25 or not documents:
            return {}
        
        tokenized_docs = [self._tokenize(doc['content']) for doc in documents]
        tokenized_query = self._tokenize(query)
        
        if not tokenized_query:
            return {}
        
        bm25 = BM25Okapi(tokenized_docs)
        scores = bm25.get_scores(tokenized_query)
        
        # Normalize to [0, 1]
        max_score = max(scores) if max(scores) > 0 else 1
        return {doc['block_id']: score / max_score for doc, score in zip(documents, scores)}

    def search(self, query: str, limit: int = 10, tag_filter: Optional[str] = None,
               recency_weight: float = 0.2, use_hybrid: bool = True,
               semantic_weight: float = 0.7, bm25_weight: float = 0.3,
               use_reranker: bool = False, rerank_top_k: int = 50,
               profile: Optional[str] = None,
               metadata_filters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Semantic search with optional hybrid BM25 and reranking.

        Args:
            query: Search query string
            limit: Number of results to return
            tag_filter: Filter by tag
            recency_weight: Weight for recency boosting (0-1)
            use_hybrid: Enable BM25 + semantic hybrid search
            semantic_weight: Weight for semantic similarity in hybrid mode
            bm25_weight: Weight for BM25 scores in hybrid mode
            use_reranker: Enable cross-encoder reranking
            rerank_top_k: Number of candidates to rerank
            profile: Named retrieval profile (filters by path prefix)
            metadata_filters: Dict of metadata filters

        Returns:
            List of result dicts with keys: block_id, resource_id, content, path, score, etc.
        """
        query_embedding = self.get_embedding(query)
        
        # Build path filter from profile
        path_prefixes = None
        if profile and profile in self.profiles:
            path_prefixes = self.profiles[profile].get("path_prefixes", [])
        
        # Get initial candidates
        cursor = self._get_db().cursor()
        
        # Build query with optional filters
        sql = """
            SELECT b.id, b.resource_id, b.content, b.block_type, b.content_date,
                   r.path, v.embedding
            FROM blocks b
            JOIN resources r ON b.resource_id = r.id
            JOIN vectors v ON b.id = v.block_id
            WHERE 1=1
        """
        params = []
        
        if tag_filter:
            sql += " AND EXISTS (SELECT 1 FROM tags t WHERE t.resource_id = r.id AND t.tag = ?)"
            params.append(tag_filter)
            
        if path_prefixes:
            path_conditions = " OR ".join(["r.path LIKE ?" for _ in path_prefixes])
            sql += f" AND ({path_conditions})"
            params.extend([p + "%" for p in path_prefixes])
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        if not rows:
            return []
        
        # Compute similarities
        results = []
        documents_for_bm25 = []
        
        for row in rows:
            block_id, resource_id, content, block_type, content_date, path, embedding = row
            
            similarity = self._cosine_similarity(query_embedding, embedding)
            
            result = {
                'block_id': block_id,
                'resource_id': resource_id,
                'content': content,
                'block_type': block_type,
                'content_date': content_date,
                'path': path,
                'semantic_score': similarity,
            }
            results.append(result)
            documents_for_bm25.append({'block_id': block_id, 'content': content})
        
        # Hybrid scoring with BM25
        if use_hybrid and HAS_BM25:
            bm25_scores = self._compute_bm25_scores(query, documents_for_bm25)
            for result in results:
                bm25_score = bm25_scores.get(result['block_id'], 0)
                result['bm25_score'] = bm25_score
                result['score'] = (
                    semantic_weight * result['semantic_score'] +
                    bm25_weight * bm25_score
                )
        else:
            for result in results:
                result['score'] = result['semantic_score']
        
        # Apply recency boost
        if recency_weight > 0:
            now = datetime.datetime.now()
            for result in results:
                if result.get('content_date'):
                    try:
                        date = datetime.datetime.fromisoformat(result['content_date'].replace('Z', '+00:00'))
                        days_old = (now - date.replace(tzinfo=None)).days
                        recency_score = max(0, 1 - (days_old / 365))  # Linear decay over 1 year
                        result['score'] = (1 - recency_weight) * result['score'] + recency_weight * recency_score
                    except:
                        pass
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Optional reranking
        if use_reranker and self.cross_encoder:
            top_candidates = results[:rerank_top_k]
            pairs = [(query, r['content']) for r in top_candidates]
            rerank_scores = self.cross_encoder.predict(pairs)
            for i, score in enumerate(rerank_scores):
                top_candidates[i]['rerank_score'] = float(score)
                top_candidates[i]['score'] = float(score)
            top_candidates.sort(key=lambda x: x['score'], reverse=True)
            results = top_candidates
        
        return results[:limit]

    def index_file(self, file_path: str, tags: Optional[List[str]] = None,
                   content_date: Optional[str] = None) -> None:
        """
        Index a file into the semantic memory.
        
        Args:
            file_path: Path to the file to index
            tags: Optional list of tags to apply
            content_date: Optional date string (ISO format) for recency weighting
        """
        if not os.path.exists(file_path):
            LOG.warning(f"File not found: {file_path}")
            return
            
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        resource_id = hashlib.md5(file_path.encode('utf-8')).hexdigest()
        
        # Extract date from frontmatter if not provided
        if not content_date:
            frontmatter_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                fm = frontmatter_match.group(1)
                date_match = re.search(r'(?:last_edited|created):\s*(\d{4}-\d{2}-\d{2})', fm)
                if date_match:
                    content_date = date_match.group(1)
        
        cursor = self._conn.cursor()
        
        # Upsert resource
        cursor.execute("DELETE FROM resources WHERE path = ? OR id = ?", (file_path, resource_id))
        cursor.execute("""
            INSERT INTO resources (id, path, hash, last_indexed_at, content_date)
            VALUES (?, ?, ?, datetime('now'), ?)
        """, (resource_id, file_path, file_hash, content_date))
        
        # Clear old blocks
        cursor.execute("DELETE FROM vectors WHERE block_id IN (SELECT id FROM blocks WHERE resource_id = ?)", (resource_id,))
        cursor.execute("DELETE FROM blocks WHERE resource_id = ?", (resource_id,))
        
        # Chunk and embed
        chunks = self._chunk_content(content)
        
        for i, chunk in enumerate(chunks):
            block_id = f"{resource_id}_{i}"
            embedding_blob = self.get_embedding(chunk['text'])
            
            cursor.execute("""
                INSERT INTO blocks (id, resource_id, block_type, content, start_line, end_line, token_count, content_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (block_id, resource_id, 'text', chunk['text'], chunk['start'], chunk['end'], len(chunk['text'])//4, content_date))
            
            cursor.execute("""
                INSERT INTO vectors (block_id, embedding)
                VALUES (?, ?)
            """, (block_id, embedding_blob))
        
        # Apply tags
        if tags:
            for tag in tags:
                cursor.execute("INSERT OR IGNORE INTO tags (resource_id, tag) VALUES (?, ?)", (resource_id, tag))
        
        self._conn.commit()
        LOG.info(f"Indexed {file_path}: {len(chunks)} blocks")

    def _chunk_content(self, content: str, chunk_size: int = 1000) -> List[Dict]:
        """Smart chunker - markdown-aware with fallback to line-based."""
        has_headers = bool(re.search(r'^#{1,6}\s', content, re.MULTILINE))
        has_code_blocks = '```' in content
        has_bullets = bool(re.search(r'^[\s]*[-*•]\s', content, re.MULTILINE))
        
        if has_headers or has_code_blocks or has_bullets:
            return self._chunk_content_markdown(content, max_chunk_size=int(chunk_size * 1.5))
        
        return self._chunk_content_simple(content, chunk_size)

    def _chunk_content_markdown(self, content: str, max_chunk_size: int = 1500,
                                min_chunk_size: int = 200) -> List[Dict]:
        """Markdown-aware chunker that respects document structure."""
        chunks = []
        lines = content.split('\n')
        
        current_chunk_lines = []
        current_chunk_size = 0
        start_line = 1
        in_code_block = False
        
        def flush_chunk(end_idx: int):
            nonlocal current_chunk_lines, current_chunk_size, start_line
            if current_chunk_lines:
                text = '\n'.join(current_chunk_lines)
                if len(text.strip()) >= min_chunk_size // 2:
                    chunks.append({
                        'text': text,
                        'start': start_line,
                        'end': end_idx,
                        'type': 'text'
                    })
            current_chunk_lines = []
            current_chunk_size = 0
        
        for i, line in enumerate(lines, 1):
            line_len = len(line)
            
            # Track code blocks
            if line.strip().startswith('```'):
                if not in_code_block:
                    if current_chunk_size > max_chunk_size * 0.7:
                        flush_chunk(i - 1)
                        start_line = i
                    in_code_block = True
                else:
                    in_code_block = False
                current_chunk_lines.append(line)
                current_chunk_size += line_len
                continue
            
            if in_code_block:
                current_chunk_lines.append(line)
                current_chunk_size += line_len
                continue
            
            is_header = re.match(r'^#{1,6}\s', line)
            should_split = False
            
            if is_header and current_chunk_size > min_chunk_size:
                should_split = True
            elif current_chunk_size + line_len > max_chunk_size:
                if is_header or line.strip() == '' or not line.strip().startswith(('-', '*', '1.', '•')):
                    should_split = True
            
            if should_split and current_chunk_lines:
                flush_chunk(i - 1)
                start_line = i
            
            current_chunk_lines.append(line)
            current_chunk_size += line_len
        
        flush_chunk(len(lines))
        return chunks

    def _chunk_content_simple(self, content: str, chunk_size: int = 1000) -> List[Dict]:
        """Simple line-based chunking fallback."""
        lines = content.splitlines()
        chunks = []
        current_chunk = []
        current_len = 0
        start_line = 1
        
        for i, line in enumerate(lines):
            line_len = len(line)
            if current_len + line_len > chunk_size and current_chunk:
                text = "\n".join(current_chunk)
                chunks.append({
                    'text': text,
                    'start': start_line,
                    'end': start_line + len(current_chunk) - 1
                })
                current_chunk = []
                current_len = 0
                start_line = i + 1
            
            current_chunk.append(line)
            current_len += line_len
        
        if current_chunk:
            text = "\n".join(current_chunk)
            chunks.append({
                'text': text,
                'start': start_line,
                'end': len(lines)
            })
        
        return chunks

    def needs_indexing(self, file_path: str) -> bool:
        """Check if a file needs (re)indexing based on content hash."""
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        current_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        cursor = self._conn.cursor()
        cursor.execute("SELECT hash FROM resources WHERE path = ?", (file_path,))
        row = cursor.fetchone()
        
        return row is None or row[0] != current_hash

    def delete_resource(self, file_path: str) -> bool:
        """Remove a file from the index."""
        resource_id = hashlib.md5(file_path.encode('utf-8')).hexdigest()
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM vectors WHERE block_id IN (SELECT id FROM blocks WHERE resource_id = ?)", (resource_id,))
        cursor.execute("DELETE FROM blocks WHERE resource_id = ?", (resource_id,))
        cursor.execute("DELETE FROM tags WHERE resource_id = ?", (resource_id,))
        cursor.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
        self._conn.commit()
        return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, int]:
        """Get index statistics."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM resources")
        resources = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM blocks")
        blocks = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM vectors")
        vectors = cursor.fetchone()[0]
        return {
            'resources': resources,
            'blocks': blocks,
            'vectors': vectors,
            'provider': self.provider,
            'has_ann_index': self.ann_index is not None,
        }

    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


# ============================================================================
# CLI INTERFACE
# ============================================================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="N5 Semantic Memory CLI")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search indexed content')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('-n', '--limit', type=int, default=5, help='Number of results')
    search_parser.add_argument('--profile', help='Named retrieval profile')
    search_parser.add_argument('--hybrid', action='store_true', help='Use hybrid search')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index a file')
    index_parser.add_argument('path', help='File path to index')
    index_parser.add_argument('--tags', nargs='+', help='Tags to apply')
    
    # Stats command
    subparsers.add_parser('stats', help='Show index statistics')
    
    args = parser.parse_args()
    
    client = N5MemoryClient()
    
    if args.command == 'search':
        results = client.search(
            args.query,
            limit=args.limit,
            profile=args.profile,
            use_hybrid=args.hybrid
        )
        for i, r in enumerate(results, 1):
            print(f"\n--- Result {i} (score: {r['score']:.3f}) ---")
            print(f"Path: {r['path']}")
            print(f"Content: {r['content'][:200]}...")
    
    elif args.command == 'index':
        client.index_file(args.path, tags=args.tags)
        print(f"Indexed: {args.path}")
    
    elif args.command == 'stats':
        stats = client.get_stats()
        print(json.dumps(stats, indent=2))
    
    else:
        parser.print_help()
    
    client.close()


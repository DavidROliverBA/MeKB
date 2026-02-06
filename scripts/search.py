#!/usr/bin/env python3
"""
Hybrid Search Engine for MeKB
Supports FTS5 BM25, optional vector similarity, and hybrid fusion.

Usage:
    python3 scripts/search.py "search query"
    python3 scripts/search.py "query" --type Concept
    python3 scripts/search.py "query" --limit 20
    python3 scripts/search.py "query" --explain
    python3 scripts/search.py "query" --json

Three search tiers:
    1. FTS5 BM25 - always available (requires search.db)
    2. Vector similarity - when embeddings.json exists
    3. Hybrid fusion (70/30 BM25/vector) - when both exist

Dependencies: Python 3.9+ (stdlib only)
Optional: sentence-transformers (for vector search)
"""

import argparse
import json
import math
import os
import re
import sqlite3
import sys
from pathlib import Path


def find_vault_root():
    """Find the vault root by looking for .mekb/ or CLAUDE.md."""
    path = Path.cwd()
    while path != path.parent:
        if (path / ".mekb").is_dir() or (path / "CLAUDE.md").is_file():
            return path
        path = path.parent
    return Path.cwd()


def fts5_search(db_path, query, note_type=None, limit=20, exclude_classifications=None):
    """Search using SQLite FTS5 with BM25 ranking."""
    if not db_path.exists():
        return []

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # Escape FTS5 special characters and build query
    fts_query = sanitise_fts_query(query)
    if not fts_query:
        conn.close()
        return []

    sql = """
        SELECT n.path, n.title, n.type, n.tags, n.classification,
               n.created, n.status, n.verified,
               f.rank AS bm25_rank,
               snippet(fts_notes, 3, '>>>', '<<<', '...', 40) AS snippet
        FROM fts_notes f
        JOIN notes n ON n.id = f.rowid
        WHERE fts_notes MATCH ?
    """
    params = [fts_query]

    if note_type:
        sql += " AND n.type = ?"
        params.append(note_type)

    if exclude_classifications:
        placeholders = ", ".join("?" * len(exclude_classifications))
        sql += f" AND COALESCE(n.classification, 'personal') NOT IN ({placeholders})"
        params.extend(exclude_classifications)

    sql += " ORDER BY f.rank LIMIT ?"
    params.append(limit)

    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError:
        # FTS5 query syntax error - fall back to simple term search
        simple_query = re.sub(r'[^\w\s]', '', query)
        if simple_query:
            params[0] = simple_query
            try:
                rows = conn.execute(sql, params).fetchall()
            except sqlite3.OperationalError:
                rows = []
        else:
            rows = []

    results = []
    for row in rows:
        results.append({
            "path": row["path"],
            "title": row["title"],
            "type": row["type"],
            "tags": row["tags"],
            "classification": row["classification"],
            "created": row["created"],
            "status": row["status"],
            "verified": row["verified"],
            "bm25_score": abs(row["bm25_rank"]) if row["bm25_rank"] else 0,
            "snippet": clean_snippet(row["snippet"]),
            "source": "fts5",
        })

    conn.close()
    return results


def sanitise_fts_query(query):
    """Sanitise a user query for FTS5 MATCH syntax."""
    # Handle quoted phrases
    if query.startswith('"') and query.endswith('"'):
        return query

    # Remove FTS5 operators that could cause syntax errors
    query = re.sub(r'[{}()\[\]^~]', '', query)

    # Split into terms and rejoin
    terms = query.split()
    if not terms:
        return ""

    # If multiple terms, search for all of them
    if len(terms) > 1:
        # Use implicit AND (space-separated in FTS5)
        return " ".join(t for t in terms if t.upper() not in ("AND", "OR", "NOT", "NEAR"))

    return terms[0]


def clean_snippet(snippet):
    """Clean FTS5 snippet markers for display."""
    if not snippet:
        return ""
    # Replace >>> and <<< with display markers
    return snippet.replace(">>>", "**").replace("<<<", "**")


def vector_search(embeddings_path, query, limit=20):
    """Search using pre-computed vector embeddings with cosine similarity."""
    if not embeddings_path.exists():
        return []

    try:
        with open(embeddings_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

    embeddings = data.get("embeddings", {})
    if not embeddings:
        return []

    # Try to compute query embedding
    query_embedding = compute_query_embedding(query, data.get("model"))
    if not query_embedding:
        return []

    # Compute cosine similarity for each note
    scored = []
    for path, entry in embeddings.items():
        vec = entry.get("vector", [])
        if not vec:
            continue
        similarity = cosine_similarity(query_embedding, vec)
        scored.append({
            "path": path,
            "title": entry.get("title", Path(path).stem),
            "type": entry.get("type"),
            "vector_score": similarity,
            "source": "vector",
        })

    # Sort by similarity descending
    scored.sort(key=lambda x: x["vector_score"], reverse=True)
    return scored[:limit]


def compute_query_embedding(query, model_name=None):
    """Compute embedding for a query string. Returns None if not available."""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model_name or "all-MiniLM-L6-v2")
        embedding = model.encode(query).tolist()
        return embedding
    except ImportError:
        return None
    except Exception:
        return None


def cosine_similarity(vec_a, vec_b):
    """Compute cosine similarity between two vectors."""
    if len(vec_a) != len(vec_b) or not vec_a:
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def load_graph_degrees(vault_root):
    """Load node degree data from graph.json for centrality boosting."""
    graph_path = vault_root / ".mekb" / "graph.json"
    if not graph_path.exists():
        return {}

    try:
        with open(graph_path, "r") as f:
            data = json.load(f)
        degrees = {}
        nodes = data.get("nodes", {})
        if not nodes:
            return {}
        max_degree = max((n.get("degree", 0) for n in nodes.values()), default=1)
        if max_degree == 0:
            max_degree = 1
        for path, node in nodes.items():
            degrees[path] = node.get("degree", 0) / max_degree  # Normalise 0-1
        return degrees
    except (json.JSONDecodeError, IOError):
        return {}


def hybrid_search(fts_results, vector_results, graph_degrees=None,
                  fts_weight=0.7, vector_weight=0.3, graph_weight=0.1):
    """Fuse FTS5 and vector results using reciprocal rank fusion.

    When graph_degrees is available, applies a centrality boost:
    hub notes (more connections) get a small ranking advantage.
    Weights are renormalised to sum to 1.0 when graph is present.
    """
    # Renormalise weights when graph is present
    if graph_degrees:
        total = fts_weight + vector_weight + graph_weight
        fts_weight = fts_weight / total
        vector_weight = vector_weight / total
        graph_weight = graph_weight / total
    else:
        graph_weight = 0

    # Build score maps using reciprocal rank fusion (RRF)
    k = 60  # RRF constant
    scores = {}

    for rank, result in enumerate(fts_results):
        path = result["path"]
        scores[path] = scores.get(path, {"data": result, "fts_rrf": 0, "vec_rrf": 0})
        scores[path]["fts_rrf"] = 1.0 / (k + rank + 1)
        scores[path]["data"] = result

    for rank, result in enumerate(vector_results):
        path = result["path"]
        if path not in scores:
            scores[path] = {"data": result, "fts_rrf": 0, "vec_rrf": 0}
        scores[path]["vec_rrf"] = 1.0 / (k + rank + 1)
        # Merge vector score into data
        scores[path]["data"]["vector_score"] = result.get("vector_score", 0)

    # Compute weighted fusion score with optional graph boost
    fused = []
    for path, entry in scores.items():
        graph_score = graph_degrees.get(path, 0) if graph_degrees else 0
        fusion_score = (
            (fts_weight * entry["fts_rrf"]) +
            (vector_weight * entry["vec_rrf"]) +
            (graph_weight * graph_score * (1.0 / (k + 1)))  # Scale graph to RRF range
        )
        data = entry["data"]
        data["fusion_score"] = fusion_score
        data["graph_score"] = graph_score
        data["source"] = "hybrid"
        fused.append(data)

    fused.sort(key=lambda x: x["fusion_score"], reverse=True)
    return fused


def format_results(results, explain=False):
    """Format search results for display."""
    if not results:
        print("No results found.")
        return

    print(f"\nFound {len(results)} result(s):\n")

    for i, r in enumerate(results, 1):
        note_type = r.get("type") or "unknown"
        title = r.get("title") or r["path"]
        path = r["path"]

        print(f"  {i}. [{note_type}] {title}")
        print(f"     {path}")

        if r.get("snippet"):
            # Truncate long snippets
            snippet = r["snippet"][:200]
            print(f"     {snippet}")

        if explain:
            source = r.get("source", "fts5")
            if source == "hybrid":
                parts = [f"fusion={r.get('fusion_score', 0):.4f}",
                         f"bm25={r.get('bm25_score', 0):.4f}",
                         f"vector={r.get('vector_score', 0):.4f}"]
                if r.get("graph_score"):
                    parts.append(f"graph={r.get('graph_score', 0):.2f}")
                print(f"     Score: {' '.join(parts)}")
            elif source == "fts5":
                print(f"     Score: bm25={r.get('bm25_score', 0):.4f}")
            elif source == "vector":
                print(f"     Score: vector={r.get('vector_score', 0):.4f}")

            if r.get("tags"):
                print(f"     Tags: {r['tags']}")
            if r.get("classification") and r["classification"] != "personal":
                print(f"     Classification: {r['classification']}")

        print()


def format_json(results):
    """Output results as JSON."""
    output = []
    for r in results:
        output.append({
            "path": r["path"],
            "title": r.get("title"),
            "type": r.get("type"),
            "score": r.get("fusion_score") or r.get("bm25_score") or r.get("vector_score", 0),
            "snippet": r.get("snippet"),
            "source": r.get("source"),
        })
    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Search MeKB vault")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--type", "-t", dest="note_type", help="Filter by note type")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("--explain", "-e", action="store_true", help="Show scoring details")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--vault", help="Vault root directory")
    parser.add_argument("--fts-only", action="store_true", help="Use FTS5 search only")
    parser.add_argument("--vector-only", action="store_true", help="Use vector search only")
    args = parser.parse_args()

    vault_root = Path(args.vault) if args.vault else find_vault_root()
    db_path = vault_root / ".mekb" / "search.db"
    embeddings_path = vault_root / ".mekb" / "embeddings.json"

    # Always exclude secret from search output
    exclude_cls = ["secret"]

    fts_results = []
    vec_results = []

    # Tier 1: FTS5 BM25 (always available if index exists)
    if not args.vector_only:
        if not db_path.exists():
            print("No search index found. Run: python3 scripts/build-index.py", file=sys.stderr)
            if args.vector_only or not embeddings_path.exists():
                sys.exit(1)
        else:
            fts_results = fts5_search(
                db_path, args.query,
                note_type=args.note_type,
                limit=args.limit,
                exclude_classifications=exclude_cls,
            )

    # Tier 2: Vector similarity (when embeddings exist)
    if not args.fts_only and embeddings_path.exists():
        vec_results = vector_search(embeddings_path, args.query, limit=args.limit)

    # Load graph centrality data for ranking boost
    graph_degrees = load_graph_degrees(vault_root)

    # Tier 3: Hybrid fusion (when both exist)
    if fts_results and vec_results and not args.fts_only and not args.vector_only:
        results = hybrid_search(fts_results, vec_results, graph_degrees)[:args.limit]
    elif fts_results:
        results = fts_results
    elif vec_results:
        results = vec_results
    else:
        results = []

    if args.json:
        format_json(results)
    else:
        format_results(results, explain=args.explain)


if __name__ == "__main__":
    main()

"""
=========================================================
File: hybrid_search.py
=========================================================

Purpose
-------
This file combines multiple retrieval techniques to
improve search quality.

Current Retrieval Methods
-------------------------
1. BM25 Search
   - Finds exact keyword matches.
   - Good when query words are present in document.

2. Semantic Search
   - Uses vector embeddings.
   - Finds similar meaning even if exact words are absent.

Instead of simply appending the two result lists,
we use Reciprocal Rank Fusion (RRF).

Why RRF?
--------
Suppose:

BM25

1. Page 5
2. Page 8
3. Page 2

Semantic Search

1. Page 8
2. Page 4
3. Page 5

Simple Merge

5
8
2
4

This does not consider ranking quality.

RRF calculates a score for every chunk based on
its position in every ranking list.

Final Ranking

1. Page 5
2. Page 8
3. Page 4
4. Page 2

This gives much better retrieval performance.

Used By
-------
chat.py

Flow
----

User Query
      │
      ▼
BM25 Search
      │
Semantic Search
      │
      ▼
Reciprocal Rank Fusion
      │
      ▼
Top Ranked Chunks

=========================================================
"""

from app.services.bm25_service import bm25_search
from app.services.search_service import semantic_search
from app.services.rrf import reciprocal_rank_fusion

from app.services.reranker_service import rerank_documents


def hybrid_search(query, db, limit=5):
    """
    Hybrid Retrieval using BM25 + Semantic Search.

    Parameters
    ----------
    query : str
        User question.

    db
        SQLAlchemy database session.

    limit : int
        Number of final chunks required.

    Returns
    -------
    List[Chunk]
        Top ranked chunks after RRF.
    """

    # ----------------------------------------
    # BM25 Keyword Search
    # Returns:
    # [(chunk, score), (chunk, score), ...]
    # ----------------------------------------

    bm25_results = bm25_search(query, db, limit=20)

    # Extract only Chunk objects
    bm25_chunks = [chunk for chunk, score in bm25_results]

    print("BM25 Results :", len(bm25_chunks))

    # ----------------------------------------
    # Semantic Search
    # Returns:
    # [chunk, chunk, chunk]
    # ----------------------------------------

    semantic_chunks = semantic_search(query, db, limit=20)

    print("Semantic Results :", len(semantic_chunks))

    # ----------------------------------------
    # Reciprocal Rank Fusion
    # ----------------------------------------

    fused_results = reciprocal_rank_fusion(bm25_chunks, semantic_chunks)

    print("RRF Results :", len(fused_results))

    # ----------------------------------------
    # Return top chunks
    # ----------------------------------------

    reranked_results = rerank_documents(query, fused_results[:20], top_k=limit)

    return reranked_results

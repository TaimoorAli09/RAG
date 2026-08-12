"""
=========================================================
File: hybrid_search.py
=========================================================

Purpose
-------
Combines BM25 and Semantic Search using Reciprocal
Rank Fusion (RRF).

Pipeline:

BM25
  +
Semantic Search
  ↓
RRF
  ↓
Fused Chunks

Reranking is handled separately by the LangGraph
Rerank Node.

=========================================================
"""

from app.services.bm25_service import bm25_search
from app.services.search_service import semantic_search
from app.services.rrf import reciprocal_rank_fusion


def hybrid_search(query, db, limit=20):

    # -----------------------------------------
    # BM25 Search
    # -----------------------------------------

    bm25_results = bm25_search(
        query,
        db,
        limit=limit
    )

    bm25_chunks = [
        chunk
        for chunk, score in bm25_results
    ]

    print(
        "BM25 Results:",
        len(bm25_chunks)
    )

    # -----------------------------------------
    # Semantic Search
    # -----------------------------------------

    semantic_chunks = semantic_search(
        query,
        db,
        limit=limit
    )

    print(
        "Semantic Results:",
        len(semantic_chunks)
    )

    # -----------------------------------------
    # Reciprocal Rank Fusion
    # -----------------------------------------

    fused_results = reciprocal_rank_fusion(
        bm25_chunks,
        semantic_chunks
    )

    print(
        "RRF Results:",
        len(fused_results)
    )

    # -----------------------------------------
    # Return fused chunks
    #
    # Reranker will be applied later
    # by LangGraph.
    # -----------------------------------------

    return fused_results[:limit]
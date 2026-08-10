"""
=========================================================
File: retrieve.py
=========================================================

Purpose
-------
Retrieves relevant document chunks using the existing
hybrid search pipeline.

Retrieval:

Query
  ↓
BM25
  +
Semantic Search
  ↓
RRF
  ↓
Reranker
  ↓
Relevant Chunks
=========================================================
"""

from app.services.hybrid_search import hybrid_search


def retrieve_node(state, runtime):

    # -----------------------------------------
    # Get query
    # -----------------------------------------

    query = state["query"]

    # -----------------------------------------
    # Get database session
    # -----------------------------------------

    db = runtime.context["db"]

    print("\n==============================")
    print("RETRIEVE NODE")
    print("==============================")

    print("Query:", query)

    # -----------------------------------------
    # Hybrid Retrieval
    # -----------------------------------------

    chunks = hybrid_search(
        query,
        db,
        limit=5
    )

    print(
        "Retrieved chunks:",
        len(chunks)
    )

    # -----------------------------------------
    # Update state
    # -----------------------------------------

    return {
        "retrieved_chunks": chunks
    }
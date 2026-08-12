"""
=========================================================
File: rerank.py
=========================================================

Reranking Node

Takes chunks retrieved by BM25 + Semantic + RRF
and applies the Cross Encoder reranker.

20 candidates
      ↓
Cross Encoder
      ↓
Top 5
=========================================================
"""

from app.services.reranker_service import rerank_documents


def rerank_node(state):

    query = state["query"]

    chunks = state["retrieved_chunks"]

    print("\n==============================")
    print("RERANK NODE")
    print("==============================")

    print("Candidates:", len(chunks))

    reranked_chunks = rerank_documents(query, chunks, top_k=5)

    print("Reranked:", len(reranked_chunks))

    return {"reranked_chunks": reranked_chunks}

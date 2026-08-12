"""
=========================================================
File: retrieve.py
=========================================================

Retrieval Node

BM25
+
Semantic Search
+
RRF

Returns candidate chunks for reranking.
=========================================================
"""

from app.services.hybrid_search import hybrid_search


def retrieve_node(state, runtime):

    query = state["query"]

    db = runtime.context["db"]

    print("\n==============================")
    print("RETRIEVE NODE")
    print("==============================")

    print("Query:", query)

    chunks = hybrid_search(
        query,
        db,
        limit=20
    )

    print(
        "Retrieved chunks:",
        len(chunks)
    )

    return {
        "retrieved_chunks": chunks
    }
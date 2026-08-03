from app.services.bm25_service import bm25_search
from app.services.search_service import semantic_search


def hybrid_search(query, db, limit=5):

    bm25_results = bm25_search(query, db, limit)
    print("BM25 RESULTS")
    semantic_results = semantic_search(query, db, limit)

    final = []

    # BM25 results add

    for chunk, score in bm25_results:

        final.append(chunk)

    # semantic results add
    print("SEMANTIC RESULTS")
    for chunk in semantic_results:

        if chunk not in final:

            final.append(chunk)

    return final[:limit]

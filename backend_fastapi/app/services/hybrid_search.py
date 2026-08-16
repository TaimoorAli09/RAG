from langsmith import traceable

from app.services.bm25_service import bm25_search
from app.services.search_service import semantic_search
from app.services.rrf import reciprocal_rank_fusion
from app.services.reranker_service import rerank_documents


@traceable(name="hybrid_search")
def hybrid_search(query, db, limit=5):

    # =========================================
    # 1. Candidate Retrieval
    # =========================================

    candidate_limit = 20

    # -----------------------------------------
    # BM25
    # -----------------------------------------

    bm25_results = bm25_search(
        query,
        db,
        limit=candidate_limit
    )

    bm25_chunks = [
        chunk
        for chunk, score in bm25_results
    ]

    print("BM25 Results:", len(bm25_chunks))

    # -----------------------------------------
    # Semantic Search
    # -----------------------------------------

    semantic_chunks = semantic_search(
        query,
        db,
        limit=candidate_limit
    )

    print("Semantic Results:", len(semantic_chunks))

    # =========================================
    # 2. RRF
    # =========================================

    fused_results = reciprocal_rank_fusion(
        bm25_chunks,
        semantic_chunks
    )

    print("RRF Results:", len(fused_results))

    # =========================================
    # 3. Reranking
    # =========================================

    rerank_candidates = min(
        len(fused_results),
        20
    )

    reranked_results = rerank_documents(
        query=query,
        documents=fused_results,
        top_k=limit,
        candidate_limit=rerank_candidates
    )

    print(
        "Reranker Candidates:",
        rerank_candidates
    )

    print(
        "Reranked Results:",
        len(reranked_results)
    )

    return reranked_results
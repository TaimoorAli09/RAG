from sentence_transformers import CrossEncoder


# =========================================
# Load Reranker Model
# =========================================

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


# =========================================
# Rerank Documents
# =========================================

def rerank_documents(
    query,
    documents,
    top_k=5,
    candidate_limit=None
):

    # -----------------------------------------
    # Candidate selection
    # -----------------------------------------

    if candidate_limit is not None:
        documents = documents[:candidate_limit]

    if not documents:
        return []

    # -----------------------------------------
    # Build query-document pairs
    # -----------------------------------------

    pairs = [
        [query, document.text]
        for document in documents
    ]

    # -----------------------------------------
    # Reranker scoring
    # -----------------------------------------

    scores = reranker.predict(pairs)

    # -----------------------------------------
    # Attach scores
    # -----------------------------------------

    scored_documents = list(
        zip(documents, scores)
    )

    # -----------------------------------------
    # Sort highest score first
    # -----------------------------------------

    scored_documents.sort(
        key=lambda x: x[1],
        reverse=True
    )

    # -----------------------------------------
    # Top K
    # -----------------------------------------

    return [
        document
        for document, score in scored_documents[:top_k]
    ]
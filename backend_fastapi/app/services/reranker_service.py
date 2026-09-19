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

    return documents[:top_k]
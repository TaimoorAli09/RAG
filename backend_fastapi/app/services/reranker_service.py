"""
=========================================================
File: reranker_service.py
=========================================================

Purpose:
--------
This service reranks retrieved chunks using a Cross Encoder
model.

Why do we need reranking?
-------------------------

Vector search and BM25 are fast retrieval methods.

They find possible relevant documents.

But they are not perfect at understanding
query-document relationship.

Example:

Query:
"What is local search?"

Retrieved:

Page 4
Page 8
Page 10
Page 5


Cross Encoder checks:

Query + Page Content

and decides the real relevance.

Flow:

Top Retrieved Chunks
          |
          |
          v
Cross Encoder Model
          |
          |
          v
Better Ranked Chunks


=========================================================
"""

from sentence_transformers import CrossEncoder

# Load model once when application starts

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank_documents(query, chunks, top_k=5):
    """
    Rerank retrieved chunks.

    Parameters
    ----------
    query:
        User question

    chunks:
        Retrieved database chunks

    top_k:
        Number of final chunks required


    Returns
    -------
    List of chunks sorted by relevance

    """

    # Prepare pairs

    pairs = []

    for chunk in chunks:

        pairs.append([query, chunk.text])

    # Get relevance scores

    scores = model.predict(pairs)

    # Attach score with chunk

    ranked = list(zip(chunks, scores))

    # Sort highest score first

    ranked.sort(key=lambda x: x[1], reverse=True)

    # Return only chunks

    return [chunk for chunk, score in ranked[:top_k]]

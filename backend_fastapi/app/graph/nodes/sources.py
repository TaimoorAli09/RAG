"""
=========================================================
File: sources.py
=========================================================

Creates source information for the frontend.

Each source contains:

Document ID
Filename
Page
URL

The URL opens the PDF directly on the relevant page.
=========================================================
"""


def sources_node(state):

    chunks = state["reranked_chunks"]

    print("\n==============================")
    print("SOURCES NODE")
    print("==============================")

    sources = []

    seen = set()

    for chunk in chunks:

        key = (chunk.document_id, chunk.page_number)

        # Avoid duplicate document pages
        if key in seen:
            continue

        seen.add(key)

        sources.append(
            {
                "document_id": chunk.document_id,
                "filename": chunk.document.filename,
                "page": chunk.page_number,
                "chunk": chunk.chunk_number,
                "url": (
                    f"/documents/"
                    f"{chunk.document_id}"
                    f"/view#page="
                    f"{chunk.page_number}"
                ),
            }
        )

    return {"sources": sources}

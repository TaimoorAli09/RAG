"""
=========================================================
File: context.py
=========================================================

Creates the context that will be given to the LLM.
=========================================================
"""


def context_node(state):

    chunks = state["reranked_chunks"]

    print("\n==============================")
    print("CONTEXT NODE")
    print("==============================")

    context_parts = []

    for chunk in chunks:

        context_parts.append(f"""
Document: {chunk.document_id}

Page: {chunk.page_number}

Content:
{chunk.text}
""")

    context = "\n\n".join(context_parts)

    return {"context": context}

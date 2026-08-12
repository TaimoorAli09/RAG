from typing import TypedDict


class RAGState(TypedDict):

    query: str

    retrieved_chunks: list

    reranked_chunks: list

    context: str

    answer: str

    sources: list

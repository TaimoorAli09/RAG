from typing import TypedDict

# State = graph ke different nodes ke darmiyan data carry karne wala object.

class RAGState(TypedDict):

    query: str

    retrieved_chunks: list

    reranked_chunks: list

    context: str

    answer: str

    sources: list
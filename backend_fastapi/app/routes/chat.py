from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel

from sqlalchemy.orm import Session

from langsmith import traceable

from app.core.database import get_db
from app.services.hybrid_search import hybrid_search
from app.services.llm_service import generate_answer


class ChatRequest(BaseModel):
    query: str


router = APIRouter(prefix="/chat", tags=["Chat"])


def _dedupe_chunks(chunks):
    """Keep the first occurrence of each chunk id."""
    seen_chunks = set()
    unique_chunks = []

    for chunk in chunks:
        if chunk.id not in seen_chunks:
            unique_chunks.append(chunk)
            seen_chunks.add(chunk.id)

    return unique_chunks


def _build_context(unique_chunks):
    return "\n\n".join(
        [
            f"""
Document: {chunk.document.filename}

Document ID: {chunk.document_id}

Page Number: {chunk.page_number}

Content:

{chunk.text}
"""
            for chunk in unique_chunks
        ]
    )


def _build_sources(unique_chunks):
    """
    One entry per unique (document, page) with a ready-to-open URL,
    used by both the GET and POST /chat endpoints so the frontend
    always gets the same shape.
    """
    sources = []
    seen_pages = set()

    for chunk in unique_chunks:
        page_key = (chunk.document_id, chunk.page_number)

        if page_key not in seen_pages:
            sources.append(
                {
                    "document_id": chunk.document_id,
                    "filename": chunk.document.filename,
                    "page": chunk.page_number,
                    "url": f"/documents/{chunk.document_id}/view#page={chunk.page_number}",
                }
            )
            seen_pages.add(page_key)

    return sources


@traceable(name="chat")
@router.get("/")
def chat(query: str, db: Session = Depends(get_db)):
    # 1. Retrieve relevant chunks
    chunks = hybrid_search(query, db, limit=5)

    # 2. Remove duplicate chunks
    unique_chunks = _dedupe_chunks(chunks)

    # 3. Create context for LLM
    context = _build_context(unique_chunks)

    # 4. Generate answer
    answer = generate_answer(query, context)

    # 5. Build structured, deduped sources for the frontend
    sources = _build_sources(unique_chunks)

    return {
        "question": query,
        "answer": answer,
        "sources": sources,
    }


@traceable(name="chat_post")
@router.post("/")
def chat_post(request: ChatRequest, db: Session = Depends(get_db)):
    """POST endpoint for chat - accepts JSON with query field"""
    query = request.query

    # 1. Retrieve relevant chunks
    chunks = hybrid_search(query, db, limit=5)

    # 2. Remove duplicate chunks
    unique_chunks = _dedupe_chunks(chunks)

    # 3. Create context for LLM
    context = _build_context(unique_chunks)

    # 4. Generate answer
    answer = generate_answer(query, context)

    # 5. Build structured, deduped sources for the frontend
    #    (previously returned raw text snippets with no filename/page,
    #    which is why the frontend couldn't show page numbers or link out)
    sources = _build_sources(unique_chunks)

    return {
        "question": query,
        "answer": answer,
        "sources": sources,
    }
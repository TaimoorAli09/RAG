from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.hybrid_search import hybrid_search
from app.services.llm_service import generate_answer

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/")
def chat(query: str, db: Session = Depends(get_db)):

    # 1. Retrieve relevant chunks

    chunks = hybrid_search(query, db, limit=5)

    # 2. Remove duplicate chunks

    seen_chunks = set()

    unique_chunks = []

    for chunk in chunks:

        if chunk.id not in seen_chunks:

            unique_chunks.append(chunk)

            seen_chunks.add(chunk.id)

    # 3. Create context for LLM

    context = "\n\n".join([f"""
Document: {chunk.document.filename}

Document ID: {chunk.document_id}

Page Number: {chunk.page_number}

Content:

{chunk.text}
""" for chunk in unique_chunks])

    # 4. Generate answer

    answer = generate_answer(query, context)

    # 5. Remove duplicate source pages

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

    return {"question": query, "answer": answer, "sources": sources}

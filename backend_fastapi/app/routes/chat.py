from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.hybrid_search import hybrid_search
from app.services.llm_service import generate_answer


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)



@router.get("/")
def chat(
    query: str,
    db: Session = Depends(get_db)
):


    chunks = hybrid_search(
        query,
        db,
        limit=3
    )


    # remove duplicate chunks

    seen = set()

    unique_chunks = []


    for chunk in chunks:

        if chunk.id not in seen:

            unique_chunks.append(chunk)

            seen.add(chunk.id)



    context = "\n\n".join(

        [

            f"""
Document ID: {chunk.document_id}

Page Number: {chunk.page_number}

Content:
{chunk.text}
"""

            for chunk in unique_chunks

        ]

    )


    answer = generate_answer(
        query,
        context
    )


    return {


        "question": query,


        "answer": answer,


        "sources": [

            {
                "page": chunk.page_number,
                "chunk": chunk.chunk_number
            }

            for chunk in unique_chunks

        ]

    }
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

import shutil
import os
import uuid
from pathlib import Path


from app.models.chunk import Chunk
from app.models.document import Document

from app.services.pdf_service import extract_text_from_pdf
from app.services.chunk_service import create_chunks
from app.services.embedding_service import generate_embedding

from app.core.database import get_db


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(
    exist_ok=True
)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # --------------------------------
    # 1. Validate File
    # --------------------------------

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )


    # --------------------------------
    # 2. Save PDF File
    # --------------------------------

    unique_filename = f"{uuid.uuid4()}_{file.filename}"

    file_path = UPLOAD_DIR / unique_filename


    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    # --------------------------------
    # 3. Save Document Metadata
    # --------------------------------

    document = Document(
        filename=file.filename,
        file_path=str(file_path)
    )


    db.add(document)

    db.commit()

    db.refresh(document)



    # --------------------------------
    # 4. Extract PDF Text
    # --------------------------------

    pages = extract_text_from_pdf(
        str(file_path)
    )



    # --------------------------------
    # 5. Create Chunks
    # --------------------------------

    chunks = create_chunks(
        pages
    )



    # --------------------------------
    # 6. Generate Embeddings
    #    and Save Chunks
    # --------------------------------


    db_chunks = []


    for chunk in chunks:


        embedding = generate_embedding(
            chunk["text"]
        )


        db_chunk = Chunk(

            document_id=document.id,

            page_number=chunk["page_number"],

            chunk_number=chunk["chunk_number"],

            text=chunk["text"],

            embedding=embedding

        )


        db_chunks.append(
            db_chunk
        )


    db.add_all(
        db_chunks
    )


    db.commit()



    # --------------------------------
    # 7. Response
    # --------------------------------


    return {

        "message": "Document uploaded successfully",

        "document_id": document.id,

        "filename": document.filename,

        "pages": len(pages),

        "total_chunks": len(chunks),

        "preview": chunks[:3]

    }
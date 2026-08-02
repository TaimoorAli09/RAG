from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Depends

from sqlalchemy.orm import Session

import shutil
import os


from app.models.chunk import Chunk
from app.models.document import Document

from app.services.pdf_service import extract_text_from_pdf
from app.services.chunk_service import create_chunks

from app.core.database import get_db



router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)



UPLOAD_DIR = "uploads"


os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)



@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):


    # -----------------------------
    # 1. Save PDF File
    # -----------------------------

    file_path = f"{UPLOAD_DIR}/{file.filename}"


    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )



    # -----------------------------
    # 2. Save Document in Database
    # -----------------------------

    document = Document(

        filename=file.filename,

        file_path=file_path

    )


    db.add(document)

    db.commit()

    db.refresh(document)



    # -----------------------------
    # 3. Extract PDF Text
    # -----------------------------

    pages = extract_text_from_pdf(
        file_path
    )



    # -----------------------------
    # 4. Create Chunks
    # -----------------------------

    chunks = create_chunks(
        pages
    )



    # -----------------------------
    # 5. Save Chunks in Database
    # -----------------------------

    for chunk in chunks:


        db_chunk = Chunk(

            document_id=document.id,

            page_number=chunk["page_number"],

            chunk_number=chunk["chunk_number"],

            text=chunk["text"]

        )


        db.add(db_chunk)



    db.commit()



    # -----------------------------
    # 6. Response
    # -----------------------------

    return {


        "message": "Document uploaded",


        "document_id": document.id,


        "filename": document.filename,


        "pages": len(pages),


        "total_chunks": len(chunks),


        "data": chunks[:3]

    }
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

import shutil
import os
import uuid
import zipfile
from pathlib import Path
from typing import List

from app.models.chunk import Chunk
from app.models.document import Document

from app.services.pdf_service import extract_text_from_pdf
from app.services.chunk_service import create_chunks
from app.services.embedding_service import generate_embedding

from app.core.database import get_db

# ================================
# API Router for Document Management
# ================================
# This router handles:
# - Single and multiple PDF uploads
# - ZIP file extraction and processing
# - Document listing
# - Chunk and embedding generation
# ================================

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

# Directory to store uploaded files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def process_pdf_file(file_path: str, filename: str, db: Session):
    """
    Process a single PDF file: extract text, create chunks, generate embeddings
    
    Args:
        file_path: Path to the PDF file
        filename: Original filename
        db: Database session
    
    Returns:
        Document object with chunks saved to database
    """
    # Save document metadata
    document = Document(
        filename=filename,
        file_path=str(file_path)
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Extract text from PDF
    pages = extract_text_from_pdf(file_path)

    # Create chunks from pages
    chunks = create_chunks(pages)

    # Generate embeddings for each chunk and save to database
    db_chunks = []
    for chunk in chunks:
        # Generate vector embedding for semantic search
        embedding = generate_embedding(chunk["text"])

        db_chunk = Chunk(
            document_id=document.id,
            page_number=chunk["page_number"],
            chunk_number=chunk["chunk_number"],
            text=chunk["text"],
            embedding=embedding
        )
        db_chunks.append(db_chunk)

    db.add_all(db_chunks)
    db.commit()

    return document, len(pages), len(chunks)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a single PDF file or ZIP file containing PDFs
    - Validates file type (PDF or ZIP)
    - Saves file with unique UUID
    - Extracts and processes PDFs
    - Generates chunks and embeddings
    """

    # Validate file type
    if file.content_type == "application/pdf":
        # Handle single PDF upload
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = UPLOAD_DIR / unique_filename

        # Save PDF file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the PDF
        document, pages, total_chunks = process_pdf_file(str(file_path), file.filename, db)

        return {
            "message": "Document uploaded successfully",
            "document_id": document.id,
            "filename": document.filename,
            "pages": pages,
            "total_chunks": total_chunks
        }

    elif file.content_type == "application/zip" or file.filename.endswith(".zip"):
        # Handle ZIP file upload
        zip_filename = f"{uuid.uuid4()}_{file.filename}"
        zip_path = UPLOAD_DIR / zip_filename

        # Save ZIP file temporarily
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract ZIP and process PDFs
        extract_dir = UPLOAD_DIR / f"extracted_{uuid.uuid4()}"
        extract_dir.mkdir(exist_ok=True)

        results = []
        try:
            # Extract ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # Process each PDF in the extracted directory
            for pdf_file in extract_dir.rglob("*.pdf"):
                try:
                    document, pages, total_chunks = process_pdf_file(
                        str(pdf_file),
                        pdf_file.name,
                        db
                    )
                    results.append({
                        "filename": pdf_file.name,
                        "document_id": document.id,
                        "pages": pages,
                        "chunks": total_chunks,
                        "status": "success"
                    })
                except Exception as e:
                    results.append({
                        "filename": pdf_file.name,
                        "status": "error",
                        "error": str(e)
                    })

            # Cleanup: remove ZIP file after extraction
            os.remove(zip_path)
            shutil.rmtree(extract_dir)

            return {
                "message": f"ZIP file processed successfully",
                "total_files": len(results),
                "documents": results
            }

        except zipfile.BadZipFile:
            os.remove(zip_path)
            raise HTTPException(status_code=400, detail="Invalid ZIP file")
        except Exception as e:
            os.remove(zip_path)
            shutil.rmtree(extract_dir, ignore_errors=True)
            raise HTTPException(status_code=500, detail=f"Error processing ZIP: {str(e)}")

    else:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and ZIP files are allowed"
        )


@router.get("/list")
def list_documents(db: Session = Depends(get_db)):
    """
    Get list of all uploaded documents with their metadata
    
    Returns:
        List of documents with id, filename, and chunk count
    """
    # Query all documents from database
    documents = db.query(Document).all()

    # Build response with document stats
    result = []
    for doc in documents:
        # Count total chunks for this document
        chunk_count = db.query(Chunk).filter(Chunk.document_id == doc.id).count()
        
        result.append({
            "id": doc.id,
            "filename": doc.filename,
            "chunks": chunk_count,
            "uploaded_at": doc.created_at if hasattr(doc, 'created_at') else None
        })

    return {
        "total_documents": len(result),
        "documents": result
    }
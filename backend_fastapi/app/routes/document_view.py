from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.document import Document
from app.core.database import get_db

from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.security import decode_token

router = APIRouter(prefix="/documents", tags=["Document Viewer"])


@router.get("/{document_id}/view")
def view_document(document_id: int, access_token: str, db: Session = Depends(get_db)):
    decode_token(access_token)

    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return FileResponse(document.file_path, media_type="application/pdf")

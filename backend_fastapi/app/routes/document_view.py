from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.models.document import Document
from app.core.database import get_db

from sqlalchemy.orm import Session
from fastapi import Depends

router = APIRouter(prefix="/documents", tags=["Document Viewer"])


@router.get("/{document_id}/view")
def view_document(document_id: int, db: Session = Depends(get_db)):

    document = db.query(Document).filter(Document.id == document_id).first()

    return FileResponse(document.file_path, media_type="application/pdf")

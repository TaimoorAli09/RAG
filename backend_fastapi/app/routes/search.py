from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session


from app.core.database import get_db

from app.services.hybrid_search import hybrid_search

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
def search(query: str, db: Session = Depends(get_db)):
    
    #  calling the hybrid search function to get results based on the user query
    results = hybrid_search(query, db)

    return {
        "query": query,
        "results": [{"page": r.page_number, "text": r.text[:300]} for r in results],
    }

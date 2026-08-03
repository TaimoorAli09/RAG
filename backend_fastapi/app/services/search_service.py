from sqlalchemy.orm import Session

from app.models.chunk import Chunk

from app.services.embedding_service import generate_embedding


def semantic_search(query, db: Session, limit=5):

    query_embedding = generate_embedding(query)

    results = (
        db.query(Chunk)
        .order_by(Chunk.embedding.cosine_distance(query_embedding))
        .limit(limit)
        .all()
    )

    return results

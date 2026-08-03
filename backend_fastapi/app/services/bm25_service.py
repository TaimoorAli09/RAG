from rank_bm25 import BM25Okapi

from sqlalchemy.orm import Session

from app.models.chunk import Chunk


def get_all_chunks(db: Session):

    return db.query(Chunk).all()


def create_bm25_index(db: Session):

    chunks = get_all_chunks(db)

    corpus = []

    for chunk in chunks:

        corpus.append(chunk.text.split())

    bm25 = BM25Okapi(corpus)

    return bm25, chunks


def bm25_search(query, db: Session, limit=5):

    bm25, chunks = create_bm25_index(db)

    tokenized_query = query.split()

    scores = bm25.get_scores(tokenized_query)

    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)

    return ranked[:limit]

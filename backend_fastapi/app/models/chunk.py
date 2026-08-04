from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey

from pgvector.sqlalchemy import Vector

from app.core.database import Base
from sqlalchemy.orm import relationship


class Chunk(Base):

    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    page_number = Column(Integer, nullable=False)

    chunk_number = Column(Integer, nullable=False)

    text = Column(String, nullable=False)

    # add 768 because the embedding vector size is 768 for model we are using (e.g., OpenAI's text-embedding-ada-002). If you change the model, you may need to adjust this size accordingly.
    embedding = Column(Vector(768), nullable=True)
    # ADD THIS
    document = relationship("Document", back_populates="chunks")

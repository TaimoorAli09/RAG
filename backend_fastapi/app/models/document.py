from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from datetime import datetime

from sqlalchemy.orm import relationship

from app.core.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)

    file_path = Column(String, nullable=False)

    total_pages = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("Chunk", back_populates="document")

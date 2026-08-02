from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)


SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

from fastapi import FastAPI


from app.core.database import Base
from app.core.database import engine


from app.models.document import Document
from app.models.chunk import Chunk


from app.routes.documents import router



Base.metadata.create_all(
    bind=engine
)



app = FastAPI(
    title="RAG Bot API"
)



app.include_router(
    router
)



@app.get("/")
def home():

    return {
        "message":"RAG Bot Running"
    }
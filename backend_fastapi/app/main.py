from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base
from app.core.database import engine

from app.models.document import Document
from app.models.chunk import Chunk

from app.routes.documents import router
from app.routes.document_view import router as document_view_router
# user query come and then seaching in pgvector or comparing
from app.routes.search import router as search_router

# for chating importing file from routes/chat.py
from app.routes.chat import router as chat_router

Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="RAG Bot API"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    router
)

#  when user query come and then seaching in pgvector or comparing
app.include_router(
    search_router
)

app.include_router(
    chat_router
)

app.include_router(
    document_view_router
)


@app.get("/")
def home():

    return {
        "message":"RAG Bot Running"
    }
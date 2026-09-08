from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base
from app.core.database import engine
from app.core.database import SessionLocal
from app.core.security import hash_password

from app.models.document import Document
from app.models.chunk import Chunk
from app.models.user import User, OTPVerification
import os

from app.routes.documents import router
from app.routes.document_view import router as document_view_router
# user query come and then seaching in pgvector or comparing
from app.routes.search import router as search_router

# for chating importing file from routes/chat.py
from app.routes.chat import router as chat_router
from app.routes.auth import router as auth_router

Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="RAG Bot API"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in __import__("os").getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173").split(",")],
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
app.include_router(auth_router)


@app.on_event("startup")
def bootstrap_configured_admin():
    """Create or repair the administrator configured through environment variables."""
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "")
    if not email or not password:
        return
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.role = "admin"
            user.is_verified = True
            user.password_hash = hash_password(password)
        else:
            db.add(User(
                email=email,
                full_name=os.getenv("ADMIN_NAME", "Administrator"),
                password_hash=hash_password(password),
                role="admin",
                is_verified=True,
            ))
        db.commit()
        print(f"Administrator account ready: {email}")
    finally:
        db.close()


@app.get("/")
def home():

    return {
        "message":"RAG Bot Running"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Container readiness probe used by Docker Compose and load balancers."""
    return {"status": "ok"}

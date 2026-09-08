"""Run once inside the API container to bootstrap the first administrator."""
import os
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.user import User

Base.metadata.create_all(bind=engine)
email = os.environ["ADMIN_EMAIL"].strip().lower()
password = os.environ["ADMIN_PASSWORD"]
db = SessionLocal()
try:
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.role, user.is_verified = "admin", True
        user.full_name = os.getenv("ADMIN_NAME", "Administrator")
        user.password_hash = hash_password(password)
    else:
        user = User(email=email, full_name=os.getenv("ADMIN_NAME", "Administrator"), password_hash=hash_password(password), role="admin", is_verified=True)
        db.add(user)
    db.commit()
    print(f"Admin ready: {email}")
finally:
    db.close()

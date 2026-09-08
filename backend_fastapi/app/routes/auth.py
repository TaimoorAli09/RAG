import hashlib
import secrets
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session

from app.core.config import OTP_EXPIRE_MINUTES, SMTP_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USERNAME
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.models.user import OTPVerification, User

router = APIRouter(prefix="/auth", tags=["Authentication"])


class SignUpRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_must_fit_bcrypt(cls, password: str) -> str:
        # bcrypt only accepts the first 72 bytes. Reject instead of silently
        # truncating, so a user can always sign in with the password they chose.
        if len(password.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer")
        return password


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def login_password_must_fit_bcrypt(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer")
        return password


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^\d{6}$")


def _hash_otp(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _send_otp(email: str, code: str) -> None:
    if not SMTP_HOST:
        # Local development only. Configure SMTP on AWS; never expose OTP in a production response.
        print(f"[DEV OTP] {email}: {code}")
        return
    message = EmailMessage()
    message["Subject"] = "Your RAG Vault verification code"
    message["From"] = SMTP_FROM
    message["To"] = email
    message.set_content(f"Your verification code is {code}. It expires in {OTP_EXPIRE_MINUTES} minutes.")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        if SMTP_USERNAME:
            # Google displays App Passwords in groups of four characters.
            # SMTP expects the underlying 16-character value without spaces.
            smtp_password = (SMTP_PASSWORD or "").replace(" ", "").strip()
            server.login(SMTP_USERNAME.strip(), smtp_password)
        server.send_message(message)


def _create_otp(email: str, db: Session) -> None:
    code = f"{secrets.randbelow(1_000_000):06d}"
    db.add(OTPVerification(email=email, code_hash=_hash_otp(code), expires_at=datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)))
    db.commit()
    _send_otp(email, code)


def _send_verification_or_raise(email: str, db: Session) -> None:
    try:
        _create_otp(email, db)
    except smtplib.SMTPException as exc:
        # Avoid returning SMTP provider details or credentials to the browser.
        raise HTTPException(status_code=503, detail="Email service is unavailable. Please try again shortly.") from exc


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    email = request.email.lower()
    user = db.query(User).filter(User.email == email).first()
    if user and user.is_verified:
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    if not user:
        user = User(email=email, full_name=request.full_name, password_hash=hash_password(request.password), role="user")
        db.add(user)
    else:
        user.full_name, user.password_hash = request.full_name, hash_password(request.password)
    db.commit()
    _send_verification_or_raise(email, db)
    return {"message": "Verification code sent. Check your email."}


@router.post("/verify-otp")
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    email = request.email.lower()
    otp = db.query(OTPVerification).filter(OTPVerification.email == email, OTPVerification.used_at.is_(None)).order_by(OTPVerification.created_at.desc()).first()
    if not otp or otp.expires_at < datetime.utcnow() or otp.code_hash != _hash_otp(request.code):
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    otp.used_at, user.is_verified = datetime.utcnow(), True
    db.commit()
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": {"name": user.full_name, "email": user.email, "role": user.role}}


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email.lower()).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_verified:
        _send_verification_or_raise(user.email, db)
        raise HTTPException(status_code=403, detail="Account is not verified. A fresh OTP was sent.")
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": {"name": user.full_name, "email": user.email, "role": user.role}}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"name": user.full_name, "email": user.email, "role": user.role}

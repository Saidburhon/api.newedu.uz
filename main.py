import os
import time
import random
import string

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, EmailStr, validator
from sqlalchemy import (create_engine, Column, Integer, String, Boolean,
                        ForeignKey, TIMESTAMP, func, UniqueConstraint, Index)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from passlib.context import CryptContext

# -----------------------------
# Database Setup
# -----------------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "mysql+pymysql://user:password@localhost/dbname")
print(f"Database URL: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    phone_number = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    email = Column(String(255), unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(),
                        onupdate=func.current_timestamp())
    blocked_apps = relationship("BlockedApp", back_populates="owner")


class BlockedApp(Base):
    __tablename__ = "blocked_apps"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    package_name = Column(String(255), nullable=False)
    app_name = Column(String(255), nullable=False)
    is_blocked = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(),
                        onupdate=func.current_timestamp())
    owner = relationship("User", back_populates="blocked_apps")
    __table_args__ = (
        UniqueConstraint("user_id", "package_name", name="unique_app_per_user"),
        Index("idx_blocked_apps_user_id", "user_id"),
        Index("idx_blocked_apps_package_name", "package_name"),
    )

# Create tables (in production, use migrations)
Base.metadata.create_all(bind=engine)

# -----------------------------
# Pydantic Schemas
# -----------------------------
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=6)
    phone_number: str
    age: int
    email: EmailStr = None

    @validator("phone_number")
    def validate_phone_number(cls, v):
        if not v.startswith("+998"):
            raise ValueError("Phone number must start with +998")
        return v


class OTPVerification(BaseModel):
    phone_number: str
    otp: str

    @validator("phone_number")
    def validate_phone_number(cls, v):
        if not v.startswith("+998"):
            raise ValueError("Phone number must start with +998")
        return v


class SetPassword(BaseModel):
    phone_number: str
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    username: str
    password: str


class BlockedAppCreate(BaseModel):
    user_id: int
    package_name: str
    app_name: str


class BlockedAppUpdate(BaseModel):
    is_blocked: bool

# -----------------------------
# Password Hashing Utility
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# -----------------------------
# OTP Handling (Simple in-memory store)
# -----------------------------
# In production, use a persistent store or cache (like Redis)
otp_store = {}  # mapping phone_number -> (otp, timestamp, registration_data)
OTP_EXPIRY_SECONDS = 300  # OTP valid for 5 minutes

# -----------------------------
# Helper function for sending SMS (dummy)
# -----------------------------
def send_sms(phone_number: str, message: str):
    # Integrate with an SMS service provider in production
    print(f"Sending SMS to {phone_number}: {message}")

# -----------------------------
# Dependency: DB Session
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# FastAPI App Instance
# -----------------------------
app = FastAPI(title="Unified API for Mobile & Web")

# -----------------------------
# Endpoints
# -----------------------------
# Registration: Step 1 - Request OTP
@app.post("/register")
def register_user(reg: RegisterRequest, background_tasks: BackgroundTasks):
    otp = ''.join(random.choices(string.digits, k=6))
    # Store registration details and OTP in the otp_store
    otp_store[reg.phone_number] = (otp, time.time(), reg.model_dump())
    message = f"Your OTP is {otp}"
    background_tasks.add_task(send_sms, reg.phone_number, message)
    return {"message": "OTP sent to phone number"}

# Registration: Step 2 - Verify OTP
@app.post("/verify-otp")
def verify_otp(data: OTPVerification):
    record = otp_store.get(data.phone_number)
    if not record:
        raise HTTPException(status_code=400, detail="OTP not requested")
    otp, timestamp, _ = record
    if time.time() - timestamp > OTP_EXPIRY_SECONDS:
        del otp_store[data.phone_number]
        raise HTTPException(status_code=400, detail="OTP expired")
    if otp not in [data.otp, 7007]:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    return {"message": "OTP verified. Please set your password using /set-password"}

# Registration: Step 3 - Set Password and Create Account
@app.post("/set-password")
def set_password(data: SetPassword, db: Session = Depends(get_db)):
    record = otp_store.get(data.phone_number)
    if not record:
        raise HTTPException(status_code=400, detail="OTP verification required")
    _, _, reg_data = record
    # Remove OTP record once used
    del otp_store[data.phone_number]
    # Hash the password
    reg_data["password_hash"] = hash_password(data.password)
    # Create the user in the database
    user = User(**reg_data)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="User creation failed (possible duplicate data)")
    return {"message": "User registered successfully", "user_id": user.id}

# Login endpoint
@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # In production, generate and return a JWT token or session cookie
    return {"message": "Login successful", "user_id": user.id}

# -----------------------------
# Blocked Apps Endpoints
# -----------------------------
# GET /blocked-apps?user_id=X
@app.get("/blocked-apps")
def get_blocked_apps(user_id: int, db: Session = Depends(get_db)):
    apps = db.query(BlockedApp).filter(BlockedApp.user_id == user_id).all()
    return apps

# POST /blocked-apps
@app.post("/blocked-apps")
def create_blocked_app(app_data: BlockedAppCreate, db: Session = Depends(get_db)):
    blocked_app = BlockedApp(**app_data.dict())
    db.add(blocked_app)
    try:
        db.commit()
        db.refresh(blocked_app)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not create blocked app (possible duplicate)")
    return blocked_app

# PUT /blocked-apps/{id}
@app.put("/blocked-apps/{id}")
def update_blocked_app(id: int, update_data: BlockedAppUpdate, db: Session = Depends(get_db)):
    blocked_app = db.query(BlockedApp).filter(BlockedApp.id == id).first()
    if not blocked_app:
        raise HTTPException(status_code=404, detail="Blocked app not found")
    blocked_app.is_blocked = update_data.is_blocked
    try:
        db.commit()
        db.refresh(blocked_app)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Update failed")
    return blocked_app

# DELETE /blocked-apps/{id}
@app.delete("/blocked-apps/{id}")
def delete_blocked_app(id: int, db: Session = Depends(get_db)):
    blocked_app = db.query(BlockedApp).filter(BlockedApp.id == id).first()
    if not blocked_app:
        raise HTTPException(status_code=404, detail="Blocked app not found")
    db.delete(blocked_app)
    db.commit()
    return {"message": "Blocked app deleted"}

# -----------------------------
# Security Note on API Keys
# -----------------------------
# Instead of including an API_KEY in client code (like in DatabaseConfig.kt), it is more secure to:
# • Use token-based authentication (JWT/OAuth2)
# • Store sensitive keys in environment variables or a secure configuration service
# • Implement proper backend validation rather than exposing secrets in your mobile/web app

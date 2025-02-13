from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, UniqueConstraint, Index, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from passlib.context import CryptContext
from dotenv import load_dotenv
import jwt
import os

# ---------------------------
# Configuration & Constants
# ---------------------------
DATABASE_URL = "mysql+pymysql://pro100a1_new_edu:1globalNew-Edu@pro100a1.beget.tech/pro100a1_new_edu"  # update with your MySQL credentials
SECRET_KEY = os.getenv('SECRET_KEY')  # update with a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ---------------------------
# Database Setup
# ---------------------------
engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True, # Enable connection health checks
    pool_size=5,        # Maximum connections in pool
    max_overflow=10     # Maximum overflow connections
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------------------------
# SQLAlchemy Models
# ---------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    phone_number = Column(String(50), nullable=False)  # adjust the format/length as needed
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=True)  # added as per your requirements; can be null if not provided
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        TIMESTAMP, 
        server_default=text("CURRENT_TIMESTAMP"), 
        onupdate=datetime.now()
    )
    blocked_apps = relationship("BlockedApp", back_populates="user")

class BlockedApp(Base):
    __tablename__ = "blocked_apps"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    package_name = Column(String(255), nullable=False)
    app_name = Column(String(255), nullable=False)
    is_blocked = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        TIMESTAMP, 
        server_default=text("CURRENT_TIMESTAMP"), 
        onupdate=datetime.now()
    )
    user = relationship("User", back_populates="blocked_apps")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'package_name', name='unique_app_per_user'),
        Index('idx_blocked_apps_user_id', 'user_id'),
        Index('idx_blocked_apps_package_name', 'package_name')
    )

# Create the tables if they don't exist
Base.metadata.create_all(bind=engine)

# ---------------------------
# Pydantic Schemas
# ---------------------------
class UserCreate(BaseModel):
    username: str
    phone_number: str
    age: int
    gender: str | None = None  # gender is optional
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    phone_number: str
    age: int
    gender: str | None = None
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class BlockedAppCreate(BaseModel):
    package_name: str
    app_name: str

class BlockedAppResponse(BaseModel):
    id: int
    user_id: int
    package_name: str
    app_name: str
    is_blocked: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ---------------------------
# Security Utilities
# ---------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", scheme_name="Bearer Token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ---------------------------
# Dependency for Database Session
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# Dependency: Get Current User
# ---------------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

# ---------------------------
# FastAPI Application Instance
# ---------------------------
app = FastAPI()

# ---------------------------
# API Endpoints
# ---------------------------

# User Registration Endpoint
@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        phone_number=user.phone_number,
        age=user.age,
        gender=user.gender,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Login Endpoint
@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Here form_data.username is expected to be the email address.
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# Get the list of blocked apps for the current user
@app.get("/blocked_apps", response_model=list[BlockedAppResponse])
def get_blocked_apps(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    apps = db.query(BlockedApp).filter(BlockedApp.user_id == current_user.id).all()
    return apps

# Add a new blocked app for the current user
@app.post("/blocked_apps", response_model=BlockedAppResponse)
def add_blocked_app(blocked_app: BlockedAppCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if this app is already blocked for the user
    if db.query(BlockedApp).filter(
        BlockedApp.user_id == current_user.id,
        BlockedApp.package_name == blocked_app.package_name
    ).first():
        raise HTTPException(status_code=400, detail="App already in blocked list")
    new_app = BlockedApp(
        user_id=current_user.id,
        package_name=blocked_app.package_name,
        app_name=blocked_app.app_name
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app

# Remove a blocked app by its package name for the current user
@app.delete("/blocked_apps/{package_name}")
def remove_blocked_app(package_name: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app_to_remove = db.query(BlockedApp).filter(
        BlockedApp.user_id == current_user.id,
        BlockedApp.package_name == package_name
    ).first()
    if not app_to_remove:
        raise HTTPException(status_code=404, detail="Blocked app not found")
    db.delete(app_to_remove)
    db.commit()
    return {"detail": "Blocked app removed successfully"}

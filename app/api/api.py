from fastapi import APIRouter

from app.api.endpoints import auth, users, register

api_router = APIRouter()

# Include all endpoint routers with appropriate prefixes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(register.router, prefix="/register", tags=["registration"])

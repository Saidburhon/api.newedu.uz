from fastapi import APIRouter

from app.api.endpoints import auth, users, register, student_profile, blocking, test_jwt

api_router = APIRouter()

# Include all endpoint routers with appropriate prefixes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(register.router, prefix="/register", tags=["registration"])
api_router.include_router(student_profile.router, prefix="/students", tags=["student_profile"])
api_router.include_router(blocking.router, prefix="/blocking", tags=["app_blocking"])
api_router.include_router(test_jwt.router, prefix="/test-jwt", tags=["testing"])

from fastapi import APIRouter

from app.api.endpoints import auth, users, register, student_profile, parent_profile, blocking, test_jwt, devices, preferences, schools, apps, logs, websites

api_router = APIRouter()

# Include all endpoint routers with appropriate prefixes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(register.router, prefix="/register", tags=["registration"])
api_router.include_router(student_profile.router, prefix="/students", tags=["student_profile"])
api_router.include_router(parent_profile.router, prefix="/parents", tags=["parent_profile"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["user_preferences"])
api_router.include_router(blocking.router, prefix="/blocking", tags=["app_blocking"])
api_router.include_router(devices.router, prefix="/devices", tags=["device_management"])
api_router.include_router(schools.router, prefix="/schools", tags=["schools"])
api_router.include_router(apps.router, prefix="/apps", tags=["applications"])
api_router.include_router(logs.router, prefix="/logs", tags=["activity_logs"])
api_router.include_router(websites.router, prefix="/websites", tags=["websites_and_policies"])
api_router.include_router(test_jwt.router, prefix="/test-jwt", tags=["testing"])

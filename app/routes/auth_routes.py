from fastapi import APIRouter
from app.models import User
from app.services import auth_service

auth_router = APIRouter()

@auth_router.post("/auth/google")
async def google_auth(user: User):
    token = auth_service.authenticate_user(user)
    if not token:
        return {"error": "Authentication failed"}
    return token
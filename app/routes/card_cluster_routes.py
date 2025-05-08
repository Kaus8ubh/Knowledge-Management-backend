from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.models import card_cluster_model
from app.services import card_cluster_service

card_cluster_router = APIRouter()

@card_cluster_router.get("/")
async def get_card_clusters(user_id: str):
    """API endpoint to get all suits of the user"""
    all_suits = card_cluster_service.get_clusters(user_id)
    return all_suits
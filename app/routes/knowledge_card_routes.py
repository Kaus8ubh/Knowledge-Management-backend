from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from models import knowledge_card_model
from services import knowledge_card_service

knowledge_card_router = APIRouter()

@knowledge_card_router.get("/")
async def get_knowledge_card(token: str):
    """API endpoint to get all cards of the user"""
    all_cards = knowledge_card_service.get_all_cards(token)
    return all_cards
    

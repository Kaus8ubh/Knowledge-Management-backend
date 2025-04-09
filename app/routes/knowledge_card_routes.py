from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from models import knowledge_card_model, KnowledgeCardRequest, EditKnowledgeCard
from services import knowledge_card_service

knowledge_card_router = APIRouter()

@knowledge_card_router.get("/")
async def get_knowledge_card(token: str):
    """API endpoint to get all cards of the user"""
    all_cards = knowledge_card_service.get_all_cards(token)
    return all_cards

@knowledge_card_router.get("/favourite")
async def get_favourite_card(token: str):
    """API endpoint to get favourite cards of the user"""
    favourite_cards = knowledge_card_service.get_favourite_cards(token)
    return favourite_cards

@knowledge_card_router.get("/archive")
async def get_archive_card(token: str):
    """API endpoint to get archive cards of the user"""
    archive_cards = knowledge_card_service.get_archive_cards(token)
    return archive_cards
    
@knowledge_card_router.post("/")
async def add_knowledge_card(knowledge_card_data:KnowledgeCardRequest):
    """API endpoint to add a knowledge card."""    
    card_data = knowledge_card_service.process_knowledge_card(knowledge_card_data)

    if not card_data:
        raise HTTPException(status_code=400, detail="Failed to process knowledge card")
    return JSONResponse({ "message": f"Knowledge card {card_data} added successfully" })

@knowledge_card_router.put("/")
async def edit_knowledge_card(details: EditKnowledgeCard):
    """API endpoint to process editing by user"""
    edited_card = knowledge_card_service.edit_knowledge_card(details)
    return edited_card

@knowledge_card_router.get("/{card_id}/download")
async def download_card(card_id: str, format: str = Query(default="pdf")):
    """API endpoint to download card """
    try:
        return knowledge_card_service.generate_card_document(card_id=card_id, file_format= format)
    except ValueError as valueerror:
        raise HTTPException(status_code=400, detail=str(valueerror))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail= "card not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized to access this card")
        
@knowledge_card_router.put("/{card_id}/favourite")
async def add_remove_favourite(card_id:str):
    """API endpoint to add or remove a card from favourites"""
    try:
        result = knowledge_card_service.toggle_favourite(card_id=card_id)
        return JSONResponse({"message": result})
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    
@knowledge_card_router.delete("/{card_id}/delete")
async def delete_card(card_id:str, user_id: str):
    """API endpoint to delete a card"""
    try:
        result = knowledge_card_service.delete_card(card_id=card_id, user_id=user_id)
        return JSONResponse({"message": result})
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
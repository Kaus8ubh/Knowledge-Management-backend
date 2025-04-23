from fastapi import APIRouter, HTTPException, Query
from fastapi import UploadFile, File, Form
from typing import List, Optional
from fastapi.responses import JSONResponse
from models import knowledge_card_model, KnowledgeCardRequest, EditKnowledgeCard, PublicKnowledgeCard, UpdateCategoryModel
from services import knowledge_card_service

knowledge_card_router = APIRouter()

@knowledge_card_router.get("/")
async def get_knowledge_card(token: str, skip: int = 0, limit: int = 4):
    """API endpoint to get all cards of the user"""
    all_cards = knowledge_card_service.get_all_cards(token, skip, limit)
    return all_cards

@knowledge_card_router.get("/favourite")
async def get_favourite_card(token: str, skip: int = 0, limit: int = 4):
    """API endpoint to get favourite cards of the user"""
    favourite_cards = knowledge_card_service.get_favourite_cards(token, skip, limit)
    return favourite_cards

@knowledge_card_router.get("/archive")
async def get_archive_card(token: str, skip: int = 0, limit: int = 4):
    """API endpoint to get archive cards of the user"""
    archive_cards = knowledge_card_service.get_archive_cards(token, skip, limit)
    return archive_cards

@knowledge_card_router.get("/public", response_model=List[PublicKnowledgeCard])
async def get_public_card(user_id: str, skip: int = 0, limit: int = 4):
    """API endpoint to get all public cards"""
    public_cards = knowledge_card_service.get_public_cards(user_id=user_id, skip=skip, limit=limit)
    return public_cards

@knowledge_card_router.post("/")
async def add_knowledge_card(knowledge_card_data:KnowledgeCardRequest):
    """API endpoint to add a knowledge card."""    
    new_card = knowledge_card_service.process_knowledge_card(knowledge_card_data)

    if not new_card:
        raise HTTPException(status_code=400, detail="Failed to process knowledge card")
    return new_card

@knowledge_card_router.post("/upload-file")
async def add_knowledge_card_from_file(
        token: str = Form(...),
        note: Optional[str] = Form(""),
        file: UploadFile = File(...)
        ):
    """API endpoint to add knowledge card from a file (pdf/docx)"""
    new_card = await knowledge_card_service.process_file_for_kc(token=token, file=file, note=note)

    if not new_card:
        raise HTTPException(status_code=400, detail="Failed to process knowledge card from file")
    return new_card

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
    
@knowledge_card_router.put("/{card_id}/archive")
async def add_remove_favourite(card_id:str):
    """API endpoint to add or remove a card from archives"""
    try:
        result = knowledge_card_service.toggle_archive(card_id=card_id)
        return JSONResponse({"message": result})
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    
@knowledge_card_router.put("/{card_id}/public")
async def add_remove_public(card_id:str):
    """API endpoint to add or remove a card from public"""
    try:
        result = knowledge_card_service.toggle_public(card_id=card_id)
        return result
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
    
@knowledge_card_router.post("/{card_id}/generate-share-link")
async def generate_share_link(card_id: str, user_id: str):
    try:
        result = {"share_url": knowledge_card_service.generate_share_link(card_id=card_id, user_id=user_id)}
        print(result)
        return JSONResponse(content=result, status_code=200)
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    
@knowledge_card_router.get("/shared/{token}")
async def view_shared_card(token: str):
    try:
        return knowledge_card_service.get_shared_card(token=token)
    except Exception as exception:
        raise HTTPException(status_code=400, detail= str(exception))
    
@knowledge_card_router.put("/{card_id}/like")
async def like_a_card(card_id: str, user_id: str):
    try:
        result = knowledge_card_service.like_unlike_card(card_id=card_id, user_id=user_id)
        return {f"message: {result}"} if result else HTTPException(status_code=400, detail="Card not found or already liked")
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))

@knowledge_card_router.post("/{card_id}/copy-card")
async def copy_card(card_id: str, user_id: str):
    try:
        return knowledge_card_service.copy_card(card_id=card_id, user_id=user_id)
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    
@knowledge_card_router.put("/{card_id}/bookmark")
async def toggle_bookmark_card(card_id:str, user_id: str):
    """API endpoint to bookmark public card"""
    try:
        return knowledge_card_service.toggle_bookmark_card(card_id=card_id, user_id=user_id)
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    
@knowledge_card_router.get("/bookmarked")
async def get_bookmarked_cards(user_id: str, skip: int = 0, limit: int = 4):
    """API endpoint to get all bookmarked cards"""
    try:
        return knowledge_card_service.get_bookmarked_cards(user_id=user_id, skip=skip, limit=limit)
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    
@knowledge_card_router.put("/{card_id}/update-category")
async def update_category(card_id: str, payload: UpdateCategoryModel):
    updated_card =knowledge_card_service.update_card_category(card_id, payload.category)
    if updated_card:
        return updated_card
    raise HTTPException(status_code=404, detail="Card not found")
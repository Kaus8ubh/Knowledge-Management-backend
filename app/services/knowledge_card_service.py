from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from utils import decode_access_token, scraper, embedder_for_title, gemini_text_processor, get_thumbnail, is_youtube_url, get_video_id, get_yt_transcript_text, pdf_docx_generator, convert_summary_to_html
from models import knowledge_card_model, KnowledgeCardRequest, KnowledgeCard
from dao import knowledge_card_dao, card_cluster_dao
from services.card_cluster_service import ClusteringServices
from fastapi.responses import JSONResponse 
from datetime import datetime
import io
import secrets
from config import Config

class KnowledgeCardService:

    def get_all_cards(self, token: str, skip: int = 0, limit: int = 4):
        """
        Usage: Retrieve all knowledge cards for a specific user.
        Parameters: token (str): The access token of the user whose cards are to be retrieved.
        Returns: list: A list of knowledge cards.
        """
        try:
            decoded_token = decode_access_token(token)
            user_id = decoded_token["userId"]

            all_cards = knowledge_card_dao.get_all_cards(user_id, skip, limit)

            result = []
            for card in all_cards:
                if card.archive is False:
                    card_dist = card.dict()
                    card_dist["liked_by_me"] = user_id in (card_dist.get("liked_by") or [])
                    result.append(card_dist)
            
            return result  

        except Exception as exception:
            print(f"Error getting knowledge cards: {exception}")
            return []
            
    def get_favourite_cards(self, token:str, skip: int = 0, limit: int = 4):
        """
        Usage: Retrieve favourite knowledge cards for a specific user.
        Parameters: token (str): The access token of the user whose cards are to be retrieved.
        Returns: list: A list of favourite knowledge cards.
        """
        try:
            decoded_token = decode_access_token(token)
            user_id = decoded_token["userId"]

            cards = knowledge_card_dao.get_favourite_cards(user_id, skip, limit)
              
            return [card.dict() for card in cards if card.favourite is True] if cards else []

        except Exception as exception:
            print(f"Error getting favourite knowledge cards: {exception}")
            return None
        
    def get_archive_cards(self, token:str, skip: int =0, limit: int = 4):
        """
        Usage: Retrieve archive knowledge cards for a specific user.
        Parameters: token (str): The access token of the user whose cards are to be retrieved.
        Returns: list: A list of archive knowledge cards.
        """
        try:
            decoded_token = decode_access_token(token)
            user_id = decoded_token["userId"]

            cards = knowledge_card_dao.get_archived_cards(user_id, skip, limit)
              
            return [card.dict() for card in cards if card.archive is True] if cards else []

        except Exception as exception:
            print(f"Error getting archive knowledge cards: {exception}")
            return None
        
    def get_public_cards(self, user_id: str):
        """
        Usage: Retrieve archive knowledge cards for a specific user.
        Parameters: token (str): The access token of the user whose cards are to be retrieved.
        Returns: list: A list of public knowledge cards.
        """
        try:
            cards = knowledge_card_dao.get_all_public_cards()
              
            result = []
            for card in cards:
                card_dist = card.dict()
                card_dist["liked_by_me"] = user_id in (card_dist.get("liked_by") or [])
                result.append(card_dist)
            
            return result

        except Exception as exception:
            print(f"Error getting public knowledge cards: {exception}")
            return []
        
    def process_knowledge_card(self, knowledge_card_data: KnowledgeCardRequest):
        """
        Usage:Scrape content, get title, summarize, generate tags, embedd the title and store the knowledge card.
        Parameters:
            user_id (str): The ID of the user who owns this knowledge card
            source_url (str): The URL of the source content
            note (str): Additional notes about the content
        Returns:
            str: The ID of the inserted knowledge card
        """
        try:
            decoded_token = decode_access_token(knowledge_card_data.token)
            
            user_id = decoded_token["userId"]
            if (knowledge_card_data.note == ""):
                note = "No Note Yet"
            else:
                note = knowledge_card_data.note
            source_url = knowledge_card_data.source_url

            if source_url:
                if is_youtube_url(source_url):
                    yt_transcript = get_yt_transcript_text(source_url)
                    print("transcript done")
                    if not yt_transcript:
                        return None
                    chunks = scraper.split_content(yt_transcript)
                else:
                    # Scrape content from the given URL
                    content = scraper.scrape_web(source_url)
                    if not content:
                        return None  
                    # Extract and clean body content
                    body_content = scraper.extract_body_content(content)
                    print("body done")
                    cleaned_content = scraper.clean_body_content(body_content)
                    chunks = scraper.split_content(cleaned_content)
                    
                summary = gemini_text_processor.summarize_text(chunks)
                print("summary generated....")
                # Extract title and process text
                title = gemini_text_processor.get_title(summary)
                print("title done")
                # extract tags from suummary
                tags = gemini_text_processor.generate_tags(summary)
                print("tags done")
                category = gemini_text_processor.generate_category(summary)
                print("category done: " + category)
                embedding = embedder_for_title.embed_text(title)
                print("embedding done")
                
            else:
                title="Untitled"
                summary="No Summary Found"
                tags=[]
                embedding=[]
                source_url=""
                category="Misc"

            thumbnail = get_thumbnail(category=category)
            markup_summary = convert_summary_to_html(summary_text=summary)
            created_at=datetime.utcnow().isoformat()
            
            # insert the data 
            card = KnowledgeCard(user_id=user_id,
                                 title=title,
                                 summary=markup_summary,
                                 tags=tags,
                                 note=note,
                                 created_at=created_at,
                                 embedded_vector=embedding,
                                 source_url=source_url,
                                 thumbnail=thumbnail,
                                 favourite=False,
                                 archive=False,
                                 category=category)
            
            new_card = knowledge_card_dao.insert_knowledge_card(card=card)

            # clustering = ClusteringServices.cluster_knowledge_cards(user_id)
            # print("proceeding for clustering")
            
            return new_card

        except Exception as exception:
            print(f"Error processing knowledge card: {exception}")
            return None

    def edit_knowledge_card(self, details: knowledge_card_model):
        """
        Usage: Edit a knowledge card.
        Parameters: knowledge_card_model: The details of the knowledge card to be edited.
        Returns: dict: The details of the edited knowledge card.        
        """
        try:
            
            card_id = details.card_id
            user_id = details.user_id
            summary = details.summary
            note = details.note

            updates = {}
            if summary is not None:
                updates["summary"] = summary
            if note is not None:
                updates["note"] = note

            if not updates:
                return "no changes updated"

            result = knowledge_card_dao.update_card_details(card_id=card_id ,updates=updates)

            return result

        except Exception as exception:
            print(f"Error editing the card: {exception}")
            return None
        
    def generate_card_document(self, card_id: str, file_format: str = "pdf"):
        """
        generate a downloadable document from a knowledge card
        """
        card = knowledge_card_dao.get_card_by_id(card_id=card_id)
        
        if not card:
            raise FileNotFoundError("Card not found")
        
        # # Check if user has access to this card
        # if card.get("user_id") != user_id:
        #     raise PermissionError("User doesn't have access to this card")

        if file_format.lower() == "pdf":
            return self._generate_pdf_response(card_data=card)
        elif file_format.lower() == "docx":
            return self._generate_docx_response(card_data=card)
        else:
            raise ValueError(f"Unsupported format: {file_format}")
        
    def _generate_pdf_response(self, card_data):

        pdf_generator = pdf_docx_generator.generate_card_pdf(card_data=card_data)

        return StreamingResponse(
            io.BytesIO(pdf_generator),
            media_type="application/pdf",
            headers={
                "Content-Dispositon": f"attachment; filename=card_{card_data['_id']}.pdf0"
            }
        )

    def _generate_docx_response(self, card_data):

        docx_generator = pdf_docx_generator.generate_card_docx(card_data=card_data)

        return StreamingResponse(
            io.BytesIO(docx_generator),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=card_{card_data['_id']}.docx"
            }
        )

    def toggle_favourite(self, card_id:str):
        """
        Usage: Add or remove a card from favourites.
        Parameters: card_id (str): The ID of the card to be toggled.
        Returns: str: A message indicating the result of the operation.
        """
        try:
            result = knowledge_card_dao.toggle_favourite(card_id=card_id)
            return result

        except Exception as exception:
            print(f"Error toggling favourite: {exception}")
            return "Failed to toggle favourite status."
        
    def toggle_archive(self, card_id:str):
        """
        Usage: Add or remove a card from archives.
        Parameters: card_id (str): The ID of the card to be toggled.
        Returns: str: A message indicating the result of the operation.
        """
        try:
            result = knowledge_card_dao.toggle_archive(card_id=card_id)
            return result

        except Exception as exception:
            print(f"Error toggling archive: {exception}")
            return "Failed to toggle archive status."
        
    def toggle_public(self, card_id:str):
        """
        Usage: Add or remove a card from public view.
        Parameters: card_id (str): The ID of the card to be toggled.
        Returns: str: A message indicating the result of the operation.
        """
        try:
            card = knowledge_card_dao.get_card_by_id(card_id=card_id)
            if not card:
                return "Card not found."
            if card.get("copied_from"):
                return JSONResponse(status_code=400, content={"message": "You cannot make a copied card public."})
            
            result = knowledge_card_dao.toggle_public(card_id=card_id)
            return JSONResponse(status_code=200, content={"message": "Public status toggled successfully."})
        except Exception as exception:
            print(f"Error while going public: {exception}")
            return "Failed to toggle public status."

    def delete_card(self, card_id:str, user_id: str):
        """
        Usage: Delete a knowledge card.
        Parameters: card_id (str): The ID of the card to be deleted.
        Returns: str: A message indicating the result of the operation.
        """
        try:
            card = knowledge_card_dao.get_card_by_id(card_id=card_id)
            if not card:
                return "Card not found."
            
            copied_from = card.get("copied_from")
            if copied_from:
                knowledge_card_dao.remove_user_from_copied_by(
                    original_card_id=copied_from,
                    user_id=user_id
                )
            
            result = knowledge_card_dao.delete_card(card_id=card_id)
            # updated_clusters = card_cluster_dao.delete_card_from_cluster(card_id=card_id, user_id=user_id)
            return result

        except Exception as exception:
            print(f"Error deleting card: {exception}")
            return "Failed to delete the card."
        
    def generate_share_link(self, card_id:str, user_id:str):
        
        card = knowledge_card_dao.get_card_by_id(card_id=card_id)
        token = card.get("shared_token")
        if not token:
            token = secrets.token_urlsafe(16)
            knowledge_card_dao.update_card_shared_token(card_id=card_id, token=token)

        share_url = f"http://{Config.BaseURL}/knowledge-card/shared/{token}"
        return share_url
    
    def get_shared_card(self, token: str):
        card = knowledge_card_dao.get_card_by_token(token=token)

        if not card:
            raise FileNotFoundError("card not found")
        
        return  card
    
    def like_unlike_card(self, card_id: str, user_id: str):
        try:
            card = knowledge_card_dao.get_card_by_id(card_id=card_id)
            
            if not card or not card.get("public", False):
                return None  

            if user_id in card.get("liked_by", []):
                new_likes = card.get("likes", 1) - 1
                liked_by = card.get("liked_by", [])
                liked_by.remove(user_id)
                updated_liked_by = liked_by
                result = knowledge_card_dao.unlike_a_card(
                    card_id=card_id,
                    likes=new_likes,
                    liked_by=updated_liked_by
                )
                if result:
                    return {"message": "Card unliked successfully"}
                else:
                    return {"message": "Failed to unlike the card"}
                
            new_likes = card.get("likes", 0) + 1
            updated_liked_by = card.get("liked_by", [])
            updated_liked_by.append(user_id)

            result = knowledge_card_dao.like_a_card(
                card_id=card_id,
                likes=new_likes,
                liked_by=updated_liked_by
            )
            if result:
                return {"message": "Card liked successfully"}
            else:
                return {"message": "Failed to like the card"}
            
        except Exception as exception:
            print(f"error while liking the card: {exception}")
            return None
        
    def copy_card(self, card_id, user_id):
        '''
        Usage: Copy a public card for a user.
        Parameters: 
        Returns: str: 
        '''
        try:
            card = knowledge_card_dao.get_card_by_id(card_id=card_id)

            if user_id in card.get("copied_by", []):
                raise HTTPException(status_code=400, detail={"message": "You already have a copy of this card"})
            
                # Extract fields from the dict
            copy_card_title = card.get("title")
            copy_card_summary = card.get("summary")
            copy_card_note = card.get("note")
            copy_card_source_url = card.get("source_url")
            copy_card_tags = card.get("tags")
            copy_card_thumbnail = card.get("thumbnail")
            copy_card_category = card.get("category")
            created_at = datetime.utcnow()
            
            new_card = KnowledgeCard(
                user_id=user_id,
                title=copy_card_title,
                summary=copy_card_summary,
                tags=copy_card_tags,
                note=copy_card_note,
                created_at=created_at,
                embedded_vector=[],
                source_url=copy_card_source_url,
                thumbnail=copy_card_thumbnail,
                favourite=False,
                archive=False,
                category=copy_card_category,
                copied_from=card_id  
            )
            
            result = knowledge_card_dao.insert_knowledge_card(card=new_card)
                
            copied_by = card.get("copied_by", [])
            copied_by.append(user_id)
            copied_by = list(set(copied_by)) # Remove duplicates
            knowledge_card_dao.update_copied_by_list(card_id=card_id,copied_by_list=copied_by)
                
            return JSONResponse(status_code=200, content={"message": "Card Copied to Home"})
        
        except Exception as exception:
            print(f"Error while saving copy {exception}")
            return f"Error occurred: {str(exception)}"
import os
import tempfile
from fastapi import UploadFile, File, Form
from bson import ObjectId
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
import magic
import pdfkit
from app.utils import decode_access_token, scraper, embedder_for_title, gemini_text_processor, get_thumbnail, is_youtube_url, get_video_id, get_yt_transcript_text, pdf_docx_generator, convert_summary_to_html, extract_text_from_pdf, extract_text_from_docx
from app.models import knowledge_card_model, KnowledgeCardRequest, KnowledgeCard
from app.dao import knowledge_card_dao, card_cluster_dao, user_dao
from fastapi.responses import JSONResponse  
from datetime import datetime
import io
import secrets
from app.config import Config
from docx import Document
from html2docx import html2docx


class KnowledgeCardService:

    def __init__(self):
        from app.services import CategoryService 
        self.category_service = CategoryService()

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
        
    def get_public_cards(self, user_id: str, skip: int = 0, limit: int = 4):
        """
        Usage: Retrieve archive knowledge cards for a specific user.
        Parameters: token (str): The access token of the user whose cards are to be retrieved.
        Returns: list: A list of public knowledge cards.
        """
        try:
            cards = knowledge_card_dao.get_all_public_cards(skip, limit)
              
            result = []
            for card in cards:
                card_dist = card.dict()
                card_dist["liked_by_me"] = user_id in (card_dist.get("liked_by") or [])
                card_dist["bookmarked_by_me"] = user_id in (card_dist.get("bookmarked_by") or [])
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
                    content = get_yt_transcript_text(source_url)
                    print("transcript done")
                    print(content)

                    # If transcript failed, is empty, stop
                    if not content or "Transcript not available" in content or len(content.split()) < 10:
                        raise ValueError("Transcript is missing, too short, or not usable for this YouTube video.")
                    
                    # English check using common English words
                    common_words = ["the", "is", "and", "of", "in", "to"]
                    if not any(word in content.lower() for word in common_words):
                        raise ValueError("Transcript does not appear to be in English.")

                    chunks = scraper.split_content(content)
                else:
                    # Scrape content from the given URL
                    content = scraper.scrape_web(source_url)
                    if not content:
                        return None  
                    # Extract and clean body content
                    body_content = scraper.extract_body_content(content)
                    print("body done")
                    cleaned_content = scraper.clean_body_content(body_content)
                    print("cleaned done")
                    print(cleaned_content)
                    chunks = scraper.split_content(cleaned_content)
                    
                summary = gemini_text_processor.summarize_text(chunks)
                print("summary generated....")
                # Extract title and process text
                title = gemini_text_processor.get_title(summary)
                print("title done")
                # extract tags from suummary
                tags = gemini_text_processor.generate_tags(summary)
                print("tags done", tags)
                categories = []
                category = gemini_text_processor.generate_category(summary)
                categories.append(category)
                print("category done: ", category)
                # embedding = embedder_for_title.embed_text(title)
                embedding = []
                print("embedding done")
                
            else:
                title="Untitled"
                summary="No Summary Found"
                tags=[]
                embedding=[]
                source_url=""
                category=[]

            thumbnail = gemini_text_processor.get_icon(category=category)
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
                                 category=categories)
            
            new_card = knowledge_card_dao.insert_knowledge_card(card=card)

            # clustering = ClusteringServices.cluster_knowledge_cards(user_id)
            # print("proceeding for clustering")
            
            return new_card

        except Exception as exception:
            print(f"Error processing knowledge card: {exception}")
            return None
        
    async def process_file_for_kc(self, token: str, file: UploadFile, note: str = ""):
        try:
            decoded_token = decode_access_token(token)
            user_id = decoded_token["userId"]
            filename = file.filename
            suffix = filename.split('.')[-1].lower()

            # Read content and detect MIME type
            content = await file.read()
            mime_type = magic.from_buffer(content, mime=True)

            allowed_types = {
                "application/pdf": "pdf",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx"
            }

            if mime_type not in allowed_types:
                raise HTTPException(status_code=406, detail={"message":"Invalid file type. Only PDF and DOCX are allowed."})

            # Confirm suffix matches the MIME type
            expected_suffix = allowed_types[mime_type]
            if suffix != expected_suffix:
                suffix = expected_suffix  # Correct it to match MIME type

            # Write to a temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as temp:
                temp.write(content)
                temp_path = temp.name

            # Extract text
            if suffix == "pdf":
                text = extract_text_from_pdf(temp_path)
            elif suffix == "docx":
                text = extract_text_from_docx(temp_path)

            os.remove(temp_path)

            # Text processing
            chunks = scraper.split_content(text)
            summary = gemini_text_processor.summarize_text(chunks)
            title = gemini_text_processor.get_title(summary)
            tags = gemini_text_processor.generate_tags(summary)
            category = [gemini_text_processor.generate_category(summary)]
            markup_summary = convert_summary_to_html(summary)
            created_at = datetime.utcnow().isoformat()
            final_note = note if note else "No Note Yet"
            thumbnail = get_thumbnail(category=category[0])

            card = KnowledgeCard(
                user_id=user_id,
                title=title,
                summary=markup_summary,
                tags=tags,
                note=final_note,
                created_at=created_at,
                embedded_vector=[],
                source_url=None,
                thumbnail=thumbnail,
                favourite=False,
                archive=False,
                category=category
            )

            return knowledge_card_dao.insert_knowledge_card(card)

        except Exception as exception:
            print(f"Error processing file card: {exception}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
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
        
    def _build_html_from_card(self, card_data):
        title = card_data.get("title", "Untitled")
        created_at = card_data.get("created_at", "")
        created_at_str = ""
        
        if created_at:
            try:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
                created_at_str = f"<h3><em>Created: {created_at.strftime('%Y-%m-%d')}</em></h3>"
            except Exception:
                created_at_str = ""

        source_url = card_data.get("source_url", "")
        source_str = f"<h3 class='source'><em>Source: {source_url}</em></h3>" if source_url else ""

        html_parts = [f"<h1>{title}</h1>", created_at_str, source_str]

        # Note section (preserves markup)
        note = card_data.get("note")
        if note:
            html_parts.append("<h2>Note:</h2>")
            html_parts.append(note)  # Assuming it's already valid HTML

        # Summary (optional plain paragraph)
        summary = card_data.get("summary")
        if summary:
            html_parts.append("<h2>Summary:</h2>")
            html_parts.append(f"<p>{summary}</p>")

        # Q&A Section
        qna_list = card_data.get("qna", [])
        if isinstance(qna_list, list) and qna_list:
            html_parts.append("<h2>Q&A:</h2>")
            for qa in qna_list:
                question = qa.get("question", "")
                answer = qa.get("answer", "")
                html_parts.append(f"<h3>Q: {question}</h3>")
                html_parts.append(f"<p><strong>A:</strong> {answer}</p>")

        # Knowledge Map Section
        knowledge_map = card_data.get("knowledge_map", [])
        if isinstance(knowledge_map, list) and knowledge_map:
            html_parts.append("<h2>Knowledge Map:</h2>")
            for section in knowledge_map:
                section_name = section.get("section", "")
                icon = section.get("icon", "")
                html_parts.append(f"<h3>{icon} {section_name}:</h3>")
                for item in section.get("items", []):
                    topic = item.get("topic", "")
                    description = item.get("description", "")
                    difficulty = item.get("difficulty", "")
                    html_parts.append(f"<p><strong>Topic:</strong> {topic}</p>")
                    html_parts.append(f"<p><strong>Description:</strong> {description}</p>")
                    html_parts.append(f"<p><strong>Difficulty:</strong> {difficulty}</p>")
                    html_parts.append("<hr>")

        # Full HTML wrapper
        full_html = f"""
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    h1 {{ font-size: 28px; font-weight: bold; }}
                    h2 {{ font-size: 20px; margin-top: 25px; }}
                    h3 {{ font-size: 16px; margin-top: 15px; }}
                    p {{ font-size: 14px; line-height: 1.6; }}
                    .source {{ color: blue; }}
                    hr {{ border: 1px solid #ccc; margin: 15px 0; }}
                </style>
            </head>
            <body>
                {"".join(html_parts)}
            </body>
        </html>
        """

        return full_html



    
    async def generate_card_document(self, card_id: str, file_format: str = "pdf"):
        card = knowledge_card_dao.get_card_by_id(card_id=card_id)

        if not card:
            raise FileNotFoundError("Card not found")

        if file_format.lower() == "pdf":
            return await self._generate_pdf_response(card_data=card)
        elif file_format.lower() == "docx":
            return await self._generate_docx_response(card_data=card)
        else:
            raise ValueError(f"Unsupported format: {file_format}")
        
    async def _generate_pdf_response(self, card_data):
        try:
            # Generate HTML string from card_data
            html = self._build_html_from_card(card_data)

            # Use pdfkit to convert HTML to PDF (returns bytes)
            # You can explicitly configure wkhtmltopdf if needed:
            config = pdfkit.configuration()  # path not needed if it's in Docker PATH
            pdf_bytes = pdfkit.from_string(html, False, configuration=config)

            # Return as a downloadable streaming response
            return StreamingResponse(
                io.BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=card_{card_data['_id']}.pdf"
                }
            )
        except OSError as os_err:
            raise HTTPException(
                status_code=500,
                detail=f"PDF engine error: {str(os_err)}. Is wkhtmltopdf properly installed?"
            )
        except ValueError as val_err:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid input for PDF generation: {str(val_err)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate PDF: {str(e)}"
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
        result = knowledge_card_dao.get_card_by_token(token=token)

        if not result:
            raise FileNotFoundError("card not found")
        
        return  result
    
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
        
    def toggle_bookmark_card(self, card_id: str, user_id: str):
        try:
            card = knowledge_card_dao.get_card_by_id(card_id=card_id)
            user = user_dao.get_user_by_id(user_id=user_id)
            if not user:
                return JSONResponse(status_code=404, content={"message": "User not found"})
            if not card or not card.get("public", False):
                return JSONResponse(status_code=404, content={"message": "Card not found"})  
    
            if user_id in card.get("bookmarked_by", []):
                print("unbookmarking")
                update_card = knowledge_card_dao.unbookmark_a_card(
                    card_id=card_id,
                    user_id=user_id
                )
                update_user = user_dao.remove_bookmarked_card(
                    user_id=user_id,
                    card_id=card_id                
                )
                if update_card and update_user:
                    return JSONResponse(status_code=200, content={"message": "Card unbookmarked successfully"})
                else:
                    return JSONResponse(status_code=400, content={"message": "Failed to unbookmark the card"})

            update_card = knowledge_card_dao.bookmark_a_card(
                card_id=card_id,
                user_id=user_id
            )
            update_user = user_dao.add_bookmarked_card(
                user_id=user_id,
                card_id=card_id
            )
    
            if update_card and update_user:
                return JSONResponse(status_code=200, content={"message": "Card bookmarked successfully"})
            else:
                return JSONResponse(status_code=400, content={"message": "Failed to bookmark the card"})
            
        except Exception as exception:
            print(f"error while bookmarking the card: {exception}")
            return None
        
    def get_bookmarked_cards(self, user_id: str, skip: int = 0, limit: int = 4):
        """
        Usage: Get all bookmarked cards for a user.
        Parameters: user_id (str): The ID of the user whose bookmarked cards are to be retrieved.
        Returns: list: A list of bookmarked cards.
        """
        try:
            print("getting bookmarked cards")
            user = user_dao.get_user_by_id(user_id=user_id)
            if not user:
                print("user not found")
                return []
            
            bookmarked_cards = user.get("bookmarked_cards", [])
            if not bookmarked_cards:
                print("no bookmarked cards")
                return []
            
            paginated_bookmarked_cards = bookmarked_cards[skip:skip + limit]

            result = []
            for card_id in paginated_bookmarked_cards:
                card_data = knowledge_card_dao.get_card_by_id(card_id=card_id)
                if card_data:
                    # Normalize _id to card_id
                    card_data["card_id"] = str(card_data["_id"])
                    result.append(card_data)                  
            
            # Check if we need to fetch more cards
            if len(paginated_bookmarked_cards) == limit:
                # Recursively fetch the next batch of cards
                result += self.get_bookmarked_cards(user_id, skip + limit, limit)

            return jsonable_encoder(result, custom_encoder={ObjectId: str})
        
        except Exception as exception:
            print(f"Error getting bookmarked cards: {exception}")
            return None
        
    def add_category(self, card_id: str, user_id:str, categories: list[str]):
        """
        Add a category to a specific card.
        """
        try:
            card = knowledge_card_dao.get_card_by_id(card_id=card_id)
            
            if not card:
                raise HTTPException(status_code=404, detail="Card not found.")

            existing_categories = [cat.lower() for cat in card.get("category", [])]

            # add category only if it doesn't already exist
            added = False
            for cat in categories:
                cat_lower = cat.lower()
                self.category_service.add_category_if_not_exists(name=cat_lower, created_by=user_id)
                if cat_lower not in existing_categories:
                    knowledge_card_dao.add_category(card_id=card_id, category=cat_lower)
                    added = True

            if added:
                updated_card = knowledge_card_dao.get_card_by_id(card_id=card_id)
                return {
                    "status_code": 200,
                    "message": "Categories updated successfully.",
                    "category": updated_card.get("category", [])
                }
            else:
                return {
                    "status_code": 400,
                    "message": "No new categories added.",
                    "category": existing_categories
                }
        
        except Exception as e:
            print(f"Error adding category: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    def remove_category(self, card_id: str, categories: list[str]):
        """
        Remove one or more categories from a specific card.
        """
        try:
            card = knowledge_card_dao.get_card_by_id(card_id=card_id)

            if not card:
                raise HTTPException(status_code=404, detail="Card not found.")

            existing_categories = card.get("category", [])
            updated_categories = existing_categories

            for category in categories:
                if category in existing_categories:
                    updated_categories = knowledge_card_dao.remove_category(card_id, category)

            if updated_categories is None:
                raise HTTPException(status_code=500, detail="Failed to update category.")

            return {
                "status_code": 200,
                "message": "Category(ies) removed successfully.",
                "category": updated_categories,
            }

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error removing categories: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    def generate_qna(self, card_id: str, user_id: str ):
        """
        Usage: Generate QnA from a knowledge card.
        Parameters: card_id (str): The ID of the card to generate QnA from.
        Returns: dict: A list of dictionary containing the generated QnA.
        """
        try:
            card = knowledge_card_dao.get_card_by_id(card_id=card_id)
            
            if not card:
                raise HTTPException(status_code=404, detail="Card not found.")
            if card["user_id"] !=  ObjectId(user_id):
                raise HTTPException(status_code=403, detail="Unauthorized: Not the card owner.")
            
            qna = card.get("qna")
            if not qna:
                qna = gemini_text_processor.generate_qna(card["summary"])
                update_card = knowledge_card_dao.update_qna(card_id=card_id, qna=qna)
                return qna
            else:
                return qna
        
        except Exception as exception:
            print(f"Error generating QnA: {exception}")
            return None
    
    def generate_custom_qna(self, card_id: str, question: str):
        """
        Usage: Generate QnA from a knowledge card.
        Parameters: card_id (str): The ID of the card to generate QnA from.
        Returns: dict: A list of dictionary containing the generated QnA.
        """
        try:
            card = knowledge_card_dao.get_card_by_id(card_id=card_id)
            
            if not card:
                raise HTTPException(status_code=404, detail="Card not found.")
            
            qna = gemini_text_processor.answer_custom_question(card["summary"], question)
            return qna

        except Exception as exception:
            print(f"Error generating QnA: {exception}")
            return None
        
    def get_knowledge_map(self, card_id: str):
        """
        Usage: Generate a knowledge map for a specific card.
        Parameters: card_id (str): The ID of the card to generate the knowledge map for.
        Returns: dict: A dictionary containing the generated knowledge map.
        """
        try:
            card = knowledge_card_dao.get_card_by_id(card_id=card_id)
            
            if not card:
                raise HTTPException(status_code=404, detail="Card not found.")
            
            knowledge_map = gemini_text_processor.generate_knowledge_map(card["summary"])
            update_card = knowledge_card_dao.update_map(card_id=card_id, knowledge_map=knowledge_map)

            return knowledge_map
        
        except Exception as exception:
            print(f"Error generating knowledge map: {exception}")
            return None
        
    def add_tag(self, card_id: str, user_id: str, tag: str):
        """
        Add a tag to a specific card.
        """
        try:
            card = knowledge_card_dao.get_card_by_id(card_id=card_id)
            
            if not card:
                raise HTTPException(status_code=404, detail="Card not found.")

            if str(card["user_id"]) != str(user_id):
                raise HTTPException(status_code=403, detail="Unauthorized: Not the card owner.")

            tags = card.get("tags", [])
            if tag not in tags:
                updated_tags = knowledge_card_dao.update_tags(card_id=card_id, tag=tag)
                if updated_tags is None:
                    raise HTTPException(status_code=500, detail="Failed to update tags.")
                
                return {"status_code": 200, "message": "Tag added successfully.", "tags": updated_tags}
            else:
                return {"status_code": 400, "message": "Tag already exists.", "tags": tags}
        
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error adding tag: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    def remove_tag(self, card_id: str, user_id: str, tag: str):
        """
        Remove a tag from a specific card.
        """
        try:
            card = knowledge_card_dao.get_card_by_id(card_id=card_id)
            
            if not card:
                raise HTTPException(status_code=404, detail="Card not found.")

            if str(card["user_id"]) != str(user_id):
                raise HTTPException(status_code=403, detail="Unauthorized: Not the card owner.")

            tags = card.get("tags", [])
            if tag in tags:
                updated_tags = knowledge_card_dao.remove_tag(card_id=card_id, tag=tag)
                if updated_tags is None:
                    raise HTTPException(status_code=500, detail="Failed to update tags.")
                
                return {"status_code": 200, "message": "Tag removed successfully.", "tags": updated_tags}
            else:
                return {"status_code": 400, "message": "Tag does not exist.", "tags": tags}
        
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error removing tag: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    def get_dashboard_data(self, user_id: str):
        """
        Usage: Get dashboard data for a specific user.
        Parameters: user_id (str): The ID of the user whose dashboard data is to be retrieved.
        Returns: dict: A dictionary containing the dashboard data.
        """
        try:
            dashboard_data = knowledge_card_dao.get_dashboard_data(user_id=user_id)
            return dashboard_data

        except Exception as exception:
            print(f"Error getting dashboard data: {exception}")
            return None
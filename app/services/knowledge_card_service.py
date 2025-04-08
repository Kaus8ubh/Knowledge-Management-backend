from fastapi.responses import StreamingResponse
from utils import decode_access_token, scraper, embedder_for_title, gemini_text_processor, get_thumbnail, is_youtube_url, get_video_id, get_yt_transcript_text, pdf_docx_generator
from models import knowledge_card_model, KnowledgeCardRequest
from dao import knowledge_card_dao
from services.card_cluster_service import ClusteringServices
import io

class KnowledgeCardService:

    def get_all_cards(self, token:str):
        """
        Usage: Retrieve all knowledge cards for a specific user.
        Parameters: token (str): The access token of the user whose cards are to be retrieved.
        Returns: list: A list of knowledge cards.
        """
        try:
            decoded_token = decode_access_token(token)
            user_id = decoded_token["userId"]

            all_cards = knowledge_card_dao.get_all_cards(user_id)
              
            return [card.dict() for card in all_cards] if all_cards else [] # Convert each card to a dictionary

        except Exception as exception:
            print(f"Error getting knowledge cards: {exception}")
            return None
        
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
            note = knowledge_card_data.note
            thumbnail = get_thumbnail()
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
                embedding = embedder_for_title.embed_text(title)
                print("embedding done")
                
            else:
                title="Untitled"
                summary="No Summary Found"
                tags=[]
                embedding=[]
                source_url=""

            # insert the data 
            result =  knowledge_card_dao.insert_knowledge_card(
                user_id=user_id,
                title=title,
                summary=summary,
                tags=tags,
                note=note,
                embedding=embedding,
                source_url=source_url,
                thumbnail=thumbnail,
                favourite= False,
                archive= False
            )

            clustering = ClusteringServices.cluster_knowledge_cards(user_id)
            print("proceeding for clustering")
            return result

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

            result = knowledge_card_dao.update_card_details(card_id=card_id,user_id=user_id,updates=updates)

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

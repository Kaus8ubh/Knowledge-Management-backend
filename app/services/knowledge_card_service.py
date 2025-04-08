from utils import decode_access_token, scraper, embedder_for_title, gemini_text_processor, get_thumbnail, is_youtube_url, get_video_id, get_yt_transcript_text
from models import knowledge_card_model, KnowledgeCardRequest
from dao import knowledge_card_dao
from services.card_cluster_service import ClusteringServices

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
            card_details = []
            for card in all_cards:
                card_details.append({
                    "card_id": card.card_id,
                    "user_id":card.user_id,
                    "title": card.title,
                    "summary": card.summary,
                    "note": card.note,
                    "tags":card.tags,
                    "created_at":card.created_at,
                    "embedded_vector":card.embedded_vector,
                    "source_url": card.source_url,
                    "thumbnail": card.thumbnail,
                    "favourite": card.favourite,
                    "archive": card.archive
                })   
            return card_details

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

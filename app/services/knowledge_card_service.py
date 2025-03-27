from utils import decode_access_token
from models import knowledge_card_model
from dao import knowledge_card_dao

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
        



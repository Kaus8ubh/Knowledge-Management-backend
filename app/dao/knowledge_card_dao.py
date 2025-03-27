from bson import ObjectId
from datetime import datetime
from database import db_instance
from models import KnowledgeCard

class KnowledgeCardDao:
    def __init__(self):
        """        
        Initialize the KnowledgeCardDao with a reference to the knowledge cards collection.
        """
        self.knowledge_cards_collection = db_instance.get_collection("knowledge_cards_collection")

    def get_all_cards(self,user_id:str):
        """
        Usage: Retrieve all knowledge cards for a specific user.
        Parameters: user_id (str): The ID of the user whose cards are to be retrieved.
        Returns: list: A list of knowledge cards.
        """
        try:
            cards = self.knowledge_cards_collection.find({"user_id": ObjectId(user_id)})
            
            return [
                KnowledgeCard(
                    card_id=str(card["_id"]),
                    user_id=str(card["user_id"]),
                    title=card.get("title", ""),
                    summary=card.get("summary", ""),
                    tags=card.get("tags", []),
                    note=card.get("note", ""),
                    created_at=card.get("created_at", ""),
                    embedded_vector=card.get("embedded_vector", []),
                    source_url=card.get("source_url", ""),
                    thumbnail=card.get("thumbnail",""),
                    favourite=card.get("favourite", False),
                    archive=card.get("archive",False)
                )
                for card in cards
            ]
        
        except Exception as exception:
            print(f"An error occurred: {exception}")
            return None
        
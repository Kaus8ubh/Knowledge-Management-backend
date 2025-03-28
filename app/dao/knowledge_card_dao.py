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
        
    def insert_knowledge_card(self, user_id: str, title: str, summary: str, tags: list, note: str, embedding: list,
                              source_url: str, thumbnail: str, favourite: bool, archive: bool):
        """
        Usage:Insert a knowledge card into MongoDB"
        Parameters:
            user_id (str): The ID of the user who owns this knowledge card
            title (str): The title of the knowledge card
            summary (str): A summary of the content
            tags (list): A list of tags associated with the content
            note (str): Additional notes about the content
            embedding (list): Vector representation of the title for semantic search
            source_url (str): Original source URL of the content
        Returns:
            str: The ID of the inserted knowledge card
        """
        try:
            knowledge_card = {
                "user_id": ObjectId(user_id),
                "title": title,
                "summary": summary,
                "tags": tags,
                "note": note,
                "created_at": datetime.utcnow().isoformat(),
                "embedded_vector": embedding,
                "source_url": source_url,
                "thumbnail": thumbnail,
                "favourite": favourite,
                "archive": archive
            }
            self.knowledge_cards_collection.insert_one(knowledge_card)
            return title

        except Exception as exception:
            print(f"An error occurred: {exception}")
            return None
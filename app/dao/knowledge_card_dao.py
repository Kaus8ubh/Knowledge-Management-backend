from bson import ObjectId
from datetime import datetime
from database import db_instance
from models import KnowledgeCard
from utils import to_knowledge_card

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
                to_knowledge_card(card)  # Convert each card to a KnowledgeCard object
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
        
    def update_card_details(self, card_id:str, user_id:str, updates:dict):
        """
        Usage: Retrieve a specific card by its id.
        Parameters: card_id (str): The ID of the card.
        Returns: Details of a knowledge cards.
        """
        try:
            if not ObjectId.is_valid(card_id) or not ObjectId.is_valid(user_id):
                return "Invalid card ID or user ID."

            result = self.knowledge_cards_collection.update_one(
                {"user_id": ObjectId(user_id), "_id": ObjectId(card_id)},  # Filter by card ID
                {"$set": updates}  # Apply updates
        )
            if result.modified_count > 0:
                return "Knowledge card updated successfully."
            else:
                return "No changes made or card not found."
        
        except Exception as exception:
            print(f"An error occurred: {exception}")
            return "Failed to update the knowledge card."
        
    def get_cards_by_user(self, user_id: str ):
        """
        Usage: Get all knowledge cards for a user
        Parameter: user_id: The user ID to get cards for
        Returns: List of knowledge cards
        """
        try:
            user_id = ObjectId(user_id)
            return list(self.knowledge_cards_collection.find({"user_id": user_id}))
        except Exception as exception:
            print(f"Error getting cards: {exception}")
            return []
        
    def get_card_by_id(self, card_id: str):
        """
        Usage: Get a knowledge card by ID
        Parameter: card_id: The card ID to get           
        Returns: Knowledge card document or None
        """
        try:
            card_id = ObjectId(card_id)
            return self.knowledge_cards_collection.find_one({"_id": card_id})
        except Exception as e:
            print(f"Error getting card: {e}")
            return None
        
    def toggle_favourite(self, card_id: str):
        """
        Usage: Toggle the favourite status of a knowledge card.
        Parameters:
            card_id (str): The ID of the card to be toggled.
            user_id (str): The ID of the user who owns the card.
        Returns:
            str: A message indicating the result of the operation.
        """
        try:
            card_id = ObjectId(card_id)
            # Check if the card exists
            card = self.knowledge_cards_collection.find_one({"_id": card_id})
            if not card:
                return "Card not found."

            # Toggle the favourite status
            new_favourite_status = not card.get("favourite", False)
            self.knowledge_cards_collection.update_one(
                {"_id": card_id},
                {"$set": {"favourite": new_favourite_status}}
            )
            return "Favourite status updated successfully."
        
        except Exception as exception:
            print(f"An error occurred: {exception}")
            return "Failed to toggle favourite status."
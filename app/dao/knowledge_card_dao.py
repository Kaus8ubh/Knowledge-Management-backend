from bson import ObjectId
from datetime import datetime

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from database import db_instance
from models import KnowledgeCard
from utils import to_knowledge_card

class KnowledgeCardDao:
    def __init__(self):
        """        
        Initialize the KnowledgeCardDao with a reference to the knowledge cards collection.
        """
        self.knowledge_cards_collection = db_instance.get_collection("knowledge_cards_collection")

    def get_all_cards(self,user_id:str, skip: int = 0, limit: int = 4):
        """
        Usage: Retrieve all knowledge cards for a specific user.
        Parameters: user_id (str): The ID of the user whose cards are to be retrieved.
        Returns: list: A list of knowledge cards.
        """
        try:
            cards = self.knowledge_cards_collection.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).skip(skip).limit(limit)
            
            return [
                to_knowledge_card(card)
                for card in cards
            ]
        
        except Exception as exception:
            print(f"An error occurred: {exception}")
            return None
    
    def get_all_cards_no_limit(self, user_id: str):
        """
        Retrieve all knowledge cards for a specific user with no pagination.
        """
        try:
            cards = self.knowledge_cards_collection.find({"user_id": ObjectId(user_id)}).sort("created_at", -1)
            return [to_knowledge_card(card) for card in cards]
        except Exception as exception:
            print(f"An error occurred: {exception}")
            return None

    def get_favourite_cards(self, user_id: str, skip: int = 0, limit: int = 4):
        try:
            cards = self.knowledge_cards_collection.find({
                "user_id": ObjectId(user_id),
                "favourite": True
            }).sort("created_at", -1).skip(skip).limit(limit)

            return [to_knowledge_card(card) for card in cards]
        except Exception as exception:
            print(f"An error occurred: {exception}")
            return None

    def get_archived_cards(self, user_id: str, skip: int = 0, limit: int = 4):
        try:
            cards = self.knowledge_cards_collection.find({
                "user_id": ObjectId(user_id),
                "archive": True
            }).sort("created_at", -1).skip(skip).limit(limit)

            return [to_knowledge_card(card) for card in cards]
        except Exception as exception:
            print(f"An error occurred: {exception}")
            return None

    def get_all_public_cards(self):
        """
        Usage: Retrieve all public knowledge cards.
        Returns: list: A list of public knowledge cards.
        """
        try:
            cards = self.knowledge_cards_collection.find({"public": True})
            return [
                to_knowledge_card(card)  # Convert each card to a KnowledgeCard object
                for card in cards
            ]
        except Exception as exception:
            print(f"An error occurred: {exception}")
            return []
    
    def insert_knowledge_card(self,card: KnowledgeCard):
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
            knowledge_card = card.dict()
            knowledge_card["user_id"]=ObjectId(card.user_id)
            # knowledge_card["created_at"]=datetime.utcnow.isoformat()

            result = self.knowledge_cards_collection.insert_one(knowledge_card)
            inserted_id = result.inserted_id
            new_card = self.knowledge_cards_collection.find_one({"_id": inserted_id})
            return to_knowledge_card(new_card)
        except Exception as exception:
            print(f"An error occurred: {exception}")
            return None
        
    def update_card_details(self, card_id:str, updates:dict):
        """
        Usage: Retrieve a specific card by its id.
        Parameters: card_id (str): The ID of the card.
        Returns: Details of a knowledge cards.
        """
        try:
            if not ObjectId.is_valid(card_id):
                return "Invalid card ID or user ID."

            result = self.knowledge_cards_collection.update_one(
                {"_id": ObjectId(card_id)},  # Filter by card ID
                {"$set": updates}  
        )
            if result.modified_count > 0:
                return "Knowledge card updated successfully."
            else:
                return "No changes made or card not found."
        
        except Exception as exception:
            print(f"An error occurred: {exception}")
            return "Failed to update the knowledge card."
        
    def update_copied_by_list(self, card_id:str, copied_by_list:list):
        """
        Usage: Retrieve a specific card by its id.
        Parameters: card_id (str): The ID of the card.
        Returns: Details of a knowledge cards.
        """
        try:
            if not ObjectId.is_valid(card_id):
                return "Invalid card ID or user ID."

            result = self.knowledge_cards_collection.update_one(
                {"_id": ObjectId(card_id)},  # Filter by card ID
                {"$set": {"copied_by": copied_by_list}}  
        )
            if result.modified_count > 0:
                return "list updated successfully."
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
            result = self.knowledge_cards_collection.find_one({"_id": card_id})
            return result
        except Exception as exception:
            print(f"Error getting card: {exception}")
            return None
        
    def toggle_favourite(self, card_id: str):
        """
        Usage: Toggle the favourite status of a knowledge card.
        Parameters:
            card_id (str): The ID of the card to be toggled.
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
        
    def toggle_archive(self, card_id: str):
        """
        Usage: Toggle the favourite status of a knowledge card.
        Parameters:
            card_id (str): The ID of the card to be toggled.
        Returns:
            str: A message indicating the result of the operation.
        """
        try:
            card_id = ObjectId(card_id)
            # Check if the card exists
            card = self.knowledge_cards_collection.find_one({"_id": card_id})
            if not card:
                return "Card not found."

            # Toggle the archive status
            new_archive_status = not card.get("archive", False)
            self.knowledge_cards_collection.update_one(
                {"_id": card_id},
                {"$set": {"archive": new_archive_status}}
            )
            if new_archive_status:
                return "Card Archived"
            return "Card Unarchived"
        
        except Exception as exception:
            print(f"An error occurred: {exception}")
            return "Failed to move to archives."
        
    def toggle_public(self, card_id: str):
        """
        Usage: Toggle the public status of a knowledge card.
        Parameters:
            card_id (str): The ID of the card to be toggled.
        Returns:
            str: A message indicating the result of the operation.
        """
        try:
            card_id = ObjectId(card_id)
            # Check if the card exists
            card = self.knowledge_cards_collection.find_one({"_id": card_id})
            if not card:
                raise HTTPException(status_code=404, detail={"message": "Card not found"})

            # Toggle the public status
            new_public_status = not card.get("public", False)
            self.knowledge_cards_collection.update_one(
                {"_id": card_id},
                {"$set": {"public": new_public_status}}
            )
            return JSONResponse(status_code=200, content={"message": "Card made public" if new_public_status else "Card made private"})
        
        except Exception as exception:
            print(f"An error occurred: {exception}")
            return "Failed to move to global."
    
    def delete_card(self, card_id: str):
        """
        Usage: Delete a knowledge card by ID.
        Parameters:
            card_id (str): The ID of the card to be deleted.
        Returns:
            str: A message indicating the result of the operation.
        """
        try:
            card_id = ObjectId(card_id)
            result = self.knowledge_cards_collection.delete_one({"_id": card_id})
            if result.deleted_count > 0:
                return "Knowledge card deleted successfully."
            else:
                return "Card not found."
        
        except Exception as exception:
            print(f"An error occurred: {exception}")
            return "Failed to delete the knowledge card."
        
    def remove_user_from_copied_by(self, original_card_id: str, user_id: str):
        """
        Removes a user from the copied_by list of the original card.
        """
        try:
            if not ObjectId.is_valid(original_card_id):
                return "Invalid original card ID."

            self.knowledge_cards_collection.update_one(
                {"_id": ObjectId(original_card_id)},
                {"$pull": {"copied_by": user_id}}
            )
            return "User removed from copied_by list."
        except Exception as e:
            print(f"Failed to remove user from copied_by: {e}")
            return "Failed to update original card."

        
    def update_card_shared_token(self, card_id: str, token: str):
        try:
            return self.knowledge_cards_collection.update_one(
                {"_id": ObjectId(card_id)},
                {"$set": {
                    "shared_token": token
                    }
                }
            )
        except Exception as exception:
            print(f"An error occured: {exception}")
            return "failed to generate shareable LINK"
        
    def update_qna(self, card_id: str, qna: dict):
        try:
            result = self.knowledge_cards_collection.update_one(
                {"_id": ObjectId(card_id)},
                {"$set": {
                    "qna": qna
                    }
                }
            )
            return result.modified_count > 0
        except Exception as exception:
            print(f"An error occured: {exception}")
            return "failed to update qna"
        
    def update_map(self, card_id: str, knowledge_map: dict):
        try:
            result = self.knowledge_cards_collection.update_one(
                {"_id": ObjectId(card_id)},
                {"$set": {
                    "knowledge_map": knowledge_map
                    }
                }
            )
            return result.modified_count > 0
        except Exception as exception:
            print(f"An error occured: {exception}")
            return "failed to update map"
    
    def get_card_by_token(self, token: str):
        try:
            card = self.knowledge_cards_collection.find_one({"shared_token": token})
            return to_knowledge_card(card=card)
        except Exception as exception:
            print(f"erron finding token for sharing: {exception}")

    def like_a_card(self, card_id: str, likes: int, liked_by: list):
        try:
            return self.knowledge_cards_collection.update_one(
                {"_id": ObjectId(card_id)},
                {"$set": {
                    "likes": likes,
                    "liked_by": liked_by
                }}
            )
        except Exception as exception:
            print(f"Error while liking the Card: {exception}")
            return None
        
    def unlike_a_card(self, card_id: str, likes: int, liked_by: list):
        try:
            return self.knowledge_cards_collection.update_one(
                {"_id": ObjectId(card_id)},
                {"$set":{
                    "likes":likes,
                    "liked_by":liked_by
                }}
            )
        except Exception as exception:
            print(f"Error while unliking the card: {exception}")

    def bookmark_a_card(self, card_id: str, user_id: str):
        try:
            return self.knowledge_cards_collection.update_one(
                {"_id": ObjectId(card_id)},
                {"$addToSet": {
                    "bookmarked_by": user_id
                }}
            )
        except Exception as exception:
            print(f"Error while bookmarking the card: {exception}")
            return None
        
    def unbookmark_a_card(self, card_id: str, user_id: str):
        try:
            return self.knowledge_cards_collection.update_one(
                {"_id": ObjectId(card_id)},
                {"$pull": {
                    "bookmarked_by": user_id
                }}
            )
        except Exception as exception:
            print(f"Error while unbookmarking the card: {exception}")
            return None
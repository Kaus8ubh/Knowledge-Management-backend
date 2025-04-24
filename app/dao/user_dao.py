from datetime import datetime, timezone
from fastapi import HTTPException
from database import db_instance
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError
from utils import DatabaseError, NotFoundError
from bson import ObjectId

class UserDAO:

    
    def __init__(self):
        """
        Usage: This class is used to interact with the users_collection in the MongoDB database
        params: None
        return: None
        """
        try:
            self.users_collection = db_instance.get_collection("users_collection")
        except ConnectionFailure as connection_failure:
            print("Unable to connect to users_collection", connection_failure)
            self.users_collection = None
            raise DatabaseError("Unable to connect to users_collection", 500) from connection_failure

    
    def find_user_by_email(self, email: str):
        """
        Usage: This function is used to fetch user from the users_collection by email
        Params: email str
        Return: user dict
        """
        try:
            existing_user = self.users_collection.find_one({"email": email})
            return existing_user
        except OperationFailure as operation_failure:
            raise DatabaseError("Failed to fetch user from database.", 500) from operation_failure
        
    def get_user_by_id(self, user_id: str):
        """
        Usage: Get a user by ID
        Parameter: user_id: The user ID to get
        Returns: User document or None
        """
        try:
            user_id = ObjectId(user_id)
            return self.users_collection.find_one({"_id": user_id})
        except Exception as exception:
            print(f"Error getting user: {exception}")
            return None
    
    
    def update_existing_user_last_login(self, email: str):
        """
        Usage: This function is used to update the last_login field of the user in the users_collection by email
        Params: email str
        Return: None
        """
        try:
            self.users_collection.update_one({"email": email}, {"$set": {"last_login": datetime.utcnow().isoformat()}})
        except OperationFailure as operation_failure:
            raise DatabaseError("Couldn't update user's last login.", 500) from operation_failure
        
        
    def create_user(self, user_data: dict):
        """
        Usage: This function is used to create user in the users_collection
        Params: user_data dict
        Return: inserted_id str
        """
        try:
            user_data.created_at = datetime.now(timezone.utc).isoformat()
            user_data.last_login = datetime.now(timezone.utc).isoformat()
            result = self.users_collection.insert_one(user_data.model_dump())
            return str(result.inserted_id)
        except PyMongoError as error:
            print("Error creating user: ", error)
            raise HTTPException(status_code=500, detail={"message": "Error creating user"})
        
    def add_bookmarked_card(self, user_id: str, card_id: str):
        """
        Usage: This function is used to add a bookmarked card to the user's bookmarks
        Params: user_id str, card_id str
        Return: None
        """
        try:
            return self.users_collection.update_one({"_id": ObjectId(user_id)}, {"$addToSet": {"bookmarked_cards": card_id}})
        except OperationFailure as operation_failure:
            raise DatabaseError("Couldn't add bookmarked card.", 500) from operation_failure
        
    def remove_bookmarked_card(self, user_id: str, card_id: str):
        """
        Usage: This function is used to remove a bookmarked card from the user's bookmarks
        Params: user_id str, card_id str
        Return: None
        """
        try:
            return self.users_collection.update_one({"_id": ObjectId(user_id)}, {"$pull": {"bookmarked_cards": card_id}})
        except OperationFailure as operation_failure:
            raise DatabaseError("Couldn't remove bookmarked card.", 500) from operation_failure
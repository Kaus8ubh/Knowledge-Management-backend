from pymongo import MongoClient
from config import Config

class Database:
    def __init__(self):
        """
        Usage: This class is used to connect to the MongoDB database
        params: None
        return: None
        """
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client["brieffydb"]
        self.users_collection = self.db["users_collection"]
        self.knowledge_cards_collection = self.db["knowledge_cards_collection"]
        self.clusters_collection = self.db["clusters_collection"]

    def get_collection(self, collection_name):
        """
        Usage: This function is used to get the collection from the database
        params: collection_name str
        return: collection object
        """
        return self.db[collection_name]
    
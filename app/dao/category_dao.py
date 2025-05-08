from app.database import db_instance
from datetime import datetime

class CategoryDAO:
    def __init__(self):
        self.collection = db_instance.get_collection('categories')

    def find_by_name(self, name: str):
        """Find a category by name."""
        return self.collection.find_one({"name": name})

    def insert_category(self, name: str, created_by: str):
        """Insert a new category."""
        new_category = {
            "name": name,
            "created_by": created_by,
            "created_at": datetime.utcnow()
        }
        return self.collection.insert_one(new_category)

    def get_all_categories(self):
        """Get all categories."""
        return list(self.collection.find({}, {"_id": 0, "name": 1}).sort("name", 1))

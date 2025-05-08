from app.dao.category_dao import CategoryDAO

class CategoryService:
    def __init__(self):
        self.dao = CategoryDAO()

    def add_category_if_not_exists(self, name: str, created_by: str):
        """Add a category only if it doesn't already exist."""
        existing = self.dao.find_by_name(name)
        if existing:
            return existing  
        else:
            return self.dao.insert_category(name, created_by)

    def get_available_categories(self):
        """Get all available categories."""
        return self.dao.get_all_categories()

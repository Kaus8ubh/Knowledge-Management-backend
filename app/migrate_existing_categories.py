from database import db_instance
from datetime import datetime

def migrate_existing_categories():
    
    cards_collection = db_instance.get_collection("knowledge_cards_collection")
    categories_collection = db_instance.get_collection('categories')

    # Step 1: Extract all categories
    all_cards = cards_collection.find({"category": {"$exists": True}})
    category_set = set()

    for card in all_cards:
        categories = card.get('category', [])
        if isinstance(categories, list):
            category_set.update(categories)
        elif isinstance(categories, str):  # in case some old documents still have string
            category_set.add(categories)

    print(f"Found {len(category_set)} unique categories.")

    # Step 2: Insert into categories collection (only if not already existing)
    for category_name in category_set:
        existing = categories_collection.find_one({"name": category_name})
        if not existing:
            new_category = {
                "name": category_name,
                "created_by": "system",  # since it's migrated
                "created_at": datetime.utcnow()
            }
            categories_collection.insert_one(new_category)
            print(f"Inserted category: {category_name}")
        else:
            print(f"Category already exists: {category_name}")

    print("🎉 Migration complete.")



migrate_existing_categories()

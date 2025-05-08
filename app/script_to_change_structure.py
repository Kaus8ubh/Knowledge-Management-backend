# to change the data type of the "category" which is currently "string" to "list" (array of categories)
from app.database import db_instance

def migrate_category_field():
    
    knowledge_cards_collection = db_instance.get_collection("knowledge_cards_collection")

    result = knowledge_cards_collection.update_many(
        {'category': {'$exists': True, '$type': 'string'}},
        [{'$set': {'category': {'$cond': [{'$isArray': '$category'}, '$category', ['$category']]}}}]
    )

    print(f'Migration complete. Updated {result.modified_count} documents.')


migrate_category_field()
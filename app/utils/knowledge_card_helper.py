from models import KnowledgeCard


def to_knowledge_card(card) -> KnowledgeCard:
    return KnowledgeCard(
        card_id=str(card["_id"]),
        user_id=str(card["user_id"]),
        title=card.get("title"),
        summary=card.get("summary"),
        tags=card.get("tags",[]),
        note=card.get("note"),
        created_at=card.get("created_at"),
        embedded_vector=card.get("embedded_vector",[]),
        source_url=card.get("source_url"),
        thumbnail=card.get("thumbnail"),
        favourite=card.get("favourite", False),
        archive=card.get("archive", False),
        category=card.get("category", "Misc"),
        shared_token=card.get("shared_token"),
        public=card.get("public", False),
        likes=card.get("likes", 0),
        liked_by=card.get("liked_by") or [],
        copied_by=card.get("copied_by") or [],
        copied_from=str(card.get("copied_from")) if card.get("copied_from") else None
    )
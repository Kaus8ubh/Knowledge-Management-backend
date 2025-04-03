from .user_dao import UserDAO
from .knowledge_card_dao import KnowledgeCardDao

user_dao = UserDAO()
knowledge_card_dao = KnowledgeCardDao()

__all__ = ["user_dao","knowledge_card_dao"]


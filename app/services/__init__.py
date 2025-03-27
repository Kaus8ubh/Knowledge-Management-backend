from .auth_service import AuthService
from .knowledge_card_service import KnowledgeCardService

auth_service = AuthService()
knowledge_card_service = KnowledgeCardService()

__all__ =["auth_service", "knowledge_card_service"]

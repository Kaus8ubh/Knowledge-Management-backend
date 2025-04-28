from .auth_service import AuthService
from .knowledge_card_service import KnowledgeCardService
from .card_cluster_service import ClusteringServices
from .category_services import CategoryService

auth_service = AuthService()
knowledge_card_service = KnowledgeCardService()
card_cluster_service = ClusteringServices()
category_service = CategoryService()

__all__ =["auth_service", "knowledge_card_service", "card_cluster_service", "category_service"]
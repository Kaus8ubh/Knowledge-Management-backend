from .user_dao import UserDAO
from .knowledge_card_dao import KnowledgeCardDao
from .card_cluster_dao import ClusterDao

user_dao = UserDAO()
knowledge_card_dao = KnowledgeCardDao()
card_cluster_dao = ClusterDao()

__all__ = ["user_dao","knowledge_card_dao", "card_cluster_dao"]


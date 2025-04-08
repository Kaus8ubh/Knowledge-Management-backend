from pydantic import BaseModel
from typing import Optional, List

class CardCluster(BaseModel):
    cluster_id: str
    user_id: str
    centroid_vector: List[float]
    knowledge_card_ids: List[str]
    topic_name: Optional[str] = None
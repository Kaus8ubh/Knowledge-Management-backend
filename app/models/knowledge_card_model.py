from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class KnowledgeCard(BaseModel):
    card_id: Optional[str]=None
    user_id: str
    title: Optional[str]
    summary: Optional[str]
    tags: Optional[list]
    note: Optional[str]
    created_at: datetime
    embedded_vector: Optional[list]
    source_url: Optional[str]
    thumbnail:Optional[str]
    favourite: Optional[bool]
    archive: Optional[bool]
    category: Optional[str]
    shared_token: Optional[str]=None
    public: Optional[bool]=False
    likes: Optional[int]=0
    liked_by:Optional[list]=[]
    copied_by:Optional[list]=[]
    copied_from: Optional[str] = None
    bookmarked_by: Optional[list] = []

class PublicKnowledgeCard(KnowledgeCard):
    liked_by_me: bool = False

class KnowledgeCardRequest(BaseModel):
    token: str
    source_url: Optional[str]
    note: Optional[str]

class EditKnowledgeCard(BaseModel):
    card_id: str
    user_id: str
    summary: Optional[str]
    note: Optional[str]
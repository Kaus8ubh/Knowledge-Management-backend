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
    public: Optional[bool]=None

class KnowledgeCardRequest(BaseModel):
    token: str
    source_url: Optional[str]
    note: Optional[str]

class EditKnowledgeCard(BaseModel):
    card_id: str
    user_id: str
    summary: Optional[str]
    note: Optional[str]
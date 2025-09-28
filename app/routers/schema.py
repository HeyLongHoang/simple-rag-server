from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BuildIndexRequest(BaseModel):
    index_name: str
    documents_path: str = "./data"

class BuildIndexResponse(BaseModel):
    index_name: str
    status: str
    message: Optional[str] = None

class QueryIndexRequest(BaseModel):
    index_name: str
    query: str
    similarity_top_k: Optional[int] = 5

class QueryIndexResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = []

class IndexStatusResponse(BaseModel):
    index_name: str
    loaded: bool
    last_accessed: Optional[datetime] = None
    storage_path: str


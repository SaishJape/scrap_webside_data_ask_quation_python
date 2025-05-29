from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class URLInput(BaseModel):
    url: str

class ChatInput(BaseModel):
    query: str
    session_id: str

class ChunkData(BaseModel):
    text: str
    url: str
    chunk_index: int
    timestamp: str
    chunk_size: int
    chunk_length: int

class SearchResult(BaseModel):
    text: str
    url: str
    score: float
    metadata: Dict[str, Any] = {}

class ProcessingStats(BaseModel):
    total_chunks: int
    average_chunk_size: float
    total_words: int
    processed_urls: int
    total_urls_found: int
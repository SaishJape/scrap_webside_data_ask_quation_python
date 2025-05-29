from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.utils.logger import logger
from app.db.models import SearchResult
from typing import List
import datetime
import uuid

class QdrantService:
    def __init__(self):
        try:
            self.client = QdrantClient(
                url=settings.qdrant_url,
                timeout=settings.qdrant_timeout,
                prefer_grpc=settings.qdrant_prefer_grpc
            )
            self.model = SentenceTransformer(settings.sentence_transformer_model)
            logger.info("Successfully connected to Qdrant server")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant server: {str(e)}")
            raise Exception("Could not connect to Qdrant server. Please ensure it's running at http://localhost:6333")
    
    def get_collection_name(self, session_id: str) -> str:
        """Generate a collection name for a session."""
        return f"session_{session_id}_data"
    
    async def create_session_collection(self, session_id: str) -> None:
        """Create a new collection for a session if it doesn't exist."""
        collection_name = self.get_collection_name(session_id)
        try:
            collections = self.client.get_collections()
            collection_exists = any(col.name == collection_name for col in collections.collections)
            
            if not collection_exists:
                logger.info(f"Creating collection for session {session_id}")
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=settings.vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Successfully created collection for session {session_id}")
        except Exception as e:
            logger.error(f"Error creating collection for session {session_id}: {str(e)}")
            raise Exception(f"Error creating session collection: {str(e)}")
    
    async def session_exists(self, session_id: str) -> bool:
        """Check if a session collection exists."""
        collection_name = self.get_collection_name(session_id)
        try:
            collections = self.client.get_collections()
            return any(col.name == collection_name for col in collections.collections)
        except Exception as e:
            logger.error(f"Error checking session existence: {str(e)}")
            return False
    
    async def store_chunks(self, session_id: str, chunks: List[str], url: str) -> int:
        """Store text chunks as embeddings."""
        collection_name = self.get_collection_name(session_id)
        
        if not chunks:
            return 0
        
        try:
            # Generate embeddings
            embeddings = self.model.encode(chunks)
            
            # Prepare points
            points = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point_id = str(uuid.uuid4())
                points.append(models.PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload={
                        "text": chunk,
                        "url": url,
                        "chunk_index": i,
                        "timestamp": str(datetime.datetime.now()),
                        "chunk_size": len(chunk.split()),
                        "chunk_length": len(chunk)
                    }
                ))
            
            # Store points
            if points:
                self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                return len(points)
            
            return 0
            
        except Exception as e:
            logger.error(f"Error storing chunks: {str(e)}")
            raise
    
    async def search_similar(self, session_id: str, query: str) -> List[SearchResult]:
        """Search for similar chunks."""
        collection_name = self.get_collection_name(session_id)
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode(query)
            
            # Search for relevant chunks
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding.tolist(),
                limit=settings.search_limit
            )
            
            # Convert to SearchResult objects
            results = []
            for hit in search_results:
                results.append(SearchResult(
                    text=hit.payload["text"],
                    url=hit.payload["url"],
                    score=hit.score,
                    metadata=hit.payload
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar chunks: {str(e)}")
            return []
from fastapi import APIRouter, HTTPException
from app.db.models import URLInput, ChatInput
from app.services.gemini import GeminiService
from app.db.quadrant import QdrantService
from app.utils.logger import logger
from app.utils.common import get_all_website_urls, process_website_content
import datetime
import uuid

router = APIRouter()

# Initialize services
gemini_service = GeminiService()
qdrant_service = QdrantService()

@router.post("/embed")
async def embed_chunks(input_data: URLInput):
    try:
        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        logger.info(f"Generated new session ID: {session_id}")
        
        # Validate URL
        if not input_data.url.startswith(('http://', 'https://')):
            return {
                "status": "error",
                "message": "Invalid URL format",
                "details": "URL must start with http:// or https://",
                "timestamp": str(datetime.datetime.now())
            }
        
        # Create session collection
        await qdrant_service.create_session_collection(session_id)
        
        # Get all URLs from the website
        all_urls = get_all_website_urls(input_data.url)
        logger.info(f"Found {len(all_urls)} pages to process")
        
        # Process website content
        result = await process_website_content(all_urls, session_id, qdrant_service)
        
        if result["total_chunks"] == 0:
            return {
                "status": "error",
                "message": "No content found",
                "details": "The website appears to be empty or contains no readable content",
                "timestamp": str(datetime.datetime.now())
            }
        
        return {
            "status": "success",
            "message": "Content successfully processed and stored",
            "data": {
                "session_id": session_id,
                "url": input_data.url,
                "statistics": result
            },
            "timestamp": str(datetime.datetime.now())
        }
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "status": "error",
            "message": "Internal server error",
            "details": str(e),
            "timestamp": str(datetime.datetime.now())
        }

@router.post("/chat")
async def chat(chat_input: ChatInput):
    try:
        logger.info(f"Processing chat query for session {chat_input.session_id}")
        
        # Check if session exists
        if not await qdrant_service.session_exists(chat_input.session_id):
            return {
                "status": "error",
                "message": "Invalid session",
                "details": "Session not found. Please initialize the chat by providing a URL first",
                "timestamp": str(datetime.datetime.now())
            }
        
        # Search for relevant chunks
        search_results = await qdrant_service.search_similar(
            chat_input.session_id, 
            chat_input.query
        )
        
        # Generate response using Gemini
        response_text = await gemini_service.generate_response(
            chat_input.query, 
            search_results
        )
        
        return {
            "status": "success",
            "message": "Response generated successfully",
            "data": {
                "session_id": chat_input.session_id,
                "query": chat_input.query,
                "response": response_text
            },
            "timestamp": str(datetime.datetime.now())
        }
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "status": "error",
            "message": "Internal server error",
            "details": str(e),
            "timestamp": str(datetime.datetime.now())
        }
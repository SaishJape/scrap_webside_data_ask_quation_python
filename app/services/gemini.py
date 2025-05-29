import google.generativeai as genai
from app.config import settings
from app.db.models import SearchResult
from app.utils.logger import logger
from typing import List

class GeminiService:
    def __init__(self):
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)
            logger.info("Successfully initialized Gemini service")
        except Exception as e:
            logger.error(f"Error initializing Gemini service: {str(e)}")
            raise
    
    async def generate_response(self, query: str, search_results: List[SearchResult]) -> str:
        """Generate a response using Gemini based on query and search results."""
        try:
            # Prepare context and prompt based on whether we found relevant content
            if search_results:
                context = "\n".join([result.text for result in search_results])
                prompt = f"""You are a helpful and friendly AI assistant. You have access to the following context from a website:

Context:
{context}

User Query: {query}

Please provide a helpful and conversational response. If the query is a greeting or general question, respond naturally. If the query is about the website content, use the context to provide accurate information. If the query is not related to the context, respond conversationally without mentioning the context."""
            else:
                prompt = f"""You are a helpful and friendly AI assistant. The user has asked:

{query}

Please provide a natural, conversational response. Be friendly and helpful in your reply."""
            
            # Generate response
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."
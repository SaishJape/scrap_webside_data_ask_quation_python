import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any
import nltk
from nltk.tokenize import sent_tokenize
from app.utils.logger import logger
from app.config import settings
import datetime

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    logger.info("Successfully downloaded NLTK data")
except Exception as e:
    logger.error(f"Error downloading NLTK data: {str(e)}")
    raise

def get_all_website_urls(base_url: str) -> set:
    """Crawl the website and get all unique URLs."""
    visited_urls = set()
    urls_to_visit = {base_url}
    base_domain = urlparse(base_url).netloc
    
    while urls_to_visit:
        current_url = urls_to_visit.pop()
        
        if current_url in visited_urls:
            continue
            
        try:
            response = requests.get(current_url)
            if response.status_code != 200:
                continue
                
            visited_urls.add(current_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(current_url, href)
                parsed_url = urlparse(absolute_url)
                
                # Only include URLs from the same domain
                if parsed_url.netloc == base_domain and absolute_url not in visited_urls:
                    urls_to_visit.add(absolute_url)
                    
        except Exception as e:
            logger.error(f"Error crawling {current_url}: {str(e)}")
            continue
            
    return visited_urls

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()

def format_chunk(chunk: str) -> str:
    """Format a text chunk by cleaning sentences."""
    sentences = sent_tokenize(chunk)
    cleaned_sentences = [clean_text(sentence) for sentence in sentences]
    cleaned_sentences = [s for s in cleaned_sentences if s]
    return ' '.join(cleaned_sentences)

def chunk_text(text: str, chunk_size: int = None) -> List[str]:
    """Split text into chunks."""
    if chunk_size is None:
        chunk_size = settings.chunk_size
        
    text = clean_text(text)
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        cleaned_sentence = clean_text(sentence)
        if not cleaned_sentence:
            continue
            
        sentence_size = len(cleaned_sentence.split())
        if current_size + sentence_size > chunk_size:
            if current_chunk:
                formatted_chunk = format_chunk(' '.join(current_chunk))
                if formatted_chunk:
                    chunks.append(formatted_chunk)
            current_chunk = [cleaned_sentence]
            current_size = sentence_size
        else:
            current_chunk.append(cleaned_sentence)
            current_size += sentence_size
    
    if current_chunk:
        formatted_chunk = format_chunk(' '.join(current_chunk))
        if formatted_chunk:
            chunks.append(formatted_chunk)
    
    return chunks

async def process_website_content(all_urls: set, session_id: str, qdrant_service) -> Dict[str, Any]:
    """Process all URLs and extract content."""
    total_chunks = 0
    total_words = 0
    processed_urls = 0
    
    # Process each URL
    for url in all_urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            text = clean_text(text)
            
            if not text:
                continue
            
            # Split into chunks
            chunks = chunk_text(text)
            
            if not chunks:
                continue
            
            # Store chunks using qdrant service
            stored_count = await qdrant_service.store_chunks(session_id, chunks, url)
            
            if stored_count > 0:
                total_chunks += stored_count
                total_words += sum(len(chunk.split()) for chunk in chunks)
                processed_urls += 1
            
        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")
            continue
    
    # Calculate statistics
    stats = {
        "total_chunks": total_chunks,
        "average_chunk_size": total_words / total_chunks if total_chunks > 0 else 0,
        "total_words": total_words,
        "processed_urls": processed_urls,
        "total_urls_found": len(all_urls)
    }
    
    return stats
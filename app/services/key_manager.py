# Handles all API key loading/rotation
import os
from app.config import settings
from app.utils.logger import logger
from typing import Optional, Dict, List
import random

class KeyManager:
    """Manages API keys with rotation and fallback capabilities."""
    
    def __init__(self):
        self.api_keys: Dict[str, List[str]] = {}
        self.current_key_index: Dict[str, int] = {}
        self._load_keys()
    
    def _load_keys(self):
        """Load API keys from environment variables."""
        # Load Gemini keys
        gemini_keys = []
        if settings.gemini_api_key:
            gemini_keys.append(settings.gemini_api_key)
        
        # Load additional keys from environment (if multiple keys are provided)
        for i in range(1, 10):  # Support up to 10 keys per service
            key = os.getenv(f"GEMINI_API_KEY_{i}")
            if key:
                gemini_keys.append(key)
        
        self.api_keys["gemini"] = gemini_keys
        self.current_key_index["gemini"] = 0
        
        # Add other services here
        self.api_keys["openai"] = self._load_service_keys("OPENAI_API_KEY")
        self.api_keys["claude"] = self._load_service_keys("CLAUDE_API_KEY")
        
        logger.info(f"Loaded {len(self.api_keys['gemini'])} Gemini keys")
    
    def _load_service_keys(self, base_key_name: str) -> List[str]:
        """Load keys for a specific service."""
        keys = []
        
        # Load primary key
        primary_key = os.getenv(base_key_name)
        if primary_key:
            keys.append(primary_key)
        
        # Load additional keys
        for i in range(1, 10):
            key = os.getenv(f"{base_key_name}_{i}")
            if key:
                keys.append(key)
        
        return keys
    
    def get_key(self, service: str) -> Optional[str]:
        """Get the current API key for a service."""
        if service not in self.api_keys or not self.api_keys[service]:
            logger.warning(f"No API keys available for service: {service}")
            return None
        
        keys = self.api_keys[service]
        current_index = self.current_key_index.get(service, 0)
        
        if current_index >= len(keys):
            self.current_key_index[service] = 0
            current_index = 0
        
        return keys[current_index]
    
    def rotate_key(self, service: str) -> Optional[str]:
        """Rotate to the next available key for a service."""
        if service not in self.api_keys or not self.api_keys[service]:
            return None
        
        keys = self.api_keys[service]
        current_index = self.current_key_index.get(service, 0)
        
        # Move to next key
        new_index = (current_index + 1) % len(keys)
        self.current_key_index[service] = new_index
        
        logger.info(f"Rotated {service} key to index {new_index}")
        return keys[new_index]
    
    def get_random_key(self, service: str) -> Optional[str]:
        """Get a random key for a service."""
        if service not in self.api_keys or not self.api_keys[service]:
            return None
        
        keys = self.api_keys[service]
        return random.choice(keys)
    
    def is_key_available(self, service: str) -> bool:
        """Check if any keys are available for a service."""
        return service in self.api_keys and len(self.api_keys[service]) > 0
    
    def get_key_count(self, service: str) -> int:
        """Get the number of available keys for a service."""
        return len(self.api_keys.get(service, []))

# Global key manager instance
key_manager = KeyManager()  
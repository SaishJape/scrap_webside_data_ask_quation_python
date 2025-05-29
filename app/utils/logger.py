import logging
import sys
from app.config import settings

# Configure logging
def setup_logger():
    """Set up the application logger."""
    logger = logging.getLogger(__name__)
    
    # Only add handler if it doesn't exist
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    return logger

# Create global logger instance
logger = setup_logger()
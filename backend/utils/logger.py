import logging
import sys
from core.config import get_settings

settings = get_settings()

# Configure logging
def setup_logger(name: str = "thumbnail_factory"):
    """Set up logger with appropriate formatting and handlers."""
    logger = logging.getLogger(name)
    
    # Prevent adding multiple handlers if logger already exists
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Create a default logger instance
logger = setup_logger()
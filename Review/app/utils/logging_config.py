import logging
import sys
from app.config import settings

def setup_logging():
    
    # Създаване на логгер
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Формат на логовете
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    try:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.error(f"Could not create log file: {e}")
    
    # Намали логването от библиотеки
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("jose").setLevel(logging.WARNING)
    
    logger.info("Logging configured successfully")
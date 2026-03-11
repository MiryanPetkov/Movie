import requests
import time
from config import settings
from database import get_db
import logging

logger = logging.getLogger(__name__)

class OMDbService:
    def __init__(self):
        self.api_key = settings.OMDB_API_KEY
        self.base_url = settings.OMDB_API_URL
        self.timeout = settings.OMDB_TIMEOUT
        self.retries = settings.OMDB_RETRIES
    
    def get_rating(self, title: str):
        """Взема рейтинг от OMDb API"""
        
        # Първо провери в кеша
        cached = self._get_from_cache(title)
        if cached:
            logger.info(f"Cache hit for '{title}': {cached}")
            return cached
        
        # Опитай с exponential backoff
        for attempt in range(self.retries):
            try:
                response = requests.get(
                    self.base_url,
                    params={
                        't': title,
                        'apikey': self.api_key,
                        'type': 'movie'
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 429:  # Rate limit
                    logger.error(f"Rate limit reached for '{title}'")
                    return None
                
                if response.status_code != 200:
                    logger.warning(f"OMDb returned {response.status_code} for '{title}'")
                    return None
                
                data = response.json()
                
                if data.get('Response') == 'False':
                    logger.warning(f"Movie not found: '{title}'")
                    return None
                
                # Вземи IMDb rating
                imdb_rating = data.get('imdbRating')
                if imdb_rating and imdb_rating != 'N/A':
                    rating = float(imdb_rating)
                    # Запази в кеша
                    self._save_to_cache(title, rating)
                    return rating
                
                return None
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed for '{title}': {str(e)}")
                
                if attempt < self.retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All attempts failed for '{title}'")
                    return None
        
        return None
    
    def _get_from_cache(self, title: str):
        """Взема рейтинг от кеша"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rating FROM rating_cache WHERE movie_title = ?",
            (title.lower(),)
        )
        result = cursor.fetchone()
        conn.close()
        
        return result['rating'] if result else None
    
    def _save_to_cache(self, title: str, rating: float):
        """Запазва рейтинг в кеша"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO rating_cache (movie_title, rating)
            VALUES (?, ?)
        """, (title.lower(), rating))
        conn.commit()
        conn.close()

# Singleton instance
omdb_service = OMDbService()
from app.services.omdb_service import omdb_service
from app.database import get_db
import logging

logger = logging.getLogger(__name__)

def enrich_movie_rating(movie_id: int, title: str):
    """Background task за обогатяване на рейтинг"""
    logger.info(f"Starting enrichment for movie {movie_id}: '{title}'")
    
    # Вземи рейтинг от OMDb
    rating = omdb_service.get_rating(title)
    
    # Обнови в базата
    conn = get_db()
    cursor = conn.cursor()
    
    if rating is not None:
        cursor.execute("""
            UPDATE movies 
            SET rating = ?, enrichment_status = 'success'
            WHERE id = ?
        """, (rating, movie_id))
        logger.info(f"Successfully enriched movie {movie_id} with rating {rating}")
    else:
        cursor.execute("""
            UPDATE movies 
            SET enrichment_status = 'failed'
            WHERE id = ?
        """, (movie_id,))
        logger.warning(f"Failed to enrich movie {movie_id}")
    
    conn.commit()
    conn.close()
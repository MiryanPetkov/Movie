from app.database import get_db
from app.models.movie import MovieCreate, MovieUpdate
from app.background.tasks import enrich_movie_rating
from typing import Optional
import math
import logging

logger = logging.getLogger(__name__)

def create_movie(movie_data: MovieCreate, background_tasks):
    """Създава нов филм в базата"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO movies (title, director, release_year, enrichment_status)
        VALUES (?, ?, ?, 'pending')
    """, (movie_data.title, movie_data.director, movie_data.release_year))
    
    movie_id = cursor.lastrowid
    conn.commit()
    
    # Вземи създадения филм
    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    new_movie = dict(cursor.fetchone())
    conn.close()
    
    # Пусни background task
    background_tasks.add_task(enrich_movie_rating, movie_id, movie_data.title)
    logger.info(f"Created movie {movie_id}: {movie_data.title}")
    
    return new_movie

def get_movies(search: Optional[str], sort: str, order: str, page: int, per_page: int):
    """Връща списък с филми (с филтриране, сортиране, пагинация)"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Базов WHERE клауза
    where_clause = ""
    params = []
    
    if search:
        where_clause = "WHERE title LIKE ? COLLATE NOCASE"
        params.append(f"%{search}%")
    
    # Брой резултати
    cursor.execute(f"SELECT COUNT(*) FROM movies {where_clause}", params)
    total = cursor.fetchone()[0]
    
    # Сортиране
    if sort == "rating":
        order_by = "rating IS NULL, rating"
    else:
        order_by = "title COLLATE NOCASE"
    
    order_dir = "DESC" if order == "desc" else "ASC"
    
    # Пагинация
    offset = (page - 1) * per_page
    query = f"""
        SELECT * FROM movies 
        {where_clause}
        ORDER BY {order_by} {order_dir}
        LIMIT ? OFFSET ?
    """
    
    cursor.execute(query, params + [per_page, offset])
    movies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Метаданни за пагинация
    total_pages = math.ceil(total / per_page)
    
    return {
        "items": movies,
        "meta": {
            "current_page": page,
            "per_page": per_page,
            "total_items": total,
            "total_pages": total_pages,
            "has_previous": page > 1,
            "has_next": page < total_pages,
            "previous_page": page - 1 if page > 1 else None,
            "next_page": page + 1 if page < total_pages else None
        }
    }

def get_movie_by_id(movie_id: int):
    """Връща филм по ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()
    conn.close()
    
    return dict(movie) if movie else None

def update_movie(movie_id: int, movie_update: MovieUpdate, background_tasks):
    """Обновява филм"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Провери дали съществува
    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    existing = cursor.fetchone()
    
    if not existing:
        conn.close()
        return None
    
    # Изгради UPDATE заявка
    updates = []
    params = []
    
    if movie_update.title is not None:
        updates.append("title = ?")
        params.append(movie_update.title)
    if movie_update.director is not None:
        updates.append("director = ?")
        params.append(movie_update.director)
    if movie_update.release_year is not None:
        updates.append("release_year = ?")
        params.append(movie_update.release_year)
    
    if updates:
        params.append(movie_id)
        cursor.execute(f"""
            UPDATE movies 
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)
        
        # Ако заглавието се е променило, нулирай рейтинга
        if movie_update.title and movie_update.title != existing["title"]:
            cursor.execute("""
                UPDATE movies 
                SET rating = NULL, enrichment_status = 'pending'
                WHERE id = ?
            """, (movie_id,))
            
            background_tasks.add_task(enrich_movie_rating, movie_id, movie_update.title)
    
    conn.commit()
    
    # Вземи обновения филм
    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    updated = dict(cursor.fetchone())
    conn.close()
    
    logger.info(f"Updated movie {movie_id}")
    return updated

def delete_movie(movie_id: int):
    """Изтрива филм"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM movies WHERE id = ?", (movie_id,))
    if not cursor.fetchone():
        conn.close()
        return False
    
    cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()
    
    logger.info(f"Deleted movie {movie_id}")
    return True
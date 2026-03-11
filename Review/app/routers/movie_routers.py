from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from app.models.movie import MovieCreate, MovieUpdate, MovieResponse
from app.services.movies_service import create_movie, get_movies, get_movie_by_id, update_movie, delete_movie
from app.auth.dependencies import require_admin, require_user
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()  # Това е важно - трябва да се казва router!

@router.post("/", response_model=MovieResponse)
def create_movie_endpoint(
    movie: MovieCreate,
    background_tasks: BackgroundTasks,
    current_user = Depends(require_admin)
):
    return create_movie(movie, background_tasks)

@router.get("/", response_model=dict)
def get_movies_endpoint(
    search: Optional[str] = Query(None, description="Търсене по заглавие"),
    sort: Optional[str] = Query("rating", regex="^(rating|title)$"),
    order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user = Depends(require_user)
):
    return get_movies(search, sort, order, page, per_page)

@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie_endpoint(
    movie_id: int,
    current_user = Depends(require_user)
):
    movie = get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.put("/{movie_id}", response_model=MovieResponse)
def update_movie_endpoint(
    movie_id: int,
    movie_update: MovieUpdate,
    background_tasks: BackgroundTasks,
    current_user = Depends(require_admin)
):
    movie = update_movie(movie_id, movie_update, background_tasks)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.delete("/{movie_id}")
def delete_movie_endpoint(
    movie_id: int,
    current_user = Depends(require_admin)
):
    if not delete_movie(movie_id):
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"message": "Movie deleted successfully"}
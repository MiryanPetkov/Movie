from .auth import router as auth_router
from .movie_routers import router as movies_router   # Промени тук!

__all__ = ['auth_router', 'movies_router']
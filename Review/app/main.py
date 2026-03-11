import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import auth_router, movies_router
from utils.logging_config import setup_logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
setup_logging()

# Lifespan функция - ТУК СЕ ИНИЦИАЛИЗИРА БАЗАТА!
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - изпълнява се при стартиране
    print("🚀 Стартиране на приложението...")
    init_db()  # ← КЛЮЧОВО! Създава таблиците
    print("✅ Базата данни е инициализирана")
    yield
    # Shutdown - изпълнява се при спиране
    print("🛑 Приложението спира...")

# Initialize FastAPI WITH LIFESPAN
app = FastAPI(
    title="Movie Library API",
    description="Secure Movie Library with Background Rating Aggregation",
    version="1.0.0",
    lifespan=lifespan  # ← КЛЮЧОВО! Подаваме lifespan
)

# CORS middleware - ЗАДЪЛЖИТЕЛНО за Swagger UI!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # За development - всички
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(movies_router, prefix="/movies", tags=["Movies"])

@app.get("/")
def root():
    return {"message": "Welcome to Movie Library API", "docs": "/docs"}
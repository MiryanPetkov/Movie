from fastapi import APIRouter, HTTPException, Depends
from app.models.user import UserCreate, UserLogin, TokenResponse
from app.services import user_service

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
def register(user: UserCreate):
    """Регистрация на нов потребител"""
    result = user_service.register_user(user)
    if not result:
        raise HTTPException(status_code=400, detail="Username already exists")
    return result

@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin):
    """Вход на потребител"""
    result = user_service.login_user(user_data)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return result
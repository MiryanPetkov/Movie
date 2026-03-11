from app.database import get_db
from app.models.user import UserCreate, UserLogin
from app.auth.jwt_handler import create_access_token, hash_password, verify_password
import logging

logger = logging.getLogger(__name__)

def register_user(user_data: UserCreate):
    """Регистрира нов потребител"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Провери дали съществува
    cursor.execute("SELECT * FROM users WHERE username = ?", (user_data.username,))
    if cursor.fetchone():
        conn.close()
        return None
    
    # Създай нов потребител (винаги USER роля)
    password_hash = hash_password(user_data.password)
    cursor.execute("""
        INSERT INTO users (username, password_hash, role) 
        VALUES (?, ?, ?)
    """, (user_data.username, password_hash, 'USER'))
    
    conn.commit()
    
    # Вземи новия потребител
    cursor.execute("SELECT * FROM users WHERE username = ?", (user_data.username,))
    db_user = dict(cursor.fetchone())
    conn.close()
    
    # Създай токен
    token = create_access_token({
        "sub": db_user["username"], 
        "role": db_user["role"]
    })
    
    logger.info(f"New user registered: {user_data.username}")
    
    return {
        "access_token": token,
        "user": db_user
    }

def login_user(user_data: UserLogin):
    """Вход на потребител"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (user_data.username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not verify_password(user_data.password, user["password_hash"]):
        return None
    
    # Създай токен
    token = create_access_token({
        "sub": user["username"], 
        "role": user["role"]
    })
    
    logger.info(f"User logged in: {user_data.username}")
    
    return {
        "access_token": token,
        "user": dict(user)
    }

def get_user_by_username(username: str):
    """Връща потребител по username"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None
import sqlite3
from config import settings
from auth.jwt_handler import hash_password
import os

def get_db():
    """Връща връзка с базата данни"""
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # За да връща речници
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Създава таблиците при първо стартиране"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Създаване на таблица movies
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            director TEXT NOT NULL,
            release_year INTEGER NOT NULL,
            rating DECIMAL(3,1),
            enrichment_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Създаване на таблица users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('ADMIN', 'USER')) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Създаване на таблица rating_cache (за rate limiting)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rating_cache (
            movie_title TEXT PRIMARY KEY,
            rating DECIMAL(3,1),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    
    
    # Създаване на admin потребител ако няма
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        create_default_admin(cursor)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def create_default_admin(cursor):
    """Създава admin потребител"""
    admin_user = settings.ADMIN_USERNAME
    admin_pass = settings.ADMIN_PASSWORD
    
    if admin_pass:
        # От environment variables
        password_hash = hash_password(admin_pass)
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (admin_user, password_hash, 'ADMIN')
        )
        print(f"Admin '{admin_user}' created from environment")
    elif settings.ENVIRONMENT == "development":
        # Само за development - default admin
        default_pass = "admin123"
        password_hash = hash_password(default_pass)
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", password_hash, 'ADMIN')
        )
        print("="*50)
        print(" DEFAULT ADMIN CREATED - CHANGE IN PRODUCTION!")
        print(f"Username: admin")
        print(f"Password: admin123")
        print("="*50)
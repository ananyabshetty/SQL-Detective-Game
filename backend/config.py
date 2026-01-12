"""
SQL Detective Game - Configuration Settings
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Module-level database path (for analytics imports)
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'detective_game.db')
QUERY_TIMEOUT = 5
MAX_RESULT_ROWS = 1000


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sql-detective-secret-key-2024')
    
    # Database settings
    BASE_DIR = BASE_DIR
    DATABASE_PATH = DATABASE_PATH
    
    # SQL Execution settings
    QUERY_TIMEOUT = QUERY_TIMEOUT
    MAX_RESULT_ROWS = MAX_RESULT_ROWS
    
    # Security settings
    BLOCKED_KEYWORDS = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER',
        'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC',
        'EXECUTE', 'PRAGMA', 'ATTACH', 'DETACH', 'VACUUM',
        'REINDEX', 'REPLACE', 'UPSERT'
    ]
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:5000', 'http://127.0.0.1:5000']


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


# Config selector
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


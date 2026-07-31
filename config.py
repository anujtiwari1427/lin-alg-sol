import os

class Config:
    """Base configuration settings for Linear Algebra Solver."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'linear-algebra-solver-secret-key-2026-production-v1')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'app.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    
    # Application Settings
    APP_NAME = "Linear Algebra Solver"
    APP_VERSION = "1.0.0"
    THEME_DEFAULT = "dark"

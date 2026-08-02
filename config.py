import os

class Config:
    """Base configuration settings for Linear Algebra Solver."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'linear-algebra-solver-secret-key-2026-production-v1')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database (use /tmp/app.db in serverless read-only environments like Vercel)
    if os.environ.get('VERCEL') == '1':
        DATABASE_PATH = '/tmp/app.db'
    else:
        DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'database', 'app.db'))
        
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    
    # Application Settings
    APP_NAME = "Linear Algebra Solver"
    APP_VERSION = "2.0.0"
    THEME_DEFAULT = "green"

    @classmethod
    def get_db_path(cls):
        """Return the resolved database path for use by models."""
        return cls.DATABASE_PATH

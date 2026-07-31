import sys
import os

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class VercelPathFixer:
    """WSGI middleware to normalize PATH_INFO for Vercel serverless routing."""
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        if path.startswith('/api/index.py'):
            environ['PATH_INFO'] = path[13:] or '/'
        elif path.startswith('/api/index'):
            environ['PATH_INFO'] = path[10:] or '/'
        elif path in ('/api', '/api/'):
            environ['PATH_INFO'] = '/'
        return self.app(environ, start_response)

app.wsgi_app = VercelPathFixer(app.wsgi_app)
app.config['DEBUG'] = False

from flask import Flask, render_template, jsonify
from config import Config
from database.db import init_db
from controllers.main_controller import main_bp
from controllers.matrix_controller import matrix_bp
from controllers.determinant_controller import determinant_bp
from controllers.inverse_controller import inverse_bp
from controllers.vector_controller import vector_bp
from controllers.linear_equations_controller import linear_equations_bp
from controllers.eigen_controller import eigen_bp


def create_app(config_class=Config):
    """Application factory — register all blueprints and initialize DB."""
    app = Flask(__name__, template_folder='frontend')
    app.config.from_object(config_class)

    # Propagate runtime DB path to the model layer for test isolation
    db_path = getattr(config_class, 'DATABASE_PATH', None)
    if db_path:
        from models.calculation import CalculationModel
        CalculationModel._db_path = db_path

    # Initialize SQLite schema
    init_db(db_path)

    # Register all blueprints
    for bp in (main_bp, matrix_bp, determinant_bp, inverse_bp,
               vector_bp, linear_equations_bp, eigen_bp):
        app.register_blueprint(bp)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Health-check
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'version': app.config.get('APP_VERSION', '1.0.0')}), 200

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', True))

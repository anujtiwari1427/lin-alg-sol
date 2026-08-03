from flask import Flask, render_template, jsonify, make_response, request, g
from config import Config
from database.db import get_db_connection, init_db
from controllers.main_controller import main_bp
from controllers.matrix_controller import matrix_bp
from controllers.determinant_controller import determinant_bp
from controllers.inverse_controller import inverse_bp
from controllers.vector_controller import vector_bp
from controllers.linear_equations_controller import linear_equations_bp
from controllers.eigen_controller import eigen_bp
from datetime import date


def create_app(config_class=Config):
    """Application factory — register all blueprints and initialize DB."""
    app = Flask(__name__, template_folder='frontend')
    app.config.from_object(config_class)

    # Propagate runtime DB path to the model layer for test isolation
    from models.calculation import CalculationModel
    CalculationModel._db_path = config_class.get_db_path()

    # Initialize SQLite schema
    init_db(config_class.get_db_path())

    # Register all blueprints
    for bp in (main_bp, matrix_bp, determinant_bp, inverse_bp,
               vector_bp, linear_equations_bp, eigen_bp):
        app.register_blueprint(bp)

    # ── Request-scoped DB connection via Flask g ──────────────────────
    def teardown_db(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    app.teardown_appcontext(teardown_db)

    # ── Error handlers ────────────────────────────────────────────────
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # ── Health-check ──────────────────────────────────────────────────
    @app.route('/health')
    def health_check():
        return jsonify({
            'status':  'healthy',
            'version': app.config.get('APP_VERSION', '2.0.0')
        }), 200

    # ── Weekly activity data for dashboard chart ──────────────────────
    @app.route('/api/stats/weekly')
    def weekly_stats():
        try:
            from models.calculation import CalculationModel
            counts = CalculationModel.get_weekly_counts()
        except Exception:
            counts = [0] * 7
        return jsonify({'counts': counts})

    # ── Sitemap ───────────────────────────────────────────────────────
    SITEMAP_URLS = [
        ('/',                  '1.0', 'weekly'),
        ('/dashboard',         '0.8', 'daily'),
        ('/matrix',            '0.9', 'monthly'),
        ('/determinant',       '0.9', 'monthly'),
        ('/inverse',           '0.9', 'monthly'),
        ('/vector',            '0.9', 'monthly'),
        ('/linear-equations',  '0.9', 'monthly'),
        ('/eigen',             '0.9', 'monthly'),
        ('/learning',          '0.7', 'monthly'),
    ]

    @app.route('/sitemap.xml')
    def sitemap():
        base  = request.url_root.rstrip('/')
        today = date.today().isoformat()
        urls  = '\n'.join(
            f"""  <url>\n    <loc>{base}{loc}</loc>\n    <lastmod>{today}</lastmod>"""
            f"""\n    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>"""
            for loc, pri, freq in SITEMAP_URLS
        )
        xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>'
        resp = make_response(xml)
        resp.headers['Content-Type'] = 'application/xml'
        return resp

    @app.route('/robots.txt')
    def robots():
        base = request.url_root.rstrip('/')
        txt  = f'User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n'
        return make_response(txt, 200, {'Content-Type': 'text/plain'})

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', True))

from flask import Blueprint, render_template, request, jsonify
from models.calculation import CalculationModel
from services.solver_service import BaseSolverService

main_bp = Blueprint('main', __name__)


def _dashboard_ctx():
    """Safe default context for the dashboard template."""
    try:
        recent = CalculationModel.get_recent(limit=5)
        stats  = CalculationModel.get_stats()
    except Exception:
        recent = []
        stats  = {'total_calculations': 0, 'by_module': []}
    return {'recent_history': recent, 'stats': stats, 'notice': None,
            'active_module': None, 'history': []}


@main_bp.route('/')
def landing():
    return render_template('landing.html')


@main_bp.route('/dashboard')
def dashboard():
    ctx = _dashboard_ctx()
    ctx['active_module'] = 'dashboard'
    return render_template('dashboard.html', **ctx)


@main_bp.route('/api/search')
def search():
    q = request.args.get('q', '').strip()
    results = BaseSolverService.search(q)
    return jsonify({'query': q, 'results': results, 'count': len(results)})


@main_bp.route('/history')
def history_page():
    try:
        history = CalculationModel.get_recent(limit=50)
        stats   = CalculationModel.get_stats()
    except Exception:
        history = []
        stats   = {'total_calculations': 0, 'by_module': []}
    return render_template(
        'dashboard.html',
        active_module='history', history=history,
        recent_history=history[:5], stats=stats, notice=None,
    )


@main_bp.route('/learning')
def learning_module():
    ctx = _dashboard_ctx()
    ctx.update({'active_module': 'learning',
                'notice': 'Learning Center coming in Phase 8! (Theory, Quizzes, Flashcards, Progress Tracker)'})
    return render_template('dashboard.html', **ctx)

from flask import Blueprint, render_template, request, jsonify
from models.calculation import CalculationModel
from services.solver_service import BaseSolverService

main_bp = Blueprint('main', __name__)


def _dashboard_ctx():
    """Safe default context for the dashboard template."""
    try:
        recent = CalculationModel.get_recent(limit=5)
        stats = CalculationModel.get_stats()
    except Exception:
        recent = []
        stats = {'total_calculations': 0, 'by_module': []}
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
        stats = CalculationModel.get_stats()
    except Exception:
        history = []
        stats = {'total_calculations': 0, 'by_module': []}
    return render_template(
        'dashboard.html',
        active_module='history', history=history,
        recent_history=history[:5], stats=stats, notice=None,
    )


@main_bp.route('/learning')
def learning_module():
    ctx = _dashboard_ctx()
    ctx.update({
        'active_module': 'learning',
        'notice': 'Welcome to the Linear Algebra Student Educational Center! Explore concepts, formulas, exam tips, shortcuts, and practice questions.'
    })
    return render_template('dashboard.html', **ctx)


@main_bp.route('/api/history/search')
def history_search():
    q = request.args.get('q', '').strip()
    if not q:
        items = CalculationModel.get_recent(limit=50)
    else:
        items = CalculationModel.search_history(q)
    return jsonify({'success': True, 'query': q, 'history': items, 'count': len(items)})


@main_bp.route('/api/history/toggle-favourite/<int:record_id>', methods=['POST'])
def history_toggle_favourite(record_id):
    res = CalculationModel.toggle_favourite(record_id)
    if res is None:
        return jsonify({'success': False, 'error': 'Record not found.'}), 404
    return jsonify({'success': True, 'id': record_id, 'is_favourite': res})


@main_bp.route('/api/history/delete/<int:record_id>', methods=['DELETE', 'POST'])
def history_delete_one(record_id):
    CalculationModel.delete_by_id(record_id)
    return jsonify({'success': True, 'deleted_id': record_id})


@main_bp.route('/api/history/clear', methods=['POST', 'DELETE'])
def history_clear_all():
    CalculationModel.delete_all()
    return jsonify({'success': True, 'message': 'History cleared successfully.'})
